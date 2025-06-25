# scripts/test_codex_backend.py

from codex_client import generar_codigo

if __name__ == "__main__":
    prompt = """
    # Prueba: en Django REST Framework, define un modelo llamado TestExample:
    # - campo name = CharField(max_length=100)
    # - campo created_at = DateTimeField(auto_now_add=True)
    # - campo updated_at = DateTimeField(auto_now=True)
    # Devuélvelo como un fragmento de código listo para pegar en models.py.
    """
    codigo = generar_codigo(prompt, temperatura=0.0, max_tokens=150)
    print(codigo)
