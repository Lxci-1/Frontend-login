from rest_framework import serializers
from .models import Registro

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = ['nombres_completos', 'correo', 'contraseña']
        extra_kwargs = {'contraseña': {'write_only': True}}
    
    def create(self, validated_data):
        # Extraer la contraseña del diccionario de datos validados
        password = validated_data.pop('contraseña')
        
        # Crear instancia pero no guardar todavía
        user = Registro(**validated_data)
        
        # Cifrar la contraseña y guardar
        user.set_password(password)
        user.save()
        
        return user