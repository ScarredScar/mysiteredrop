from django.contrib import admin
from .models import MediaFile

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'created_at')
    list_filter = ('created_at', 'uploaded_by')
    search_fields = ('title',)
