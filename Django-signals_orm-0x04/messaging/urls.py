from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Placeholder URLs - these would be implemented with actual views
    path('', views.message_list, name='message_list'),
    path('send/', views.send_message, name='send_message'),
    path('notifications/', views.notification_list, name='notification_list'),
]