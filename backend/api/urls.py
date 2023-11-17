from django.urls import path
from .views import get_csrf_token
from .views import AuthenticateUserView

urlpatterns = [
    path('csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('authenticate/', AuthenticateUserView.as_view(), name='authenticate_user')
]