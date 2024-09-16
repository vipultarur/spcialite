from django.urls import path
from . import views

urlpatterns = [

    # page urls
    path('',views.index,name='index'),
    path('reels/',views.reel_feed,name='reels'),
    path('search/',views.search,name='search'),
    path('messages/',views.messages,name='messages'),

    # post urls
    path('newpost/',views.NewPost,name='newpost'),
    path('post/<uuid:post_id>/',views.PostDetail,name='postdetail'),
    path('<uuid:post_id>/like', views.like, name='postlike'),
    path('<uuid:post_id>/favourite/', views.Favourite, name='favourite2'),
    path('post/update/<uuid:post_id>/', views.update_post, name='update_post'),
    path('post/delete/<uuid:post_id>/', views.delete_post, name='delete_post'),

    # tag url
    path('tag/<slug:tag_slug>', views.Tags, name='tags'),

    # notification url
    path('notification/seen/<int:notification_id>/', views.mark_notification_as_seen, name='mark_notification_as_seen'),
    
    # reel urls
    path('reel/<uuid:id>/', views.reeldetail, name='reeldetail'),
    path('<uuid:id>/reellike', views.reel_like, name='reellike'),

    path('highlight/<int:highlight_id>/', views.highlight_detail, name='highlight_detail'),
    path('newhighlight/', views.create_highlight, name='newhighlight'),


]
