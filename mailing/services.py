from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from mailing.models import Mailing, MailingAttempt
import hashlib
import json


def get_mailing_cache_key(mailing_id, client_id=None):
    """Генерация ключа кэша для рассылки"""
    if client_id:
        return f'mailing_{mailing_id}_client_{client_id}'
    return f'mailing_{mailing_id}_results'


def send_mailing(mailing):
    """
    Отправляет рассылку и создает записи о попытках с кэшированием результатов
    """
    clients = mailing.clients.all()
    successful_sends = 0
    failed_sends = 0

    # Кэшируем общий результат рассылки на 1 час
    overall_cache_key = get_mailing_cache_key(mailing.id)
    cached_overall_result = cache.get(overall_cache_key)

    if cached_overall_result:
        return cached_overall_result

    for client in clients:
        # Проверяем кэш для каждого клиента (предотвращение дублирующих отправок)
        client_cache_key = get_mailing_cache_key(mailing.id, client.id)
        client_cached_result = cache.get(client_cache_key)

        if client_cached_result:
            # Используем кэшированный результат для этого клиента
            if client_cached_result['status'] == 'success':
                successful_sends += 1
            else:
                failed_sends += 1
            continue

        try:
            # Проверяем, есть ли email у клиента
            if not client.email:
                raise ValueError("У клиента не указан email")

            # Хэш содержимого письма для проверки изменений
            content_hash = hashlib.md5(
                f"{mailing.message.subject}{mailing.message.body}".encode()
            ).hexdigest()

            # Проверяем, не отправляли ли уже такое же письмо этому клиенту
            recent_attempts = MailingAttempt.objects.filter(
                mailing=mailing,
                client=client,
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).order_by('-created_at')[:1]

            if recent_attempts and recent_attempts[0].content_hash == content_hash:
                # Пропускаем отправку, если уже отправляли такое же письмо недавно
                cache.set(client_cache_key, {'status': 'success', 'cached': True}, 3600)
                successful_sends += 1
                continue

            # Отправка письма
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )

            # Создание успешной попытки с хэшем содержимого
            attempt = MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.SUCCESS,
                server_response='Письмо успешно отправлено',
                content_hash=content_hash
            )

            # Кэшируем результат для этого клиента на 1 час
            cache.set(client_cache_key, {'status': 'success', 'attempt_id': attempt.id}, 3600)
            successful_sends += 1

        except Exception as e:
            # Создание неуспешной попытки
            attempt = MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.FAILED,
                server_response=str(e)
            )

            # Кэшируем ошибку на 15 минут (чтобы не спамить при повторных ошибках)
            cache.set(client_cache_key, {'status': 'failed', 'attempt_id': attempt.id}, 900)
            failed_sends += 1

    # Кэшируем общий результат на 1 час
    result = (successful_sends, failed_sends)
    cache.set(overall_cache_key, result, 3600)

    return result


def send_mailing_manual(mailing_id):
    """
    Функция для ручной отправки через командную строку с кэшированием
    """
    cache_key = f'mailing_manual_result_{mailing_id}'
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    try:
        mailing = Mailing.objects.get(id=mailing_id)

        # Проверяем, не отправлялась ли рассылка недавно
        recent_attempt = MailingAttempt.objects.filter(
            mailing=mailing,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=30)
        ).order_by('-created_at').first()

        if recent_attempt and recent_attempt.status == MailingAttempt.SUCCESS:
            result = f"Рассылка '{mailing.message.subject}' уже была отправлена недавно"
            cache.set(cache_key, result, 1800)  # Кэшируем на 30 минут
            return result

        successful, failed = send_mailing(mailing)
        result = f"Рассылка '{mailing.message.subject}' отправлена. Успешно: {successful}, Неудачно: {failed}"

        # Кэшируем результат на 1 час
        cache.set(cache_key, result, 3600)

        return result

    except Mailing.DoesNotExist:
        result = f"Рассылка с ID {mailing_id} не найдена"
        cache.set(cache_key, result, 300)  # Кэшируем ошибку на 5 минут
        return result


def get_mailing_stats(mailing_id):
    """
    Получение статистики рассылки с кэшированием
    """
    cache_key = f'mailing_stats_{mailing_id}'
    cached_stats = cache.get(cache_key)

    if cached_stats:
        return cached_stats

    try:
        mailing = Mailing.objects.get(id=mailing_id)
        attempts = MailingAttempt.objects.filter(mailing=mailing)

        stats = {
            'total': attempts.count(),
            'successful': attempts.filter(status=MailingAttempt.SUCCESS).count(),
            'failed': attempts.filter(status=MailingAttempt.FAILED).count(),
            'last_attempt': attempts.order_by('-created_at').first().created_at if attempts.exists() else None,
        }

        # Кэшируем статистику на 5 минут
        cache.set(cache_key, stats, 300)

        return stats

    except Mailing.DoesNotExist:
        return {'error': 'Рассылка не найдена'}
