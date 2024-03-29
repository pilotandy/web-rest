from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import JSONField
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            firstname=firstname,
            lastname=lastname,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomGroup(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        verbose_name = 'group'

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(CustomGroup, blank=True)
    data = JSONField(default=dict, blank=True)
    private = JSONField(default=dict, blank=True)
    invoices = JSONField(default=list, blank=True)
    payments = JSONField(default=list, blank=True)
    notifications = JSONField(default=dict, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    class Meta:
        verbose_name = 'user'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def is_superuser(self):
        "Is the user a member of superusers?"
        # Simplest possible answer: All admins are superusers
        return self.is_admin
