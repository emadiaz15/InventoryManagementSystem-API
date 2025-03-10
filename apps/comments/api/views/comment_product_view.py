from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema

from apps.comments.api.repositories import ProductCommentRepository
from apps.comments.api.serializers import ProductCommentSerializer

from apps.comments.docs.comment_product_view import (
    list_comments_doc, 
    create_comment_doc, 
    get_comment_by_id_doc, 
    update_comment_doc, 
    delete_comment_doc
)

# ✅ Vista para listar comentarios de un producto
@extend_schema(**list_comments_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comment_product_list_view(request, product_id=None):
    """
    Obtiene la lista de comentarios activos de un producto.
    """
    if product_id:
        comments = ProductCommentRepository.get_comments(product_id)
        serializer = ProductCommentSerializer(comments, many=True)
    else:
        return Response({"error": "Debe proporcionar 'product_id'."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Vista para crear un comentario sobre un producto
@extend_schema(**create_comment_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_product_create_view(request, product_id=None):
    """
    Crea un nuevo comentario sobre un producto.
    """
    user = request.user
    text = request.data.get('text')

    if not text:
        return Response({"error": "El comentario no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if product_id:
            comment = ProductCommentRepository.create_comment(product_id, user, text)
            serializer = ProductCommentSerializer(comment)
        else:
            return Response({"error": "Debe proporcionar 'product_id'."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_comment_by_id_doc)
@extend_schema(**update_comment_doc)
@extend_schema(**delete_comment_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_product_detail_view(request, pk):
    """
    Obtiene, actualiza o elimina un comentario específico de producto.
    """
    try:
        comment = ProductCommentRepository.get_comment_by_id(pk)
    except ObjectDoesNotExist:
        return Response({'detail': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProductCommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        ProductCommentRepository.soft_delete_comment(pk, request.user)
        return Response({'message': 'Comentario eliminado correctamente (soft delete).'}, status=status.HTTP_204_NO_CONTENT)
