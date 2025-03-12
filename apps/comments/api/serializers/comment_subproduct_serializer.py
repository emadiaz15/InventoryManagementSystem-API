from rest_framework import serializers
from .base_comment_serializer import BaseCommentSerializer
from apps.products.models import Subproduct
from apps.comments.models import SubproductComment

class SubproductCommentSerializer(BaseCommentSerializer):
    """Serializer para comentarios en subproductos."""
    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all())  # Relación con Subproducto
    modified_by = serializers.StringRelatedField(read_only=True)  # Mostrar 'username' en lugar de 'ID'

    class Meta(BaseCommentSerializer.Meta):
        model = SubproductComment
        fields = BaseCommentSerializer.Meta.fields + ['subproduct', 'modified_by']  # Agregamos 'modified_by'

    def to_representation(self, instance):
        """Ajusta la representación del objeto para asegurar valores correctos."""
        data = super().to_representation(instance)

        # Aseguramos que 'modified_by' se representa correctamente como el 'username'
        if instance.modified_by:
            data['modified_by'] = instance.modified_by.username  # Obtener el 'username'

        return data
