from crm_app.models import Notification, User
from django.db import connection
print('Notification count:', Notification.objects.count())
with connection.cursor() as cur:
    cur.execute('PRAGMA table_info(crm_app_notification)')
    cols = [r[1] for r in cur.fetchall()]
print('Columns:', cols)
print('First 3 rows:')
for n in Notification.objects.all()[:3]:
    print(n.id, n.title, n.is_read, n.created_at)
