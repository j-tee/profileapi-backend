from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'messages', views.ContactMessageViewSet, basename='contact-message')
router.register(r'replies', views.MessageReplyViewSet, basename='message-reply')

urlpatterns = [
    # Public anonymous contact form submission - NO AUTH REQUIRED!
    path('submit/', views.public_contact_submit, name='public-contact-submit'),
    # Admin endpoints - authentication required
    path('', include(router.urls)),
]
