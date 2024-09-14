from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from post.models import Post, Reel
from django.db.models.signals import post_save, post_delete
from notification.models import Notification


class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="Comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.post
    
    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.body[:90]
        sender = comment.user
        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_types=2)
        notify.save()

    def user_del_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        notify = Notification.objects.filter(post=post, sender=sender, user=post.user, notification_types=2)
        notify.delete()

class ReelComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name="reel_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.reel

    def user_comment_reel(sender, instance, *args, **kwargs):
        comment = instance
        reel = comment.reel
        text_preview = comment.body[:90]
        sender = comment.user
        notify = Notification(reel=reel, sender=sender, user=reel.user, text_preview=text_preview, notification_types=2)
        notify.save()

    def user_del_comment_reel(sender, instance, *args, **kwargs):
        comment = instance
        reel = comment.reel
        sender = comment.user
        notify = Notification.objects.filter(reel=reel, sender=sender, user=reel.user, notification_types=2)
        notify.delete()

post_save.connect(ReelComment.user_comment_reel, sender=ReelComment)
post_delete.connect(ReelComment.user_del_comment_reel, sender=ReelComment)

post_save.connect(Comments.user_comment_post, sender=Comments)
post_delete.connect(Comments.user_del_comment_post, sender=Comments)
