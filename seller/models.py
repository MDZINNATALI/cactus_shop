from django.db import models
from accounts.models import User  # যদি তোমার User এখানে থাকে

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='seller',)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username