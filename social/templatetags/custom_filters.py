from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()

@register.filter
def timesince_filter(value):
    """
    Custom filter để tính toán khoảng thời gian tương đối
    """
    now = timezone.now()
    diff = now - value
    return timesince(value) 