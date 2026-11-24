from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CurrentUserView, UserListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    path('me/', CurrentUserView.as_view(), name='api-current-user'),
    path('all/', UserListView.as_view(), name='api-users-list'),
]
