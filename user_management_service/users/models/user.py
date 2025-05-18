import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'super_admin')  # Default role for superuser
        extra_fields.setdefault('company_id', uuid.uuid4())  # Default company_id for superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    ROLE_CHOICES = [
    ('super_admin', 'Super Admin'),
    ('admin', 'Admin'),
    ('stock_manager', 'Stock Manager'),
    ('sales', 'Sales')
  ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(null=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    # role = models.ForeignKey('users.Role', on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=False)  # Example role field
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.URLField(max_length=255, default='', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_store = models.CharField(max_length=50, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-created_at'] 