from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet, basename='campaigns')
router.register(r'messages', views.CampaignMessageViewSet, basename='campaign-messages')

urlpatterns = [
    path('', include(router.urls)),
]
