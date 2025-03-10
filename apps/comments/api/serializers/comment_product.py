from rest_framework import serializers
from .base_comment_serializer import BaseCommentSerializer
from apps.products.models.product_model import Product
from apps.comments.models.comment_product_model import ProductComment

class ProductCommentSerializer(BaseCommentSerializer):
    """Serializer para comentarios en productos."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Relación con Producto

    class Meta(BaseCommentSerializer.Meta):
        model = ProductComment
        fields = BaseCommentSerializer.Meta.fields + ['product']  # Agregamos el campo product
