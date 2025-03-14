import shortuuid
from django.db import models
from account.models import User
from PIL import Image

class Post(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    VISIBILITY_CHOICES = [
        ('only_me', 'Only Me'),
        ('public', 'Public'),
        ('friends', 'Friends'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    page = models.ForeignKey('Page', on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')  # Default approved for non-group posts
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')

    def __str__(self):
        return self.content


class ImagePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/', null=False, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.content


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} likes post: {self.post.content}'



class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.post.content} - {self.content}'



class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} - {self.receiver.username} - {self.status}'

    @staticmethod
    def unfriend(user1, user2):
        # Tìm bản ghi kết bạn có trạng thái 'accepted' giữa hai người dùng
        friendship = Friendship.objects.filter(
            sender=user1, receiver=user2, status='accepted'
        ).first() or Friendship.objects.filter(
            sender=user2, receiver=user1, status='accepted'
        ).first()

        if friendship:
            friendship.delete()
            return True
        return False


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower.username} - {self.following.username}'


class Room(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_user2')

    def __str__(self):
        return f'Chat between {self.user1.username} and {self.user2.username}'

    class Meta:
        unique_together = ('user1', 'user2')  # Đảm bảo mỗi cặp user chỉ có một phòng chat

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.content}'


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=100, choices=[
        ('friend_request', 'Friend Request'),
        ('new_message', 'New Message'),
        ('friend_request_accepted', 'Friend Request Accepted'),
        ('liked_post', 'Liked Post'),
        ('commented_post', 'Commented Post'),
    ])
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_actioned = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.recipient.username} - {self.notification_type} - {self.is_read} - {self.content}'



class ReportPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='report_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    is_resolve = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - report - {self.post.id}'


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')  # Đảm bảo mỗi user chỉ like một comment một lần


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, through='GroupMember', related_name='joined_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='group_covers/', blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def can_manage_posts(self, user):
        """Check if user can manage posts (approve/reject/delete)"""
        return GroupMember.objects.filter(
            user=user,
            group=self,
            role='admin'
        ).exists()

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'group']

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class GroupJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')

    class Meta:
        unique_together = ('user', 'group')

class Page(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pages')
    admins = models.ManyToManyField(User, related_name='admin_pages', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='page_covers/', blank=True, null=True)

    def __str__(self):
        return self.name

    def is_admin(self, user):
        return self.admins.filter(id=user.id).exists()

class PageLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_likes')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')

    def __str__(self):
        return f"{self.user.username} likes {self.page.name}"

