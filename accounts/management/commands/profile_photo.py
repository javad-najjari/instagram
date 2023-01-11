import os, random
from ...models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

# crate profile photo for all users

class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]
        images = os.listdir('/home/javad/Desktop/image/')
        rand = random.sample(list(range(0, 733)), 500)
        count = len(users)
        i = 1

        for user in users:
            print(f'profile photo: {i} / {count}')
            if user.id % 10 != 0:
                directory = f'/home/javad/Desktop/image/{images[rand[i-1]]}'

                with open(directory,'rb') as f:
                        data = f.read()

                # if not user.profile_photo:
                user.profile_photo.save(images[rand[i-1]], ContentFile(data))
            i += 1

