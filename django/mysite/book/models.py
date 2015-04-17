from django.db import models
from django.contrib.auth.models import (
    UserManager, BaseUserManager, AbstractBaseUser, AbstractUser
)
from django.db import models

# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(username=username,
            password=password,
            email=email
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractUser):
    #date_of_birth = models.DateField()
    #is_active = models.BooleanField(default=True)
    #is_admin = models.BooleanField(default=False)
    own_shop = models.IntegerField(default=0)

    objects = UserManager() #MyUserManager()

    #USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['date_of_birth']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

"""
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_staff
    """

class Book(models.Model):
    bid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title
