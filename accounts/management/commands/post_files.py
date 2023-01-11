import os, random
from post.models import Post, File
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile




# create post files

class Command(BaseCommand):
    def handle(self, *args, **options):
        posts = Post.objects.all()
        posts = [post for post in posts]
        images = os.listdir('/home/javad/Desktop/image/')
        rand = random.sample(list(range(0, 733)), 733)
        counter = len(posts)
        i, x = 1, 0

        for post in posts:
            count = random.randint(1, 5)
            print(f'post file: {i} / {counter}')
            if x > 727:
                rand = random.sample(list(range(0, 733)), 733)
                x = 0

            for _ in range(count):

                # rand = random.randint(0, 733)
                directory = f'/home/javad/Desktop/image/{images[rand[x]]}'

                with open(directory, 'rb') as f:
                        data = f.read()

                file = File(post=post)
                file.page.save(images[rand[x]], ContentFile(data))
                x += 1
            i += 1

