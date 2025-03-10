from rest_framework import serializers
from .base_comment_serializer import BaseCommentSerializer
from apps.products.models import Subproduct
from apps.comments.models import SubproductComment

class SubproductCommentSerializer(BaseCommentSerializer):
    """Serializer para comentarios en subproductos."""
    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all())  # Relación con Subproducto

    class Meta(BaseCommentSerializer.Meta):
        model = SubproductComment
        fields = BaseCommentSerializer.Meta.fields + ['subproduct']  # Agregamos el campo subproduct
