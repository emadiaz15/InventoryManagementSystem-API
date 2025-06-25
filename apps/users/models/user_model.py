from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    def _create_user(self, username, email, name, last_name, password, is_staff, is_superuser, dni=None, **extra_fields):
        if not username:
            raise ValueError("El campo de usuario es obligatorio.")
        if not email:
            raise ValueError("El campo de email es obligatorio.")

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            dni=dni,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, name, last_name, password=None, dni=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return self._create_user(username, email, name, last_name, password, False, False, dni, **extra_fields)

    def create_superuser(self, username, email, name, last_name, password=None, dni=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return self._create_user(username, email, name, last_name, password, True, True, dni, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField('Correo electrónico', max_length=255, unique=True, db_index=True)
    name = models.CharField('Nombre', max_length=255)
    last_name = models.CharField('Apellido', max_length=255)
    dni = models.CharField('DNI', max_length=10, unique=True, db_index=True, null=True, blank=True)
    image = models.CharField('Ruta en S3 de imagen de perfil', max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    historical = HistoricalRecords()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.name} {self.last_name}'
