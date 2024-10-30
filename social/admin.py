from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Post)
admin.site.register(models.ImagePost)
admin.site.register(models.Comment)
admin.site.register(models.Like)
admin.site.register(models.Notification)
admin.site.register(models.Friendship)
