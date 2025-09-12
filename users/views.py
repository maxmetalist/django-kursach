from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.views.generic import ListView, UpdateView, TemplateView, CreateView
from django.urls import reverse_lazy
from .models import Profile
from .forms import UserRegisterForm, ProfileUpdateForm
from .mixins import ManagerRequiredMixin

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        # Проверка, заблокирован ли пользователь
        if hasattr(user, 'profile') and user.profile.is_blocked:
            form.add_error(None, 'Ваш аккаунт заблокирован.')
            return self.form_invalid(form)
        return super().form_valid(form)

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.profile.email_verified = True
        self.object.profile.save()
        return response

class UserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

class ProfileUpdateView(ManagerRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'users/user_block_form.html'
    success_url = reverse_lazy('users:user_list')

class UserBlockedView(TemplateView):
    template_name = 'users/user_blocked.html'

class AccessDeniedView(TemplateView):
    template_name = 'users/access_denied.html'


class ManagerListView(UserPassesTestMixin, ListView):
    """Список пользователей для управления правами менеджеров"""
    model = User
    template_name = 'users/manager_list.html'
    context_object_name = 'users'

    def test_func(self):
        # Только суперпользователи могут управлять менеджерами
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['managers_count'] = User.objects.filter(is_staff=True).count()
        context['users_count'] = User.objects.count()
        context['superusers_count'] = User.objects.filter(is_superuser=True).count()
        return context

    def post(self, request, *args, **kwargs):
        # Обработка назначения/снятия прав менеджера
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        if user_id and action:
            try:
                user = User.objects.get(id=user_id)

                # Защита от изменения прав суперпользователей всякими хитро..опыми
                if user.is_superuser:
                    messages.error(request, 'Нельзя изменять права суперпользователя')
                else:
                    if action == 'make_manager':
                        user.is_staff = True
                        messages.success(request, f'{user.username} назначен менеджером')
                    elif action == 'remove_manager':
                        user.is_staff = False
                        messages.success(request, f'{user.username} больше не менеджер')

                    user.save()

            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден')

            return self.get(request, *args, **kwargs)
