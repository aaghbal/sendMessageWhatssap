from rest_framework import serializers
from .models import MessageTemplate, SentMessage


class MessageTemplateSerializer(serializers.ModelSerializer):
    """Serializer for MessageTemplate model"""
    
    class Meta:
        model = MessageTemplate
        fields = ('id', 'name', 'message_type', 'content', 'media_url', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_media_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Media URL must be a valid HTTP/HTTPS URL")
        return value
    
    def validate(self, attrs):
        if attrs.get('message_type') == 'media' and not attrs.get('media_url'):
            raise serializers.ValidationError("Media URL is required for media message type")
        return attrs


class SentMessageSerializer(serializers.ModelSerializer):
    """Serializer for SentMessage model"""
    template_name = serializers.CharField(source='template_used.name', read_only=True)
    
    class Meta:
        model = SentMessage
        fields = (
            'id', 'recipient_phone', 'recipient_name', 'message_content', 
            'template_used', 'template_name', 'status', 'twilio_sid', 
            'error_message', 'sent_at', 'delivered_at'
        )
        read_only_fields = ('id', 'sent_at', 'delivered_at', 'twilio_sid')


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending individual messages"""
    recipient_phone = serializers.CharField(max_length=25)
    recipient_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    message_content = serializers.CharField()
    template_id = serializers.IntegerField(required=False)
    
    def validate_recipient_phone(self, value):
        # Basic phone number validation
        import re
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def validate_template_id(self, value):
        if value:
            user = self.context['request'].user
            if not MessageTemplate.objects.filter(id=value, user=user).exists():
                raise serializers.ValidationError("Template not found or doesn't belong to user")
        return value
