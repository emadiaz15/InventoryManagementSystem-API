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
    description="Retrieve a list of all active comments",
    responses={200: CommentSerializer(many=True)},
)
@extend_schema(
    methods=['POST'],
    operation_id="create_comment",
    description="Create a new comment",
    request=CommentSerializer,
    responses={
        201: CommentSerializer,
        400: "Bad Request - Invalid data",
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comment_list_create_view(request):
    """
    Endpoint para obtener una lista de comentarios activos o crear un nuevo comentario.
    """
    if request.method == 'GET':
        comments = Comment.active_objects.all()  # Solo los comentarios activos (no eliminados)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_comment",
    description="Retrieve details of a specific active comment",
    responses={200: CommentSerializer, 404: "Comment not found"},
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    operation_id="update_comment",
    description="Update a specific comment",
    request=CommentSerializer,
    responses={
        200: CommentSerializer,
        400: "Bad Request - Invalid data",
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_comment",
    description="Soft delete a specific comment",
    responses={204: "Comment soft deleted", 404: "Comment not found"},
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar un comentario específico.
    """
    try:
        comment = Comment.active_objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # Permitir actualizaciones parciales con `partial=True`
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Soft delete del comentario (asegúrate de que el método en el modelo maneje soft=True)
        comment.delete(soft=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
