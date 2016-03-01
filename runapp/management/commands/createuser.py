from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datarun import settings

class Command(BaseCommand):
    help = 'Create a user given its name, email, and password'

    def add_arguments(self, parser):
        parser.add_argument('user_name')
        parser.add_argument('user_email')
        parser.add_argument('user_password')

    def handle(self, *args, **options):
        User.objects.create_user(options['user_name'],
                                 options['user_email'],
                                 options['user_password'])
        print User.objects.all()
        print settings.DATABASES
