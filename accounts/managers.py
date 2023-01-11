from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, username, phone_number, email, password):
        if not username:
            raise ValueError('The username must be set')
        if not email:
            raise ValueError('The email must be set')
        if not phone_number:
            raise ValueError('The phone_number must be set')
        
        user = self.model(
            username=username, email=email, phone_number=phone_number
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, email, password):
        user = self.create_user(username, phone_number, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

