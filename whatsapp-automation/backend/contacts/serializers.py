from rest_framework import serializers
from .models import PhoneNumber, PhoneNumberGroup


class PhoneNumberSerializer(serializers.ModelSerializer):
    """Serializer for PhoneNumber model"""
    full_phone_number = serializers.CharField(read_only=True)
    
    class Meta:
        model = PhoneNumber
        fields = ('id', 'phone_number', 'country_code', 'full_phone_number', 'name', 'is_active', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PhoneNumberGroupSerializer(serializers.ModelSerializer):
    """Serializer for PhoneNumberGroup model"""
    phone_numbers = PhoneNumberSerializer(many=True, read_only=True)
    phone_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PhoneNumberGroup
        fields = ('id', 'name', 'description', 'phone_numbers', 'phone_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_phone_count(self, obj):
        return obj.get_phone_count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PhoneNumberGroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PhoneNumberGroup with phone numbers"""
    phone_number_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = PhoneNumberGroup
        fields = ('id', 'name', 'description', 'phone_number_ids')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        phone_number_ids = validated_data.pop('phone_number_ids', [])
        validated_data['user'] = self.context['request'].user
        group = super().create(validated_data)
        
        if phone_number_ids:
            user = self.context['request'].user
            phone_numbers = PhoneNumber.objects.filter(
                id__in=phone_number_ids,
                user=user
            )
            group.phone_numbers.set(phone_numbers)
        
        return group


class BulkPhoneNumberCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating phone numbers from CSV"""
    csv_data = serializers.CharField()
    
    def validate_csv_data(self, value):
        import csv
        import io
        
        # Parse CSV data
        csv_file = io.StringIO(value)
        reader = csv.DictReader(csv_file)
        
        required_fields = ['phone_number']
        optional_fields = ['name', 'country_code', 'notes']
        
        parsed_data = []
        for row_num, row in enumerate(reader, start=1):
            # Check for required fields
            if not all(field in row for field in required_fields):
                raise serializers.ValidationError(
                    f"Row {row_num}: Missing required fields. Required: {required_fields}"
                )
            
            # Validate phone number
            phone_number = row['phone_number'].strip()
            if not phone_number:
                raise serializers.ValidationError(f"Row {row_num}: Phone number cannot be empty")
            
            row_data = {
                'phone_number': phone_number,
                'name': row.get('name', '').strip(),
                'country_code': row.get('country_code', '+1').strip(),
                'notes': row.get('notes', '').strip(),
            }
            parsed_data.append(row_data)
        
        if not parsed_data:
            raise serializers.ValidationError("No valid data found in CSV")
        
        return parsed_data
    
    def create(self, validated_data):
        user = self.context['request'].user
        phone_numbers = []
        
        for data in validated_data['csv_data']:
            # Check if phone number already exists for this user
            full_phone = f"{data['country_code']}{data['phone_number']}"
            if not PhoneNumber.objects.filter(user=user, full_phone_number=full_phone).exists():
                phone_number = PhoneNumber(
                    user=user,
                    phone_number=data['phone_number'],
                    country_code=data['country_code'],
                    name=data['name'] or None,
                    notes=data['notes'] or None,
                )
                phone_numbers.append(phone_number)
        
        # Bulk create
        created_numbers = PhoneNumber.objects.bulk_create(phone_numbers)
        return created_numbers
