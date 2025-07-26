from django_filters import rest_framework as filters
from .models import Message

class MessageFilter(filters.FilterSet):
    sent_at = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sender = filters.CharFilter(field_name='sender__username', lookup_expr='icontains')

    class Meta:
        model = Message
        fields = ['sent_at', 'sender']