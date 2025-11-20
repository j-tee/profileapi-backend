from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profile')
router.register(r'social-links', views.SocialLinkViewSet, basename='social-link')

urlpatterns = [
    path('', include(router.urls)),
]
