from django.urls import path
from . import views

urlpatterns = [
    # status urls
    path('upload/', views.upload_status, name='newstatus'),
    path('status_view/<int:user_id>', views.user_status, name='user_status'),
    path('profile_status/<int:user_id>/', views.profile_status, name='profile_status'),
]
