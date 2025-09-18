from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'phone-numbers', views.PhoneNumberViewSet, basename='phone-numbers')
router.register(r'groups', views.PhoneNumberGroupViewSet, basename='phone-groups')

urlpatterns = [
    path('', include(router.urls)),
]
