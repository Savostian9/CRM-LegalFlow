import os
import django
from django.conf import settings
import stripe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

stripe.api_key = settings.STRIPE_SECRET_KEY

SUB_ID = 'sub_1Sbk2L1dR7VpHP6kXwrUwf4B'

print(f"Checking subscription {SUB_ID}...")

try:
    sub = stripe.Subscription.retrieve(SUB_ID, expand=['schedule'])
    print(f"Status: {sub.status}")
    print(f"Schedule raw: {sub.schedule}")
    print(f"Schedule type: {type(sub.schedule)}")
    
    schedule = sub.schedule
    if schedule:
        if isinstance(schedule, str):
            print(f"Schedule is string ID: {schedule}")
            schedule = stripe.SubscriptionSchedule.retrieve(schedule)
            print(f"Retrieved schedule object")
        
        print(f"Schedule ID: {schedule.id if hasattr(schedule, 'id') else schedule.get('id')}")
        print(f"Schedule status: {schedule.status if hasattr(schedule, 'status') else schedule.get('status')}")
        
        phases = schedule.phases if hasattr(schedule, 'phases') else schedule.get('phases', [])
        print(f"Phases count: {len(phases)}")
        
        for i, phase in enumerate(phases):
            print(f"\nPhase {i}:")
            print(f"  start_date: {phase.get('start_date') if isinstance(phase, dict) else getattr(phase, 'start_date', None)}")
            print(f"  end_date: {phase.get('end_date') if isinstance(phase, dict) else getattr(phase, 'end_date', None)}")
            items = phase.get('items') if isinstance(phase, dict) else getattr(phase, 'items', [])
            if items:
                first_item = items[0]
                price = first_item.get('price') if isinstance(first_item, dict) else getattr(first_item, 'price', None)
                print(f"  price: {price}")
    else:
        print("No schedule attached to subscription")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
