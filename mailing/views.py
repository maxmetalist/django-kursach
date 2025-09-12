from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
)
from django.urls import reverse_lazy, reverse
from mailing.models import Client, Mailing, Message
from mailing.forms import ClientForm, MessageForm, MailingForm
from mailing.services import send_mailing
from users.mixins import OwnerRequiredMixin, UserIsNotBlockedMixin, ManagerRequiredMixin, OwnerObjectMixin


class HomeView(TemplateView):
    """Контроллер главной страницы с кэшем"""
    template_name = 'mailing/home.html'

    @method_decorator(cache_page(300))  # 5 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кэшируем счетчики на 5 минут
        cache_key_total = 'total_mailings_count'
        cache_key_active = 'active_mailings_count'
        cache_key_clients = 'total_clients_count'

        def get_active_count():
            return Mailing.objects.filter(status='Запущена').count()

        context['total_mailings'] = cache.get_or_set(
            cache_key_total,
            Mailing.objects.count,
            60 * 5 # 5 минут
        )
        context['active_mailings'] = cache.get_or_set(
            cache_key_active,
            get_active_count,
            60 * 5
        )
        context['total_clients'] = cache.get_or_set(
            cache_key_clients,
            Client.objects.count,
            60 * 5
        )

        return context


# Контроллеры клиентов
class ClientListView(UserIsNotBlockedMixin, OwnerRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    @method_decorator(cache_page(300))  # 5 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        cache_key = f'client_list_{self.request.user.id}'

        def get_original_queryset():
            return super(ClientListView, self).get_queryset()

        return cache.get_or_set(
            cache_key,
            get_original_queryset,
            60 * 5  # 5 минут
        )


class ClientCreateView(UserIsNotBlockedMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'

    def form_valid(self, form):
        # Автоматически привязываем клиента к текущему пользователю
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:client_list')


class ClientUpdateView(UserIsNotBlockedMixin, OwnerObjectMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'

    def form_valid(self, form):
        # То же самое, что и в ClientCreate
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:client_list')


class ClientDeleteView(UserIsNotBlockedMixin, OwnerObjectMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('mailing:client_list')

# Контроллеры сообщений
class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
        return context


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'

    def get_success_url(self):
        return reverse_lazy('mailing:message_list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'

    def get_success_url(self):
        return reverse_lazy('mailing:message_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('mailing:message_list')


# Контроллеры рассылки с кэшем
class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    @method_decorator(cache_page(300))  # 5 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        # Кэшируем запрос на 2 минуты
        cache_key = f'mailing_list_{self.request.user.id}'

        def get_original_queryset():
            return super(MailingListView, self).get_queryset()

        return cache.get_or_set(
            cache_key,
            get_original_queryset,
            60 * 2
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кэшируем счетчики опять же по 5 минут
        cache_key_active = 'mailing_active_count'
        cache_key_created = 'mailing_created_count'
        cache_key_completed = 'mailing_completed_count'

        def get_active_count():
            return Mailing.objects.filter(status='Запущена').count()

        def get_created_count():
            return Mailing.objects.filter(status='Создана').count()

        def get_completed_count():
            return Mailing.objects.filter(status='Завершена').count()

        context['active_count'] = cache.get_or_set(
            cache_key_active,
            get_active_count,
            60 * 5
        )
        context['created_count'] = cache.get_or_set(
            cache_key_created,
            get_created_count,
            60 * 5
        )
        context['completed_count'] = cache.get_or_set(
            cache_key_completed,
            get_completed_count,
            60 * 5
        )

        return context


class MailingCreateView(UserIsNotBlockedMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_list')


class MailingUpdateView(UserIsNotBlockedMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_list')


class MailingDeleteView(UserIsNotBlockedMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_list')


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    @method_decorator(cache_page(300))  # 5 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        # Кэшируем отдельный объект
        cache_key = f'mailing_detail_{self.kwargs["pk"]}'
        mailing = cache.get(cache_key)

        if not mailing:

            def get_original_object():
                return super(MailingDetailView).get_object(queryset)
            mailing = get_original_object()
            cache.set(cache_key, mailing, 300)  # 5 минут

        return mailing


class MailingToggleView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Включение/отключение рассылки менеджером"""

    def test_func(self):
        # Только менеджеры могут использовать это представление
        return self.request.user.is_staff

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Переключаем статус активности
        mailing.is_active = not mailing.is_active
        mailing.save()

        if mailing.is_active:
            messages.success(request, f'Рассылка #{mailing.pk} включена')
        else:
            messages.success(request, f'Рассылка #{mailing.pk} отключена')

        return redirect('mailing:mailing_list')


class SendMailingManualView(View):
    """
    Ручная отправка рассылки через интерфейс
    """

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        successful, failed = send_mailing(mailing)

        messages.success(
            request,
            f"Рассылка '{mailing.message.subject}' отправлена. "
            f"Успешно: {successful}, Неудачно: {failed}"
        )

        return redirect(reverse('mailing:mailing_detail', kwargs={'pk': pk}))
