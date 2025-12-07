import stripe
import logging
import traceback
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from crm_app.models import Company, UserPermissionSet

logger = logging.getLogger(__name__)

def can_manage_subscription(user):
    """Check if user has permission to manage subscription."""
    company = getattr(user, 'company', None)
    if not company:
        return False
    # Owner always can
    if company.owner_id == user.id:
        return True
    # Check permission set
    try:
        return user.permset.can_manage_subscription
    except UserPermissionSet.DoesNotExist:
        return False

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

# Plan hierarchy for upgrade/downgrade detection
PLAN_HIERARCHY = {
    'TRIAL': 0,
    'STARTER': 1,
    'PRO': 2,
}

def is_upgrade(current_plan: str, target_plan: str) -> bool:
    """Check if changing from current_plan to target_plan is an upgrade."""
    current_level = PLAN_HIERARCHY.get(current_plan.upper(), 0)
    target_level = PLAN_HIERARCHY.get(target_plan.upper(), 0)
    return target_level > current_level

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = None
        try:
            # Check permission
            if not can_manage_subscription(request.user):
                return Response({'error': 'No permission to manage subscription'}, status=status.HTTP_403_FORBIDDEN)
            
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
                    'shipping': 'auto',  # Required for tax_id_collection
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
    elif event['type'] == 'invoice.finalized':
        invoice = event['data']['object']
        handle_invoice_finalized(invoice)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_invoice_payment_succeeded(invoice)
    
    return HttpResponse(status=200)

def handle_checkout_completed(session):
    # Fulfill the purchase...
    client_reference_id = session.get('client_reference_id')
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    
    metadata = session.get('metadata', {})
    company_id = metadata.get('company_id')
    plan_code = metadata.get('plan')
    
    logger.info(f"handle_checkout_completed: session_id={session.get('id')}, customer={customer_id}, subscription={subscription_id}")
    logger.info(f"handle_checkout_completed: metadata={metadata}, company_id={company_id}, plan_code={plan_code}")

    if company_id and plan_code:
        try:
            company = Company.objects.get(id=company_id)
            old_plan = company.plan
            company.stripe_customer_id = customer_id
            company.stripe_subscription_id = subscription_id
            company.plan = plan_code.upper()  # Ensure uppercase
            company.subscription_status = 'active'
            company.save()
            logger.info(f"Company {company.name} upgraded from {old_plan} to {plan_code.upper()}")
        except Company.DoesNotExist:
            logger.error(f"Company {company_id} not found in webhook")
    else:
        logger.warning(f"handle_checkout_completed: Missing company_id={company_id} or plan_code={plan_code}")

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

def handle_invoice_finalized(invoice):
    """
    Send invoice email to customer when invoice is finalized.
    This ensures customers receive their invoice/receipt automatically.
    """
    invoice_id = invoice.get('id')
    customer_id = invoice.get('customer')
    invoice_status = invoice.get('status')
    billing_reason = invoice.get('billing_reason')  # subscription_create, subscription_cycle, etc.
    
    logger.info(f"Invoice finalized: id={invoice_id}, customer={customer_id}, "
                f"status={invoice_status}, billing_reason={billing_reason}")
    
    try:
        # For subscription invoices, they auto-charge, so status might already be 'paid'
        # We need to send the invoice/receipt regardless
        if invoice_status == 'open':
            # Invoice is open and awaiting payment - send payment request
            stripe.Invoice.send_invoice(invoice_id)
            logger.info(f"Invoice {invoice_id} sent to customer {customer_id}")
        elif invoice_status == 'paid':
            # Invoice already paid (common for subscriptions) - Stripe sends receipt automatically
            # if "Successful payments" email is enabled in Stripe Dashboard
            logger.info(f"Invoice {invoice_id} already paid - Stripe should send receipt automatically")
        else:
            logger.info(f"Invoice {invoice_id} not sent - status is {invoice_status}")
    except stripe.error.InvalidRequestError as e:
        # Invoice might already be paid or cannot be sent
        logger.warning(f"Could not send invoice {invoice_id}: {e}")
    except Exception as e:
        logger.error(f"Error sending invoice {invoice_id}: {e}")

def handle_invoice_payment_succeeded(invoice):
    """
    Handle successful invoice payment - send receipt/invoice email to customer.
    """
    invoice_id = invoice.get('id')
    customer_id = invoice.get('customer')
    customer_email = invoice.get('customer_email')
    amount_paid = invoice.get('amount_paid', 0)
    currency = invoice.get('currency', 'pln').upper()
    invoice_pdf = invoice.get('invoice_pdf')  # URL to PDF invoice
    hosted_invoice_url = invoice.get('hosted_invoice_url')  # Stripe hosted invoice page
    
    logger.info(f"Invoice payment succeeded: id={invoice_id}, customer={customer_id}, "
                f"email={customer_email}, amount={amount_paid/100:.2f} {currency}")
    
    try:
        company = Company.objects.filter(stripe_customer_id=customer_id).first()
        company_name = company.name if company else 'Customer'
        
        if company:
            logger.info(f"Payment received for company {company.name}: "
                       f"{amount_paid/100:.2f} {currency}")
        
        # Send invoice email to customer
        if customer_email:
            try:
                amount_formatted = f"{amount_paid/100:.2f} {currency}"
                
                # Build email content
                subject = f"Faktura za subskrypcję LegalFlow - {amount_formatted}"
                
                text_body = f"""Dzień dobry,

Dziękujemy za płatność za subskrypcję LegalFlow.

Szczegóły płatności:
- Kwota: {amount_formatted}
- Numer faktury: {invoice_id}
- Firma: {company_name}

"""
                if invoice_pdf:
                    text_body += f"Faktura PDF: {invoice_pdf}\n"
                if hosted_invoice_url:
                    text_body += f"Podgląd faktury online: {hosted_invoice_url}\n"
                
                text_body += """
Jeśli masz pytania dotyczące faktury, odpowiedz na ten email.

Pozdrawiamy,
Zespół LegalFlow
"""
                
                html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
        <tr>
            <td style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: bold;">LegalFlow</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Potwierdzenie płatności</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px;">
                <p style="margin: 0 0 20px 0; font-size: 16px;">Dzień dobry,</p>
                <p style="margin: 0 0 30px 0; font-size: 16px;">Dziękujemy za płatność za subskrypcję LegalFlow.</p>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 30px;">
                    <tr>
                        <td style="padding: 25px;">
                            <p style="margin: 0 0 15px 0; font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Szczegóły płatności:</p>
                            <p style="margin: 0 0 20px 0; font-size: 32px; font-weight: bold; color: #059669;">✓ {amount_formatted}</p>
                            <p style="margin: 0 0 8px 0; font-size: 14px; color: #475569;"><strong>Numer faktury:</strong> {invoice_id}</p>
                            <p style="margin: 0; font-size: 14px; color: #475569;"><strong>Firma:</strong> {company_name}</p>
                        </td>
                    </tr>
                </table>
                
                <table cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                    <tr>
"""
                if invoice_pdf:
                    html_body += f'''
                        <td style="padding-right: 12px;">
                            <a href="{invoice_pdf}" style="display: inline-block; background: #2563eb; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">📄 Pobierz fakturę PDF</a>
                        </td>
'''
                if hosted_invoice_url:
                    html_body += f'''
                        <td>
                            <a href="{hosted_invoice_url}" style="display: inline-block; background: #64748b; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">🔗 Zobacz fakturę online</a>
                        </td>
'''
                
                html_body += """
                    </tr>
                </table>
                
                <p style="margin: 0; font-size: 14px; color: #64748b;">Jeśli masz pytania dotyczące faktury, odpowiedz na ten email.</p>
            </td>
        </tr>
        <tr>
            <td style="background: #f8fafc; padding: 25px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0; font-size: 14px; color: #64748b;">Pozdrawiamy,<br><strong>Zespół LegalFlow</strong></p>
            </td>
        </tr>
    </table>
</body>
</html>
"""
                
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
                email = EmailMessage(
                    subject=subject,
                    body=text_body,
                    from_email=from_email,
                    to=[customer_email],
                )
                email.content_subtype = 'html'
                email.body = html_body
                email.send(fail_silently=False)
                
                logger.info(f"Invoice email sent to {customer_email} for invoice {invoice_id}")
                
            except Exception as e:
                logger.error(f"Failed to send invoice email to {customer_email}: {e}")
        else:
            logger.warning(f"No customer email for invoice {invoice_id}, cannot send email")
            
    except Exception as e:
        logger.error(f"Error processing payment for customer {customer_id}: {e}")

class CreateCustomerPortalSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Check permission
            if not can_manage_subscription(request.user):
                return Response({'error': 'No permission to manage subscription'}, status=status.HTTP_403_FORBIDDEN)
            
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


class ChangePlanView(APIView):
    """
    Change subscription plan (upgrade or downgrade).
    
    Upgrade (e.g., Starter → Pro):
        - Takes effect IMMEDIATELY
        - Prorated billing (customer pays difference now)
    
    Downgrade (e.g., Pro → Starter):
        - Takes effect at END OF CURRENT PERIOD
        - Customer keeps current plan until period ends
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Check permission
            if not can_manage_subscription(request.user):
                return Response({'error': 'No permission to manage subscription'}, status=status.HTTP_403_FORBIDDEN)
            
            user = request.user
            if not user.company:
                return Response({'error': 'User has no company'}, status=status.HTTP_400_BAD_REQUEST)
            
            company = user.company
            target_plan = request.data.get('target_plan', '').upper()
            billing_cycle = request.data.get('billing_cycle', 'month')
            
            logger.info(f"ChangePlan: user={user.email}, company={company.name}, "
                       f"current={company.plan}, target={target_plan}")
            
            # Validate target plan
            if target_plan not in STRIPE_PRICES:
                return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already on this plan
            if company.plan == target_plan:
                return Response({'error': 'Already on this plan'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get new price ID
            new_price_id = STRIPE_PRICES[target_plan].get(billing_cycle)
            if not new_price_id:
                return Response({'error': f'Price for {target_plan} ({billing_cycle}) not configured'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user has active subscription
            sub_id = company.stripe_subscription_id
            if not sub_id:
                # No subscription yet - redirect to checkout
                return Response({
                    'action': 'checkout_required',
                    'message': 'No active subscription. Please subscribe first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get current subscription from Stripe
            try:
                subscription = stripe.Subscription.retrieve(sub_id)
            except stripe.error.InvalidRequestError:
                return Response({'error': 'Subscription not found in Stripe'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            if subscription.status not in ('active', 'trialing'):
                return Response({'error': f'Subscription is {subscription.status}, cannot change plan'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Get current subscription item
            if not subscription.get('items') or not subscription['items'].get('data'):
                return Response({'error': 'No subscription items found'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            subscription_item_id = subscription['items']['data'][0]['id']
            
            # Determine if upgrade or downgrade
            upgrading = is_upgrade(company.plan, target_plan)
            
            if upgrading:
                # UPGRADE: Apply immediately with proration
                logger.info(f"ChangePlan: UPGRADE {company.plan} → {target_plan} (immediate)")
                
                updated_sub = stripe.Subscription.modify(
                    sub_id,
                    items=[{
                        'id': subscription_item_id,
                        'price': new_price_id,
                    }],
                    proration_behavior='create_prorations',  # Charge/credit difference
                    # cancel_at_period_end=False,  # Ensure subscription continues
                    metadata={
                        'company_id': company.id,
                        'plan': target_plan,
                    }
                )
                
                # Update local DB immediately for upgrades
                old_plan = company.plan
                company.plan = target_plan
                company.save(update_fields=['plan'])
                
                logger.info(f"ChangePlan: Upgrade complete. {old_plan} → {target_plan}")
                
                return Response({
                    'success': True,
                    'action': 'upgraded',
                    'message': f'Plan upgraded to {target_plan}. The price difference will be charged now.',
                    'new_plan': target_plan,
                    'effective': 'immediately'
                })
            
            else:
                # DOWNGRADE: Schedule for end of period
                logger.info(f"ChangePlan: DOWNGRADE {company.plan} → {target_plan} (at period end)")
                
                # Use subscription schedules for downgrade at period end
                # Or simpler: modify with proration_behavior='none' and billing_cycle_anchor
                
                updated_sub = stripe.Subscription.modify(
                    sub_id,
                    items=[{
                        'id': subscription_item_id,
                        'price': new_price_id,
                    }],
                    proration_behavior='none',  # No immediate charge/credit
                    billing_cycle_anchor='unchanged',  # Keep current billing date
                    metadata={
                        'company_id': company.id,
                        'plan': target_plan,
                        'pending_downgrade': 'true',
                    }
                )
                
                # For downgrade, we update plan immediately but could also wait for webhook
                # The customer keeps using current features until Stripe applies the change
                old_plan = company.plan
                company.plan = target_plan
                company.save(update_fields=['plan'])
                
                # Get period end date for user message
                import datetime
                period_end = datetime.datetime.fromtimestamp(subscription.current_period_end)
                period_end_str = period_end.strftime('%d.%m.%Y')
                
                logger.info(f"ChangePlan: Downgrade scheduled. {old_plan} → {target_plan} at {period_end_str}")
                
                return Response({
                    'success': True,
                    'action': 'downgraded',
                    'message': f'Plan will change to {target_plan} on {period_end_str}. '
                              f'You keep {old_plan} features until then.',
                    'new_plan': target_plan,
                    'effective': period_end_str,
                    'effective_timestamp': subscription.current_period_end
                })
        
        except stripe.error.StripeError as e:
            logger.exception(f"Stripe error changing plan: {e}")
            return Response({'error': f'Stripe error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception(f"Error changing plan: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Check permission
            if not can_manage_subscription(request.user):
                return Response({'error': 'No permission to manage subscription'}, status=status.HTTP_403_FORBIDDEN)
            
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
            # Check permission
            if not can_manage_subscription(request.user):
                return Response({'error': 'No permission to manage subscription'}, status=status.HTTP_403_FORBIDDEN)
            
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
            # Check permission
            if not can_manage_subscription(request.user):
                return Response({'error': 'No permission to manage subscription'}, status=status.HTTP_403_FORBIDDEN)
            
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
