from apps.products.models import Product, Subproduct

def validate_and_correct_stock():
    # Recorre todos los productos
    for product in Product.objects.all():
        total_subproduct_quantity = 0
        
        # Suma las cantidades de los subproductos
        for subproduct in product.subproducts.all():
            total_subproduct_quantity += subproduct.quantity
        
        # Verifica si la cantidad total de subproductos no coincide con la del producto
        if product.quantity != total_subproduct_quantity:
            print(f"Corrigiendo stock para el producto {product.name}")
            # Actualiza la cantidad del producto para que coincida con la sumatoria de subproductos
            product.quantity = total_subproduct_quantity
            product.save()
            print(f"Stock del producto {product.name} actualizado a {product.quantity}")
            
validate_and_correct_stock()
