from django.urls import path, include
from rest_framework import routers
# from drf_nested_routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'conversations/<int:conversation_id>/messages', MessageViewSet, basename='message')

# nested_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
# nested_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    # path('', include(nested_router.urls)),
]