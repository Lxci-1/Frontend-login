from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser
from .models import Registro
from .utils import decode_jwt_token

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Obtener el token del encabezado Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
            
        try:
            # Verificar que el formato sea "Bearer <token>"
            prefix, token = auth_header.split(' ')
        except ValueError:
            # Si el encabezado no tiene el formato correcto
            return None
            
        if prefix.lower() != 'bearer':
            # Si el prefijo no es 'bearer'
            return None
            
        # Decodificar el token
        payload = decode_jwt_token(token)
        
        if not payload:
            raise exceptions.AuthenticationFailed('Token inválido o expirado')
            
        # Obtener el usuario a partir del payload
        user_id = payload.get('user_id')
        
        try:
            usuario = Registro.objects.get(id=user_id)
        except Registro.DoesNotExist:
            raise exceptions.AuthenticationFailed('Usuario no encontrado')
            
        # Devolver una tupla de (user, auth) como espera el framework
        return (usuario, None)