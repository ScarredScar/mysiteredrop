from django.db import models
from django.contrib.auth.models import User

class MediaFile(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_files')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.file.name
