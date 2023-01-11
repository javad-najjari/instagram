import random
from faker import Faker
from ...models import User
from post.models import Post
from django.core.management.base import BaseCommand


fake = Faker()


# create random posts

class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]
        users = users[101:]
        
        for i in range(200):
            x = random.randint(1, 15)
            user = random.choice(users)
            caption = fake.paragraph(nb_sentences=x)
            print(f'create post: {i+1} / 200  ->  {user}')

            Post.objects.create(
                caption = caption,
                user = user
            )

