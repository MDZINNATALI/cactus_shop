from accounts.models import User

user_id = 1
user = User.objects.get(id=user_id)

print(f"আগে: {user.username} - Approved: {user.is_approved}")

# সরাসরি approve
user.is_approved = True
user.save()

print(f"পরে: {user.username} - Approved: {user.is_approved}")
print("✅ ইউজার approved করা হয়েছে!")



from seller.models import Seller
from django.contrib.auth.models import User

for s in Seller.objects.all():
    print(s.id, s.user_id)