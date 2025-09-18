from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import PhoneNumber, PhoneNumberGroup
from .serializers import (
    PhoneNumberSerializer, 
    PhoneNumberGroupSerializer,
    PhoneNumberGroupCreateSerializer,
    BulkPhoneNumberCreateSerializer
)


class PhoneNumberViewSet(viewsets.ModelViewSet):
    """ViewSet for managing phone numbers"""
    serializer_class = PhoneNumberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = PhoneNumber.objects.filter(user=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(full_phone_number__icontains=search)
            )
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create phone numbers from CSV data"""
        serializer = BulkPhoneNumberCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        created_numbers = serializer.save()
        
        return Response({
            'message': f'Successfully created {len(created_numbers)} phone numbers',
            'created_count': len(created_numbers)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export phone numbers to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="phone_numbers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Phone Number', 'Country Code', 'Full Phone Number', 'Notes', 'Created At'])
        
        for phone in self.get_queryset():
            writer.writerow([
                phone.name or '',
                phone.phone_number,
                phone.country_code,
                phone.full_phone_number,
                phone.notes or '',
                phone.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of a phone number"""
        phone_number = self.get_object()
        phone_number.is_active = not phone_number.is_active
        phone_number.save()
        
        return Response({
            'id': phone_number.id,
            'is_active': phone_number.is_active,
            'message': f'Phone number {"activated" if phone_number.is_active else "deactivated"}'
        })


class PhoneNumberGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing phone number groups"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = PhoneNumberGroup.objects.filter(user=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PhoneNumberGroupCreateSerializer
        return PhoneNumberGroupSerializer
    
    @action(detail=True, methods=['post'])
    def add_phone_numbers(self, request, pk=None):
        """Add phone numbers to a group"""
        group = self.get_object()
        phone_number_ids = request.data.get('phone_number_ids', [])
        
        if not phone_number_ids:
            return Response({'error': 'No phone number IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get phone numbers that belong to the user
        phone_numbers = PhoneNumber.objects.filter(
            id__in=phone_number_ids,
            user=request.user
        )
        
        # Add to group
        group.phone_numbers.add(*phone_numbers)
        
        return Response({
            'message': f'Added {phone_numbers.count()} phone numbers to group',
            'group_id': group.id,
            'added_count': phone_numbers.count()
        })
    
    @action(detail=True, methods=['post'])
    def remove_phone_numbers(self, request, pk=None):
        """Remove phone numbers from a group"""
        group = self.get_object()
        phone_number_ids = request.data.get('phone_number_ids', [])
        
        if not phone_number_ids:
            return Response({'error': 'No phone number IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get phone numbers that belong to the user and are in the group
        phone_numbers = PhoneNumber.objects.filter(
            id__in=phone_number_ids,
            user=request.user,
            groups=group
        )
        
        # Remove from group
        group.phone_numbers.remove(*phone_numbers)
        
        return Response({
            'message': f'Removed {phone_numbers.count()} phone numbers from group',
            'group_id': group.id,
            'removed_count': phone_numbers.count()
        })
    
    @action(detail=True, methods=['get'])
    def phone_numbers(self, request, pk=None):
        """Get phone numbers in a group"""
        group = self.get_object()
        phone_numbers = group.phone_numbers.all()
        
        # Apply pagination
        page = self.paginate_queryset(phone_numbers)
        if page is not None:
            serializer = PhoneNumberSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PhoneNumberSerializer(phone_numbers, many=True)
        return Response(serializer.data)
