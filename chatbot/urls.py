# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('chatbot/', views.chatbot_page, name='chatbot_page'),
#     path('response/', views.chatbot_response, name='chatbot_response'),
#     path('start-new-chat/', views.start_new_chat, name='start_new_chat'),
#     path('chat-histories/', views.chat_history, name='chat_history'),  # Add this path
#     path('signup/', views.signup_page, name='signup'),
#     path('login/', views.login_page, name='login'),
#     path('logout/', views.logout_user, name='logout'),
#     path('get-conversation/<int:conversation_id>/', views.get_conversation, name='get-conversation'),
#     path('delete-conversation/<int:conversation_id>/', views.delete_conversation, name='delete-conversation'),  # Added delete path
#     path('upload-file/', views.upload_file, name='upload_file'),
#     path('profile/', views.profile_view, name='profile_settings'),
#     path('profile/update/', views.update_profile, name='update_profile'),
#     path('rename-chat/<int:chat_id>/', views.rename_chat, name='rename_chat'),

# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('response/', views.chatbot_response, name='chatbot_response'),
    path('start-new-chat/', views.start_new_chat, name='start_new_chat'),
    path('chat-histories/', views.chat_history, name='chat_history'),
    path('get-conversation/<int:conversation_id>/', views.get_conversation, name='get-conversation'),
    path('delete-conversation/<int:conversation_id>/', views.delete_conversation, name='delete-conversation'),
    path('rename-chat/<int:chat_id>/', views.rename_chat, name='rename_chat'),
    path('upload-file/', views.upload_file, name='upload_file'),
]
