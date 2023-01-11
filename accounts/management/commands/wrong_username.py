import os
from django.core.management.base import BaseCommand
from ...models import User




class Command(BaseCommand):
    def handle(self, *args, **options):

        users = User.objects.all()
        users = [user for user in users]
        counter = len(users)
        i = 1

        for user in users:
            os.system('clear')
            print(f'{i}/{counter}')
            username = user.username
            username = username.replace('.', '')
            username = username.replace(' ', '_')
            username = username.lower()
            user.username = username
            user.save()
            i += 1
