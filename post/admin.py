from django.contrib import admin
from post.models import Post, Follow, Stream,Tag,Likes,Reel,ReelLikes,ReelStream

# Register your models here.
admin.site.register([Post, Follow, Stream, Tag, Likes, Reel, ReelLikes, ReelStream])

