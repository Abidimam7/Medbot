from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_page, name='signup'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_view, name='profile_settings'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
