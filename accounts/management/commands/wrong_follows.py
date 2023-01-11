import os
from follow.models import Follow
from django.core.management.base import BaseCommand




# delete wrong follows

class Command(BaseCommand):
    def handle(self, *args, **options):
        follows = Follow.objects.all()
        follows = [follow for follow in follows]
        count = len(follows)
        i = 0
        x = 1

        for follow in follows:
            os.system('clear')
            print(f'removing follow(1/2): {x}/{count}')
            if follow.from_user == follow.to_user:
                follow.delete()
                i += 1
            x += 1

        # delete duplicate follows

        follows = Follow.objects.all()
        follows = [follow for follow in follows]
        x = 1

        for follow in follows:
            os.system('clear')
            print(f'removing follow(2/2): {x}/{count}')
            if len(Follow.objects.filter(from_user=follow.from_user, to_user=follow.to_user)) > 1:
                follow.delete()
                i += 1
            x += 1
        print(f'{i} item removed')


