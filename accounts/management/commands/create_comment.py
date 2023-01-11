import os, random
from faker import Faker
from ...models import User
from post.models import Post, Comment
from django.core.management.base import BaseCommand    


fake = Faker()


class Command(BaseCommand):
    def handle(self, *args, **options):
        posts = Post.objects.all()
        posts = [post for post in posts]

        users = User.objects.all()
        users = [user for user in users]

        counter = len(posts)
        x = 1

        for post in posts:
            count = random.randint(1, 100)

            for i in range(count):
                os.system('clear')
                print(f'{x}/{counter}:  {i+1}/{count}')
                y = random.randint(1, 7)

                Comment.objects.create(
                    user = random.choice(users),
                    post = post,
                    body = fake.paragraph(nb_sentences=y),
                )
            x += 1

