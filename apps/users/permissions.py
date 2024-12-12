from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado:
    - Métodos seguros (GET, HEAD, OPTIONS): Permitidos para todos los usuarios autenticados.
    - Métodos no seguros (POST, PUT, DELETE, PATCH): Requieren que el usuario sea staff.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsStaffOrReadAndUpdateOnly(permissions.BasePermission):
    """
    Permite a los usuarios no staff leer (GET) y actualizar (PUT).
    Solo los usuarios staff pueden crear (POST) y eliminar (DELETE).
    Todos deben estar autenticados.
    """

    def has_permission(self, request, view):
        # Requiere que el usuario esté autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # Métodos seguros (GET, HEAD, OPTIONS): lectura para todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # PUT (modificar) también permitido para usuarios no staff
        if request.method == 'PUT':
            return True

        # POST y DELETE solo para usuarios staff
        if request.method in ['POST', 'DELETE']:
            return request.user.is_staff

        # Cualquier otro método no permitido
        return False