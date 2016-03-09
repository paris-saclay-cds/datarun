from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a user given its name, email, and password'
    # Add option for superuser

    def add_arguments(self, parser):
        parser.add_argument('user_name')
        parser.add_argument('user_email')
        parser.add_argument('user_password')
        parser.add_argument('--superuser',
                            action='store_true',
                            dest='superuser',
                            default=False,
                            help='To create a superuser')

    def handle(self, *args, **options):
        user = User.objects.create_user(options['user_name'],
                                        options['user_email'],
                                        options['user_password'])
        # TODO superuser
        if options['superuser']:
            user.is_superuser = True
        user.save()
