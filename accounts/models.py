from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRole(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Customer"
    SELLER = "SELLER", "Seller"


class BookstoreUserManager(UserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")

        username = extra_fields.pop("username", None)
        role = extra_fields.get("role", UserRole.CUSTOMER)
        if role not in UserRole.values:
            raise ValueError("Role must be CUSTOMER or SELLER.")

        email = self.normalize_email(email)
        if not extra_fields.get("name"):
            extra_fields["name"] = username or email.partition("@")[0]
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.CUSTOMER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=8,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = BookstoreUserManager()

    def __str__(self):
        return self.email
