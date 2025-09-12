from django.conf import settings
from django.db import models
from django.utils import timezone

class Client(models.Model):
    """Модель клиента"""
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        null=True,  # Временно, чтобы можно было добавить поле к существующим записям
        blank=True
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Модель сообщения"""
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Модель рассылки"""
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Создана',
        verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='Сообщение'
    )
    clients = models.ManyToManyField(Client, verbose_name='Получатели')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        null=True,  # Временно
        blank=True
    )
    is_active = models.BooleanField(  # Добавляем поле для отключения менеджером
        default=True,
        verbose_name='Активна (не заблокирована менеджером)'
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f"Рассылка {self.id} - {self.status}"


class MailingAttempt(models.Model):
    """Модель попытки рассылки"""
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (SUCCESS, 'Успешно'),
        (FAILED, 'Не успешно'),
    ]

    mailing = models.ForeignKey(
        'Mailing',
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )
    attempt_time = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время попытки'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ответ почтового сервера'
    )

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка {self.mailing.id} - {self.get_status_display()} - {self.attempt_time}"
