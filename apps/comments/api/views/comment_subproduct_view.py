from rest_framework import status
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema
from apps.core.pagination import Pagination
from apps.comments.api.repositories import SubproductCommentRepository
from apps.comments.api.serializers import SubproductCommentSerializer
from apps.products.models import Subproduct

from apps.comments.docs.comment_subproduct_view import (
    list_comments_doc, 
    create_comment_doc, 
    get_comment_by_id_doc, 
    update_comment_doc, 
    delete_comment_doc
)

@extend_schema(**list_comments_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comment_subproduct_list_view(request, product_pk, subproduct_pk):
    """
    Obtiene la lista de comentarios activos de un subproducto.
    """
    if subproduct_pk:
        comments = SubproductCommentRepository.get_comments(subproduct_pk)

        # Aplicando paginación
        pagination = Pagination()  # Inicializa el paginador
        paginated_comments = pagination.paginate_queryset(comments, request)  # Paginamos los comentarios

        # Serializamos los comentarios paginados
        serializer = SubproductCommentSerializer(paginated_comments, many=True)

        # Devolvemos la respuesta paginada
        return pagination.get_paginated_response(serializer.data)

    else:
        return Response({"error": "Debe proporcionar 'subproduct_pk'."}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(**create_comment_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_subproduct_create_view(request, product_pk=None, subproduct_pk=None):
    """
    Crea un nuevo comentario sobre un subproducto.
    """
    user = request.user
    text = request.data.get('text')

    # Validación de texto vacío
    if not text:
        return Response({"error": "El comentario no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

    if subproduct_pk:
        try:
            subproduct = Subproduct.objects.get(id=subproduct_pk)  # Verifica que el subproducto exista
        except Subproduct.DoesNotExist:
            return Response({"error": "Subproducto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Crea el comentario
        comment = SubproductCommentRepository.create_comment(subproduct, user, text)
        
        # Serializamos el comentario creado
        serializer = SubproductCommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response({"error": "Debe proporcionar 'subproduct_id'."}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(**get_comment_by_id_doc)
@extend_schema(**update_comment_doc)
@extend_schema(**delete_comment_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_subproduct_detail_view(request, product_pk, subproduct_pk, pk):
    """
    Obtiene, actualiza o elimina un comentario específico de subproducto.
    """
    try:
        # Obtener el comentario por su ID
        comment = SubproductCommentRepository.get_comment_by_id(pk)
    except ObjectDoesNotExist:
        return Response({'detail': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serializamos y devolvemos el comentario
        serializer = SubproductCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        # Actualizamos el comentario
        serializer = SubproductCommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))

        if serializer.is_valid():
            # Se pasa el usuario actual para que 'modified_by' y 'modified_at' se actualicen
            serializer.save(modified_by=request.user, modified_at=timezone.now())
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Realizamos el soft delete del comentario
        try:
            SubproductCommentRepository.soft_delete_comment(pk, request.user)
            return Response({'message': 'Comentario eliminado correctamente (soft delete).'}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'detail': 'Comentario no encontrado o ya ha sido eliminado.'}, status=status.HTTP_404_NOT_FOUND)
