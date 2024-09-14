from django.urls import path
from directs import views

urlpatterns = [
    path('inbox/',views.inbox,name='inbox'),
    path('direct/<username>', views.Directs, name="directs"),
    path('send/', views.SendDirect, name="send-directs"),
    path('search/', views.UserSearch, name="searchusers"),
    path('new/<username>', views.NewConversation, name="conversation"),
]
