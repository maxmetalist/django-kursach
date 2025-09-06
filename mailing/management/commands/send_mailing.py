from django.core.management.base import BaseCommand
from mailing.services import send_mailing_manual


class Command(BaseCommand):
    help = 'Отправляет рассылку вручную через командную строку'

    def add_arguments(self, parser):
        parser.add_argument(
            'mailing_id',
            type=int,
            help='ID рассылки для отправки'
        )

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        result = send_mailing_manual(mailing_id)
        self.stdout.write(self.style.SUCCESS(result))
