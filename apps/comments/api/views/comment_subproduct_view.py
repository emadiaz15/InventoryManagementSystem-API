from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema

from apps.comments.api.repositories import SubproductCommentRepository
from apps.comments.api.serializers import SubproductCommentSerializer

from apps.comments.docs.comment_subproduct_view import (
    list_comments_doc, 
    create_comment_doc, 
    get_comment_by_id_doc, 
    update_comment_doc, 
    delete_comment_doc
)

# ✅ Vista para listar comentarios de un subproducto
@extend_schema(**list_comments_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comment_subproduct_list_view(request, subproduct_id=None):
    """
    Obtiene la lista de comentarios activos de un subproducto.
    """
    if subproduct_id:
        comments = SubproductCommentRepository.get_comments(subproduct_id)
        serializer = SubproductCommentSerializer(comments, many=True)
    else:
        return Response({"error": "Debe proporcionar 'subproduct_id'."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Vista para crear un comentario sobre un subproducto
@extend_schema(**create_comment_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_subproduct_create_view(request, subproduct_id=None):
    """
    Crea un nuevo comentario sobre un subproducto.
    """
    user = request.user
    text = request.data.get('text')

    if not text:
        return Response({"error": "El comentario no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if subproduct_id:
            comment = SubproductCommentRepository.create_comment(subproduct_id, user, text)
            serializer = SubproductCommentSerializer(comment)
        else:
            return Response({"error": "Debe proporcionar 'subproduct_id'."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_comment_by_id_doc)
@extend_schema(**update_comment_doc)
@extend_schema(**delete_comment_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_subproduct_detail_view(request, pk):
    """
    Obtiene, actualiza o elimina un comentario específico de subproducto.
    """
    try:
        comment = SubproductCommentRepository.get_comment_by_id(pk)
    except ObjectDoesNotExist:
        return Response({'detail': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubproductCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        serializer = SubproductCommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        SubproductCommentRepository.soft_delete_comment(pk, request.user)
        return Response({'message': 'Comentario eliminado correctamente (soft delete).'}, status=status.HTTP_204_NO_CONTENT)
