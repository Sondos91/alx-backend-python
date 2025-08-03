from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Main messaging URLs
    path('', views.message_list, name='message_list'),
    path('send/', views.send_message, name='send_message'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Threaded conversation URLs
    path('thread/<int:thread_id>/', views.conversation_thread, name='conversation_thread'),
    path('reply/<int:message_id>/', views.reply_to_message, name='reply_to_message'),
    
    # Account deletion URLs
    path('delete-account/', views.delete_account_confirm, name='delete_account_confirm'),
    path('delete-account/confirm/', views.delete_account, name='delete_account'),
    path('account-deleted/', views.account_deleted, name='account_deleted'),
]