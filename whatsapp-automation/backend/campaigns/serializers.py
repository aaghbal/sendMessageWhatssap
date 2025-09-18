from rest_framework import serializers
from .models import Campaign, CampaignMessage, CampaignAnalytics
from contacts.models import PhoneNumberGroup, PhoneNumber
from whatsapp_messages.models import MessageTemplate


class CampaignMessageSerializer(serializers.ModelSerializer):
    """Serializer for CampaignMessage model"""
    
    class Meta:
        model = CampaignMessage
        fields = (
            'id', 'recipient_phone', 'recipient_name', 'message_content',
            'status', 'twilio_sid', 'error_message', 'created_at', 'sent_at', 'delivered_at'
        )
        read_only_fields = ('id', 'created_at', 'sent_at', 'delivered_at', 'twilio_sid')


class CampaignAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for CampaignAnalytics model"""
    
    class Meta:
        model = CampaignAnalytics
        fields = (
            'total_recipients', 'messages_sent', 'messages_delivered', 
            'messages_read', 'messages_failed', 'delivery_rate', 'read_rate', 
            'cost_estimate', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model"""
    message_template_name = serializers.CharField(source='message_template.name', read_only=True)
    total_recipients = serializers.SerializerMethodField()
    sent_count = serializers.SerializerMethodField()
    failed_count = serializers.SerializerMethodField()
    analytics = CampaignAnalyticsSerializer(read_only=True)
    
    class Meta:
        model = Campaign
        fields = (
            'id', 'name', 'description', 'message_template', 'message_template_name',
            'target_groups', 'target_phones', 'status', 'scheduled_at',
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'total_recipients', 'sent_count', 'failed_count', 'analytics'
        )
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'started_at', 'completed_at',
            'total_recipients', 'sent_count', 'failed_count'
        )
    
    def get_total_recipients(self, obj):
        return obj.get_total_recipients()
    
    def get_sent_count(self, obj):
        return obj.get_sent_count()
    
    def get_failed_count(self, obj):
        return obj.get_failed_count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_message_template(self, value):
        user = self.context['request'].user
        if not MessageTemplate.objects.filter(id=value.id, user=user).exists():
            raise serializers.ValidationError("Template not found or doesn't belong to user")
        return value
    
    def validate_target_groups(self, value):
        user = self.context['request'].user
        for group in value:
            if not PhoneNumberGroup.objects.filter(id=group.id, user=user).exists():
                raise serializers.ValidationError(f"Group {group.id} not found or doesn't belong to user")
        return value
    
    def validate_target_phones(self, value):
        user = self.context['request'].user
        for phone in value:
            if not PhoneNumber.objects.filter(id=phone.id, user=user).exists():
                raise serializers.ValidationError(f"Phone {phone.id} not found or doesn't belong to user")
        return value


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns"""
    target_group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    target_phone_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Campaign
        fields = (
            'id', 'name', 'description', 'message_template',
            'target_group_ids', 'target_phone_ids', 'scheduled_at'
        )
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        target_group_ids = validated_data.pop('target_group_ids', [])
        target_phone_ids = validated_data.pop('target_phone_ids', [])
        
        validated_data['user'] = self.context['request'].user
        campaign = super().create(validated_data)
        
        user = self.context['request'].user
        
        # Set target groups
        if target_group_ids:
            target_groups = PhoneNumberGroup.objects.filter(
                id__in=target_group_ids,
                user=user
            )
            campaign.target_groups.set(target_groups)
        
        # Set target phones
        if target_phone_ids:
            target_phones = PhoneNumber.objects.filter(
                id__in=target_phone_ids,
                user=user
            )
            campaign.target_phones.set(target_phones)
        
        return campaign


class CampaignStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating campaign status"""
    status = serializers.ChoiceField(choices=Campaign.STATUS_CHOICES)
    
    def validate_status(self, value):
        campaign = self.instance
        current_status = campaign.status
        
        # Define valid status transitions
        valid_transitions = {
            'draft': ['scheduled', 'running'],
            'scheduled': ['running', 'cancelled'],
            'running': ['completed', 'failed', 'cancelled'],
            'completed': [],
            'failed': [],
            'cancelled': [],
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )
        
        return value
