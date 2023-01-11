import random
from ...models import User
from follow.models import Follow
from django.core.management.base import BaseCommand




# create follow

class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]

        for user in users:
            rand = random.randint(1, 100)
            try:
                new_users = random.sample(users, rand)
                print(f'Start: {user.name}({user.id}) -> {rand}')
                for new_user in new_users:
                    Follow.objects.create(from_user=user, to_user=new_user)
            except:
                print('------------ Wrong ------------')
            print('------------------- Done -------------------')

