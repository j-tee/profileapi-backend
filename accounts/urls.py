from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('my-portfolio-profile/', views.UserPortfolioProfileView.as_view(), name='user-portfolio-profile'),
    
    # MFA endpoints
    path('mfa/setup/', views.MFASetupView.as_view(), name='mfa-setup'),
    path('mfa/verify/', views.MFAVerifyView.as_view(), name='mfa-verify'),
    path('mfa/disable/', views.MFADisableView.as_view(), name='mfa-disable'),
    
    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # User activity logs
    path('activity/', views.UserActivityListView.as_view(), name='user-activity'),
    
    # User management (admin only)
    path('', include(router.urls)),
]
