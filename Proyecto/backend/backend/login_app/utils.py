import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_access_token(user_id):
    """
    Genera un token JWT para el usuario
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),  # Token expira en 1 hora
        'iat': datetime.utcnow()  # Tiempo de creación del token
    }
    
    # Crea un SECRET_KEY en settings.py si no existe
    secret_key = getattr(settings, 'SECRET_KEY', 'your-secret-key-here')
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def generate_refresh_token(user_id):
    """
    Genera un token de actualización JWT para el usuario
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expira en 7 días
        'iat': datetime.utcnow()  # Tiempo de creación del token
    }
    
    secret_key = getattr(settings, 'SECRET_KEY', 'your-secret-key-here')
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def decode_jwt_token(token):
    """
    Decodifica un token JWT y devuelve el payload
    """
    try:
        secret_key = getattr(settings, 'SECRET_KEY', 'your-secret-key-here')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.InvalidTokenError:
        # Token inválido
        return None