from django import template

register = template.Library()

@register.inclusion_tag('comments/comment_recursive.html')
def show_comment(context, comment):
    context.update({
        'comment': comment,
        'liked_comments_ids': context.get('liked_comments_ids', [])
    })
    return context
