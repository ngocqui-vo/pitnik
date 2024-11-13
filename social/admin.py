from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Post)
admin.site.register(models.ImagePost)
admin.site.register(models.Comment)
admin.site.register(models.Like)
admin.site.register(models.Notification)
admin.site.register(models.Friendship)
admin.site.register(models.Message)
admin.site.register(models.Room)
admin.site.register(models.Follow)
admin.site.register(models.ReportPost)
admin.site.register(models.Group)
admin.site.register(models.GroupMember)
admin.site.register(models.GroupJoinRequest)