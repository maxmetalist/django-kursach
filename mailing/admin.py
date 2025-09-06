from django.contrib import admin
from mailing.models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment_preview')
    list_filter = ('email',)
    search_fields = ('email', 'full_name', 'comment')
    ordering = ('email',)

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comview) > 50 else obj.comment

    comment_preview.short_description = 'Комментарий (превью)'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body_preview')
    list_filter = ('subject',)
    search_fields = ('subject', 'body')
    ordering = ('subject',)

    def body_preview(self, obj):
        return obj.body[:100] + '...' if len(obj.body) > 100 else obj.body

    body_preview.short_description = 'Тело письма (превью)'


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'message_subject', 'clients_count')
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('message__subject', 'status')
    ordering = ('-start_time',)
    filter_horizontal = ('clients',)
    readonly_fields = ('status',)

    def message_subject(self, obj):
        return obj.message.subject

    message_subject.short_description = 'Тема сообщения'

    def clients_count(self, obj):
        return obj.clients.count()

    clients_count.short_description = 'Количество клиентов'

    fieldsets = (
        ('Основная информация', {
            'fields': ('start_time', 'end_time', 'status')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Получатели', {
            'fields': ('clients',)
        }),
    )


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ['mailing', 'attempt_time', 'status', 'server_response_short']
    list_filter = ['status', 'attempt_time']
    search_fields = ['mailing__name', 'server_response']

    def server_response_short(self, obj):
        return obj.server_response[:50] + '...' if obj.server_response and len(
            obj.server_response) > 50 else obj.server_response

    server_response_short.short_description = 'Ответ сервера'
