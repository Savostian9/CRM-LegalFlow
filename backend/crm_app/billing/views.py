import stripe
import logging
import traceback
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from crm_app.models import Company

logger = logging.getLogger(__name__)

# Configure Stripe - log if key is missing
_stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
if _stripe_key:
    stripe.api_key = _stripe_key
    logger.info("Stripe API key configured successfully")
else:
    logger.error("STRIPE_SECRET_KEY is not configured!")

# Price IDs mapping
# TODO: Add Yearly Price IDs when available
STRIPE_PRICES = {
    'STARTER': {
        'month': 'price_1SVZ1G1dR7VpHP6kCJhfCmuu',
        # 'year': 'price_...' 
    },
    'PRO': {
        'month': 'price_1SVZ1l1dR7VpHP6k68MJ4qn7',
        # 'year': 'price_...'
    }
}

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = None
        try:
            # Check Stripe key at runtime
            if not stripe.api_key:
                logger.error("Stripe API key is not set!")
                return Response({'error': 'Payment system not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            user = request.user
            logger.info(f"CreateCheckoutSession: Starting for user={user.email if user else 'unknown'}")
            
            if not user.company:

                logger.warning(f"CreateCheckoutSession: User {user.email} has no company")
                return Response({'error': 'User has no company'}, status=status.HTTP_400_BAD_REQUEST)
            
            company = user.company
            logger.info(f"CreateCheckoutSession: Company={company.name}, ID={company.id}")
            
            data = request.data
            logger.info(f"CreateCheckoutSession: Raw request.data={data}")
            
            target_plan = data.get('target_plan', '').upper()
            billing_cycle = data.get('billing_cycle', 'month') # month or year

            logger.info(f"CreateCheckoutSession: User={user.email}, Target={target_plan}, Cycle={billing_cycle}")

            if target_plan not in STRIPE_PRICES:
                logger.error(f"Invalid plan: {target_plan}")
                return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)
            
            price_id = STRIPE_PRICES[target_plan].get(billing_cycle)
            logger.info(f"Selected Price ID: {price_id}")

            if not price_id:
                return Response({'error': f'Price for {target_plan} ({billing_cycle}) not configured'}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create Stripe Customer
            if not company.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=company.name,
                    metadata={
                        'company_id': company.id,
                        'company_name': company.name,
                    }
                )
                company.stripe_customer_id = customer.id
                company.save(update_fields=['stripe_customer_id'])
            
            # Create Checkout Session
            domain = settings.FRONTEND_URL # e.g. http://localhost:8080
            logger.info(f"CreateCheckoutSession: Using domain={domain} for success/cancel URLs")
            
            if not domain:
                logger.error("CreateCheckoutSession: FRONTEND_URL is not set!")
                return Response({'error': 'Server configuration error: FRONTEND_URL not set'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            checkout_session = stripe.checkout.Session.create(
                customer=company.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                tax_id_collection={
                    'enabled': True,
                },
                customer_update={
                    'address': 'auto',
                    'name': 'auto',
                },
                billing_address_collection='required',
                shipping_address_collection={
                    'allowed_countries': ['PL'],
                },
                locale='pl',
                success_url=f'{domain}/dashboard/plan?success=true&session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{domain}/dashboard/plan?canceled=true',
                metadata={
                    'company_id': company.id,
                    'plan': target_plan,
                    'cycle': billing_cycle
                },
                subscription_data={
                    'metadata': {
                        'company_id': company.id,
                        'plan': target_plan
                    }
                }
            )
            
            return Response({'id': checkout_session.id, 'url': checkout_session.url})

        except stripe.error.StripeError as e:
            logger.exception(f"Stripe API error for user={user.email if user else 'unknown'}: {e}")
            return Response({'error': f'Stripe error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"Stripe checkout error for user={user.email if user else 'unknown'}: {e}\n{tb}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@csrf_exempt
def stripe_webhook(request):
    logger.info("Webhook received")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    logger.info(f"Webhook event type: {event['type']}")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return HttpResponse(status=200)

def handle_checkout_completed(session):
    # Fulfill the purchase...
    client_reference_id = session.get('client_reference_id')
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    
    metadata = session.get('metadata', {})
    company_id = metadata.get('company_id')
    plan_code = metadata.get('plan')

    if company_id and plan_code:
        try:
            company = Company.objects.get(id=company_id)
            company.stripe_customer_id = customer_id
            company.stripe_subscription_id = subscription_id
            company.plan = plan_code
            company.subscription_status = 'active'
            company.save()
            logger.info(f"Company {company.name} upgraded to {plan_code}")
        except Company.DoesNotExist:
            logger.error(f"Company {company_id} not found in webhook")

def handle_subscription_updated(subscription):
    # Check status
    status = subscription.get('status')
    customer_id = subscription.get('customer')
    
    try:
        company = Company.objects.filter(stripe_customer_id=customer_id).first()
        if company:
            company.subscription_status = status
            # If active, ensure plan is correct (optional, usually plan is set on checkout)
            # If past_due or canceled, maybe downgrade or block?
            company.save(update_fields=['subscription_status'])
    except Exception as e:
        logger.error(f"Error updating subscription for customer {customer_id}: {e}")

def handle_subscription_deleted(subscription):
    customer_id = subscription.get('customer')
    try:
        company = Company.objects.filter(stripe_customer_id=customer_id).first()
        if company:
            company.subscription_status = 'canceled'
            # Optionally downgrade to TRIAL or FREE
            # company.plan = 'TRIAL' 
            company.save(update_fields=['subscription_status'])
            logger.info(f"Subscription canceled for company {company.name}")
    except Exception as e:
        logger.error(f"Error canceling subscription for customer {customer_id}: {e}")

class CreateCustomerPortalSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.company:
                return Response({'error': 'User has no company'}, status=status.HTTP_400_BAD_REQUEST)
            
            company = user.company
            if not company.stripe_customer_id:
                return Response({'error': 'No Stripe customer found'}, status=status.HTTP_400_BAD_REQUEST)

            domain = settings.FRONTEND_URL
            
            # Create a session for the customer portal
            session = stripe.billing_portal.Session.create(
                customer=company.stripe_customer_id,
                return_url=f'{domain}/dashboard/plan',
            )
            
            return Response({'url': session.url})

        except Exception as e:
            logger.exception("Stripe portal error")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.company:
                return Response({'error': 'User has no company'}, status=status.HTTP_400_BAD_REQUEST)
            
            company = user.company
            sub_id = company.stripe_subscription_id
            
            if not sub_id:
                return Response({'error': 'No active subscription found'}, status=status.HTTP_400_BAD_REQUEST)

            # Cancel at period end
            stripe.Subscription.modify(
                sub_id,
                cancel_at_period_end=True
            )
            
            # Update local state immediately (optional, webhook will confirm)
            company.subscription_status = 'active' # It remains active until period end, but we might want to track 'canceling'
            # Stripe doesn't have a 'canceling' status, it just has cancel_at_period_end=True.
            # We can rely on the webhook to update status eventually, or just return success.
            
            return Response({'message': 'Subscription will be canceled at the end of the billing period.'})

        except Exception as e:
            logger.exception("Error canceling subscription")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StripeConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'publicKey': settings.STRIPE_PUBLISHABLE_KEY})

class CreateSetupIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.company:
                return Response({'error': 'User has no company'}, status=status.HTTP_400_BAD_REQUEST)
            
            company = user.company
            if not company.stripe_customer_id:
                # Create customer if missing
                customer = stripe.Customer.create(
                    email=user.email,
                    name=company.name,
                    metadata={'company_id': company.id}
                )
                company.stripe_customer_id = customer.id
                company.save(update_fields=['stripe_customer_id'])

            intent = stripe.SetupIntent.create(
                customer=company.stripe_customer_id,
                payment_method_types=['card'],
            )
            
            return Response({'client_secret': intent.client_secret})
        except Exception as e:
            logger.exception("Error creating SetupIntent")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateDefaultPaymentMethodView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            company = user.company
            payment_method_id = request.data.get('payment_method_id')
            
            if not payment_method_id:
                return Response({'error': 'payment_method_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            if not company.stripe_customer_id:
                return Response({'error': 'No Stripe customer'}, status=status.HTTP_400_BAD_REQUEST)

            stripe.Customer.modify(
                company.stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            return Response({'message': 'Default payment method updated'})
        except Exception as e:
            logger.exception("Error updating default payment method")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
