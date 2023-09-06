from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(null=True, max_length=20)
    photo = models.ImageField(upload_to='users', default='default.jpeg', blank=True)
    location = models.CharField(max_length=60, default='Lagos')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="datasets", null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
  
    def __str__(self):
        return self.user.username



class Result(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    f1_score = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    anomalies_shape = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.dataset.name} by {self.user.username}"