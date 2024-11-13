from django.test import TestCase
from django.db.utils import IntegrityError  # Importamos IntegrityError
from .models import User

class UserModelTest(TestCase):

    def create_user(self, username, email, password, name, last_name, dni, is_superuser=False):
        """
        Método auxiliar para crear un usuario o superusuario.
        """
        if is_superuser:
            return User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                name=name,
                last_name=last_name,
                dni=dni
            )
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            name=name,
            last_name=last_name,
            dni=dni
        )

    def test_duplicate_username(self):
        """
        Prueba que no se pueda crear un usuario con el mismo username.
        """
        # Creamos el primer usuario
        self.create_user(
            username='duplicateuser',
            email='user1@test.com',
            password='pass1',
            name='User1',
            last_name='Duplicate',
            dni='1234567890'
        )

        # Intentamos crear un segundo usuario con el mismo username, lo cual debe fallar
        with self.assertRaises(IntegrityError):
            self.create_user(
                username='duplicateuser',  # mismo username
                email='user2@test.com',
                password='pass2',
                name='User2',
                last_name='Duplicate2',
                dni='0987654321'  # aseguramos que el DNI sea único
            )
