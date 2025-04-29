from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Registro(models.Model):
    nombres_completos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False  # Para usar tabla existente
        db_table = 'registro'
    
    def set_password(self, raw_password):
        """Cifra la contraseña antes de guardarla"""
        self.contraseña = make_password(raw_password)
        
    def check_password(self, raw_password):
        """Verifica si la contraseña ingresada coincide con la cifrada"""
        return check_password(raw_password, self.contraseña)