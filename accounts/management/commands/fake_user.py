import random, string
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import User
from .get_time import get_time


faker = Faker()
count = 1000

class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()
        self.bios = [self.fake.paragraph(nb_sentences=2) for _ in range(count)]
        self.gender = [random.choice(('Male', 'Female', 'Custom', 'None')) for _ in range(count)]
        self.date_joined = [get_time() for _ in range(count)]



    def handle(self, *args, **options):

        # create random user

        names = []
        emails = []

        while len(names) < 800:
            name = faker.name()
            if name not in names:
                names.append(faker.name())

        while len(emails) < 800:
            email = faker.email()
            if email not in emails:
                emails.append(faker.email())

        i = 0
        x = User.objects.all().count()
        while x < 500:
            try:
                print(f'create user: {x+1} / 500')
                user = User.objects.create_user(
                    username = names[i],
                    email = emails[i],
                    password = 'root',
                )
                user.name = names[i],
                user.bio = self.bios[i],
                user.gender = self.gender[i],
                user.date_joined = self.date_joined[i]
                user.save()
                x += 1
            except:
                pass

            i += 1
        
        print(('-' * 50) + 'Repair' + ('-' * 50))


        ## repair name and bio

        users = User.objects.all()
        count = users.count()
        users = [user for user in users]
        counter = 0

        for user in users:
            print(f'repair name, bio: {counter+1} / {count}')
            name = user.name
            bio = user.bio

            if len(name) > 0 and name[0] == '(':
                new_name = name[2:len(name)-3]
                new_bio = bio[2:len(bio)-3]
                user.name = new_name
                user.bio = new_bio
                user.save()

            counter += 1

