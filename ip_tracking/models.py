 from django.db import models
 from chats.models import CustomUser
 from django.conf import settings

 class RequestLog(model.Model):
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} accessed {self.path} at {self.timestamp}"