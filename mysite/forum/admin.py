from django.contrib import admin
from django.urls import path, include
from .models import Topic, Reply

admin.site.register(Topic)
admin.site.register(Reply)