from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

class OwnerRequiredMixin(LoginRequiredMixin):
    """Миксин для фильтрации queryset по владельцу (для ListView)"""
    def get_queryset(self):
        # Для ListView и DetailView: показываем только свои объекты
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerObjectMixin(LoginRequiredMixin):
    """Миксин для проверки владельца объекта (для DetailView, UpdateView, DeleteView)"""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            return redirect('users:access_denied')
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(UserPassesTestMixin):
    """Разрешает доступ только менеджерам (staff)."""
    def test_func(self):
        return self.request.user.is_staff

class UserIsNotBlockedMixin(LoginRequiredMixin):
    """Проверяет, что пользователь не заблокирован."""
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_blocked:
            return redirect('users:user_blocked')
        return super().dispatch(request, *args, **kwargs)
