from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class ActiveUser(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_suspended=False)


class Suspendeduser(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_suspended=True)


class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, first_name=None, last_name=None, password=None):
        # check that user has email and username
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, first_name=None, last_name=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50, unique=True, null=True, blank=True)
    last_name = models.CharField(max_length=50, unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    is_suspended = models.BooleanField(default=False)

    suspended_user = Suspendeduser
    objects = ActiveUser

    # fields with defaults
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


highest_qualification_choice = (
    ("PhD", "PhD"),
    ("MSc.", "MSc."),
    ("BSc.", "BSc."),
    ("HND.", "HND"),
    ("OND.", "OND"),
    ("WASSCE", "WASSCE")
)

gender = (
    ("M", "Male"),
    ("F", "Female"),
)


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(blank=True, upload_to="userprofile")
    current_city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    highest_qualification = models.CharField(max_length=20, choices=highest_qualification_choice)
    hometown = models.CharField(max_length=30, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=3, null=True, blank=True, choices=gender)
    bio = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username}"

    def full_address(self):
        return f"{self.user.username}"
