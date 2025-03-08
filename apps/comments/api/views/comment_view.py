from rest_framework import status
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from drf_spectacular.utils import extend_schema

from apps.comments.api.repositories.comment_repository import CommentRepository
from apps.comments.api.serializers.comment_serializer import CommentSerializer

from apps.comments.docs.comment_doc import (
    list_comments_doc, 
    create_comment_doc, 
    get_comment_by_id_doc, 
    update_comment_doc, 
    delete_comment_doc
)


# Vista para listar los comentarios de un producto o subproducto
@extend_schema(**list_comments_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comment_list_view(request, product_id, subproduct_id=None):
    """
    Endpoint para obtener una lista de comentarios activos de un producto o subproducto.
    """
    if not product_id and not subproduct_id:
        return Response({"error": "Either 'product_id' or 'subproduct_id' must be provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Determinar el tipo de contenido (product o subproduct)
    content_type = 'subproduct' if subproduct_id else 'product'
    object_id = subproduct_id if subproduct_id else product_id

    try:
        # Obtener los comentarios desde el repositorio
        comments = CommentRepository.get_comments(content_type, object_id)
        # Serializar los comentarios
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Vista para crear un comentario sobre un producto o subproducto
@extend_schema(**create_comment_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create_view(request, product_id, subproduct_id=None):
    """
    Endpoint para crear un nuevo comentario sobre un producto o subproducto.
    """
    # Determinar el tipo de contenido (product o subproduct)
    content_type = 'subproduct' if subproduct_id else 'product'
    object_id = subproduct_id if subproduct_id else product_id
    text = request.data.get('text')
    user = request.user  # Usuario autenticado

      # Validación del texto
    if not text:
        return Response({"error": "The comment text cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Usamos el repositorio para crear el comentario
        comment = CommentRepository.create_comment(content_type, object_id, user, text)
        # Serializamos el comentario creado
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Vista para obtener, actualizar y eliminar un comentario específico
@extend_schema(**get_comment_by_id_doc)
@extend_schema(**update_comment_doc)
@extend_schema(**delete_comment_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar suavemente un comentario específico.
    """
    try:
        comment = CommentRepository.get_comment_by_id(pk)
    except ObjectDoesNotExist:
        return Response({'detail': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serializa y devuelve los datos del comentario
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        # Permite actualizaciones completas o parciales
        serializer = CommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()  # Guarda los cambios en el comentario
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Realiza el soft delete a través del método delete() del repositorio
        user = request.user
        CommentRepository.soft_delete_comment(pk, user)
        return Response({'message': 'Comment set to inactive successfully (soft delete).'}, status=status.HTTP_204_NO_CONTENT)
