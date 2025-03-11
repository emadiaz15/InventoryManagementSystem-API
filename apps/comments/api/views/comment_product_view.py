from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema
from django.utils import timezone

from apps.core.pagination import Pagination
from apps.products.models import Product
from apps.comments.api.repositories import ProductCommentRepository
from apps.comments.api.serializers import ProductCommentSerializer

from apps.comments.docs.comment_product_view import (
    list_comments_doc, 
    create_comment_doc, 
    get_comment_by_id_doc, 
    update_comment_doc, 
    delete_comment_doc
)

@extend_schema(**list_comments_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comment_product_list_view(request, product_pk=None):
    """
    Obtiene la lista de comentarios activos de un producto.
    """
    if product_pk:
        comments = ProductCommentRepository.get_comments(product_pk)
        pagination = Pagination() 
        paginated_comments = pagination.paginate_queryset(comments, request)
        serializer = ProductCommentSerializer(paginated_comments, many=True)
        return pagination.get_paginated_response(serializer.data)
    else:
        return Response({"error": "Debe proporcionar 'product_pk'."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**create_comment_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_product_create_view(request, product_pk):
    """
    Crea un nuevo comentario sobre un producto.
    """
    user = request.user
    text = request.data.get('text')

    if not text:
        return Response({"error": "El comentario no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Obtener el producto usando 'product_pk' como argumento
        product = Product.objects.get(pk=product_pk)

        # Crear el comentario asociado al producto
        comment = ProductCommentRepository.create_comment(product, user, text)
        serializer = ProductCommentSerializer(comment)

        # Responder con el comentario creado
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Product.DoesNotExist:
        # Si el producto no se encuentra, enviar error 404
        return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        # Manejar otros errores
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(**get_comment_by_id_doc)
@extend_schema(**update_comment_doc)
@extend_schema(**delete_comment_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_product_detail_view(request, product_pk, pk):
    """
    Obtiene, actualiza o elimina un comentario específico de producto.
    """
    try:
        # Obtener el comentario por su ID
        comment = ProductCommentRepository.get_comment_by_id(pk)
    except ObjectDoesNotExist:
        return Response({'detail': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serializamos y devolvemos el comentario
        serializer = ProductCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        # Actualizamos el comentario
        serializer = ProductCommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))

        if serializer.is_valid():
            # Se pasa el usuario actual para que 'modified_by' y 'modified_at' se actualicen
            serializer.save(modified_by=request.user, modified_at=timezone.now())
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Realizamos el soft delete del comentario
        try:
            ProductCommentRepository.soft_delete_comment(pk, request.user)
            return Response({'message': 'Comentario eliminado correctamente (soft delete).'}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'detail': 'Comentario no encontrado o ya ha sido eliminado.'}, status=status.HTTP_404_NOT_FOUND)