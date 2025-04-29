from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .utils import decode_jwt_token
from .models import Registro

class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware para procesar tokens JWT en endpoints protegidos
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Rutas públicas que no requieren autenticación
        public_paths = ['/api/login/', '/api/register/', '/api/refresh/']
        
        # Si es una ruta pública, permitir el acceso
        if request.path_info in public_paths:
            return None
            
        # Obtener el token del encabezado Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'No autorizado'}, status=401)
            
        # Extraer el token
        token = auth_header.split(' ')[1]
        
        # Decodificar el token
        payload = decode_jwt_token(token)
        
        if not payload:
            return JsonResponse({'error': 'Token inválido o expirado'}, status=401)
            
        # Obtener el usuario a partir del ID en el token
        user_id = payload.get('user_id')
        
        try:
            usuario = Registro.objects.get(id=user_id)
            # Guardar el usuario en request para uso posterior
            request.user = usuario
            return None
        except Registro.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=401)