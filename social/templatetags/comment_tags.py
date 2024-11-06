from django import template

register = template.Library()

@register.inclusion_tag('comments/comment_recursive.html')
def show_comment(comment):
    return {'comment': comment}
