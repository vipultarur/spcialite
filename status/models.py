from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statuses')
    media = models.FileField(upload_to='status_media/', help_text="Upload image or video")
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(hours=24))

    def __str__(self):
        return f"Status by {self.user.username}"

    def is_active(self):
        return timezone.now() < self.expires_at

class Highlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    title = models.CharField(max_length=100)
    cover = models.ImageField(upload_to=user_directory_path, verbose_name="cover")
    statuses = models.ManyToManyField(Status, related_name='highlights')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s highlight: {self.title}"

