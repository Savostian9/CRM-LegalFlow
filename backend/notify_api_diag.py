import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
django.setup()
from rest_framework.test import APIClient
from crm_app.models import User
from django.contrib.auth import get_user_model
User=get_user_model()
user=User.objects.first()
client=APIClient()
try:
    from rest_framework.authtoken.models import Token
    token,_=Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token '+token.key)
    print('Using token', token.key[:8]+'...')
except Exception as e:
    print('Token auth unavailable', e)
resp=client.get('/api/notifications/?limit=5')
print('List status', resp.status_code)
print('Payload keys', list(resp.data.keys()) if hasattr(resp,'data') else None)
items=resp.data.get('items') if hasattr(resp,'data') else []
if items:
    first=items[0]
    print('First item id', first['id'],'is_read', first['is_read'])
    r2=client.post(f"/api/notifications/mark-read/{first['id']}/")
    print('Mark read status', r2.status_code, getattr(r2,'data',None))
    r3=client.get('/api/notifications/unread-count/')
    print('Unread count', r3.status_code, getattr(r3,'data',None))
else:
    print('No items returned')
