from django.db import models
from accounts.models import User  # তোমার User যেই app এ আছে সেই অনুযায়ী ঠিক করো

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username