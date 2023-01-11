import os, random
from ...models import User
from post.models import Post, PostLike
from django.core.management.base import BaseCommand




class Command(BaseCommand):
    def handle(self, *args, **options):
        posts = Post.objects.all()
        posts = [post for post in posts]

        users = User.objects.all()
        users = [user for user in users]

        counter = len(posts)
        i = 1

        for post in posts:
            rand = random.randint(1, 150)
            new_users = random.sample(users, rand)

            x = 1
            for user in new_users:
                os.system('clear')
                print(f'{i}/{counter}: {x}/{rand}')

                PostLike.objects.create(
                    user = user,
                    post = post
                )
                x += 1
            i += 1
        
        likes = PostLike.objects.all()
        likes = [like for like in likes]
        i = 0

        for like in likes:
            if len(PostLike.objects.filter(user=like.user, post=like.post)) > 1:
                like.delete()
                i += 1
        
        print(f'{i} likes removed')

