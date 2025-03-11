from rest_framework import serializers
from .base_comment_serializer import BaseCommentSerializer
from apps.products.models.product_model import Product
from apps.comments.models.comment_product_model import ProductComment

class ProductCommentSerializer(BaseCommentSerializer):
    """Serializer para comentarios en productos."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Relación con Producto
    modified_by = serializers.StringRelatedField(read_only=True)  # Mostrar 'username' en lugar de 'ID'

    class Meta(BaseCommentSerializer.Meta):
        model = ProductComment
        fields = BaseCommentSerializer.Meta.fields + ['product', 'modified_by']  # Agregamos 'modified_by'

    def to_representation(self, instance):
        """Ajusta la representación del objeto para asegurar valores correctos."""
        data = super().to_representation(instance)
        # Aseguramos que 'modified_by' se representa correctamente como el nombre de usuario
        if instance.modified_by:
            data['modified_by'] = instance.modified_by.username  # Obtener el 'username'
        return data