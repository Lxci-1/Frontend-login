from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Registro
from .serializers import RegistroSerializer
from .utils import generate_access_token, generate_refresh_token
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Serializers adicionales para documentación
class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Correo electrónico del usuario")
    password = serializers.CharField(help_text="Contraseña del usuario")

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Token de actualización JWT")

@swagger_auto_schema(
    method='post',
    request_body=RegistroSerializer,
    responses={
        201: openapi.Response(
            description="Usuario registrado exitosamente",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: "Datos de registro inválidos"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def registro_usuario(request):
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        return Response({'mensaje': 'Usuario registrado exitosamente'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=LoginRequestSerializer,
    responses={
        200: openapi.Response(
            description="Login exitoso",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING),
                    'usuario': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'nombres': openapi.Schema(type=openapi.TYPE_STRING),
                            'correo': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING),
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        401: "Credenciales inválidas"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    correo = request.data.get('username', '')
    contraseña = request.data.get('password', '')
    
    try:
        # Buscar usuario por correo
        usuario = Registro.objects.get(correo=correo)
        
        # Verificar contraseña
        if usuario.check_password(contraseña):
            # Generar tokens JWT
            access_token = generate_access_token(usuario.id)
            refresh_token = generate_refresh_token(usuario.id)
            
            return Response({
                'mensaje': 'Login exitoso',
                'usuario': {
                    'id': usuario.id,
                    'nombres': usuario.nombres_completos,
                    'correo': usuario.correo
                },
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)
        
    except Registro.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='post',
    request_body=RefreshTokenSerializer,
    responses={
        200: openapi.Response(
            description="Token actualizado exitosamente",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: "Token de actualización no proporcionado",
        401: "Token inválido o expirado"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Endpoint para renovar el token de acceso usando el token de actualización
    """
    refresh_token = request.data.get('refresh', '')
    
    if not refresh_token:
        return Response({'error': 'Se requiere token de actualización'}, status=status.HTTP_400_BAD_REQUEST)
    
    from .utils import decode_jwt_token
    
    # Decodificar el token de actualización
    payload = decode_jwt_token(refresh_token)
    
    if not payload:
        return Response({'error': 'Token inválido o expirado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Obtener ID de usuario del payload
    user_id = payload.get('user_id')
    
    try:
        # Verificar que el usuario existe
        usuario = Registro.objects.get(id=user_id)
        
        # Generar nuevo token de acceso
        access_token = generate_access_token(usuario.id)
        
        return Response({
            'access': access_token
        }, status=status.HTTP_200_OK)
    
    except Registro.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="Perfil del usuario",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'nombres': openapi.Schema(type=openapi.TYPE_STRING),
                    'correo': openapi.Schema(type=openapi.TYPE_STRING),
                    'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                }
            )
        ),
        404: "Usuario no encontrado"
    },
    security=[{'Bearer': []}]  # Indica que requiere autenticación JWT
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_perfil(request):
    """
    Endpoint protegido que requiere autenticación JWT
    """
    usuario = request.user
    
    try:
        registro = Registro.objects.get(id=usuario.id)
        return Response({
            'id': registro.id,
            'nombres': registro.nombres_completos,
            'correo': registro.correo,
            'fecha_registro': registro.fecha_registro
        }, status=status.HTTP_200_OK)
    except Registro.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)