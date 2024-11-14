# Este archivo define las vistas para manejar los comentarios, incluyendo listar, crear, obtener, actualizar y eliminar de manera suave los comentarios activos.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.comments.models import Comment
from apps.comments.api.serializers import CommentSerializer
from drf_spectacular.utils import extend_schema
from django.utils.timezone import now

@extend_schema(
    methods=['GET'],
    operation_id="list_comments",
    description="Recupera una lista de todos los comentarios activos",
    responses={200: CommentSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comment_list_view(request):
    """
    Endpoint para obtener una lista de comentarios activos.
    """
    # Recupera solo los comentarios activos (no eliminados)
    comments = Comment.active_objects.all()
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    methods=['POST'],
    operation_id="create_comment",
    description="Crea un nuevo comentario",
    request=CommentSerializer,
    responses={
        201: CommentSerializer,
        400: "Solicitud incorrecta - Datos inválidos",
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create_view(request):
    """
    Endpoint para crear un nuevo comentario.
    """
    # Crea un nuevo comentario asociado al usuario autenticado
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Asigna el usuario que crea el comentario
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Devuelve errores de validación en caso de datos incorrectos
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_comment",
    description="Recupera los detalles de un comentario activo específico",
    responses={200: CommentSerializer, 404: "Comentario no encontrado"},
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    operation_id="update_comment",
    description="Actualiza un comentario específico",
    request=CommentSerializer,
    responses={
        200: CommentSerializer,
        400: "Solicitud incorrecta - Datos inválidos",
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_comment",
    description="Elimina suavemente un comentario específico",
    responses={204: "Comentario eliminado correctamente (soft delete)", 404: "Comentario no encontrado"},
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar suavemente un comentario específico.
    """
    try:
        # Recupera el comentario activo por su clave primaria (pk)
        comment = Comment.active_objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response({'detail': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serializa y devuelve los datos del comentario
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        # Permite actualizaciones completas o parciales con `partial=True`
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Guarda los cambios en el comentario
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Devuelve errores de validación en caso de datos incorrectos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Realiza un soft delete del comentario estableciendo `deleted_at` en la fecha y hora actuales
        comment.deleted_at = now()
        comment.save(update_fields=['deleted_at'])  # Actualiza solo el campo `deleted_at`
        return Response({'message': 'Comentario eliminado correctamente (soft delete)'}, status=status.HTTP_204_NO_CONTENT)
