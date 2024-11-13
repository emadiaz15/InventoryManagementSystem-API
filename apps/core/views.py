from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from drf_spectacular.utils import extend_schema

@extend_schema(
    operation_id="public_home_view",
    description="Public Home page for unauthenticated users",
    responses={200: {"message": "Welcome to the public Home page!"}},
)
@api_view(['GET'])
def public_home_view(request):
    """
    Vista pública para el Home de la aplicación.
    Accesible sin autenticación.
    """
    return Response({"message": "Welcome to the public Home page!"})


@extend_schema(
    operation_id="dashboard_view",
    description="Dashboard for authenticated users",
    responses={200: {"message": "Welcome to the Dashboard!"}},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """
    Vista del Dashboard de la aplicación.
    Solo accesible para usuarios autenticados.
    """
    return Response({"message": "Welcome to the Dashboard!"})
