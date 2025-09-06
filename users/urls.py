from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from users.views import ManagerListView, UserRegisterView, UserBlockedView, AccessDeniedView, ProfileUpdateView, \
    CustomLoginView

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/blocked/', UserBlockedView.as_view(), name='user_blocked'),
    path('access-denied/', AccessDeniedView.as_view(), name='access_denied'),

# URL для менеджеров
    path('', views.UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/block/', ProfileUpdateView.as_view(), name='user_block'),

# URL для супера
    path('managers/', ManagerListView.as_view(), name='manager_list'),
]