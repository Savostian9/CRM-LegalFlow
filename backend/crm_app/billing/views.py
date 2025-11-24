import stripe
import logging
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

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
        try:
            user = request.user
            if not user.company:
                return Response({'error': 'User has no company'}, status=status.HTTP_400_BAD_REQUEST)
            
            company = user.company
            data = request.data
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

        except Exception as e:
            logger.exception("Stripe checkout error")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

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
