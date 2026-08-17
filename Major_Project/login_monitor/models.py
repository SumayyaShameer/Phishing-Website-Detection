from django.db import models
from django.contrib.auth.models import User


class LoginActivity(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    username_attempted = models.CharField(max_length=150)

    login_time = models.DateTimeField(auto_now_add=True)

    login_hour = models.IntegerField()

    day_of_week = models.IntegerField()

    login_status = models.CharField(max_length=20)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    login_frequency = models.IntegerField(default=1)

    prediction = models.CharField(
        max_length=20,
        default='Normal'
    )

    def __str__(self):
        return f"{self.username_attempted} - {self.prediction}"