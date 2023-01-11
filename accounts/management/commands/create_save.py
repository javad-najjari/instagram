import os, random
from ...models import User
from post.models import Post, PostSave
from django.core.management.base import BaseCommand




class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]

        posts = Post.objects.all()
        posts = [post for post in posts]

        counter = len(users)
        i = 1
        
        for user in users:
            rand = random.randint(1, 10)
            new_posts = random.sample(posts, rand)
            os.system('clear')
            print(f'{i}/{counter}: {rand} saves ...')

            for post in new_posts:
                PostSave.objects.create(
                    user = user,
                    post = post
                )
            i += 1

