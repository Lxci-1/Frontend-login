<template>
  <div id="app">
    <div class="background-container">
      <div class="form-container">
        <h1>{{ isLogin ? 'Iniciar sesión' : 'Crear cuenta' }}</h1>
        
        <form @submit.prevent="handleSubmit">
          <!-- Formulario de Login -->
          <div v-if="isLogin">
            <div class="input-group">
              <label for="username">Usuario</label>
              <input type="text" id="username" v-model="loginForm.username" placeholder="Ingrese su usuario">
            </div>
            
            <div class="input-group">
              <label for="password">Contraseña</label>
              <input type="password" id="password" v-model="loginForm.password" placeholder="Ingrese su contraseña">
            </div>
            
            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? 'Procesando...' : 'Iniciar sesión' }}
            </button>
            <p class="switch-link" @click="isLogin = false">¿No tienes cuenta? Regístrate</p>
          </div>
          
          <!-- Formulario de Registro -->
          <div v-else>
            <div class="input-group">
              <label for="fullname">Nombres completos</label>
              <input type="text" id="fullname" v-model="registerForm.nombres_completos" placeholder="Ingrese su nombre completo">
            </div>
            
            <div class="input-group">
              <label for="email">Correo</label>
              <input type="email" id="email" v-model="registerForm.correo" placeholder="Ingrese su correo">
            </div>
            
            <div class="input-group">
              <label for="password">Contraseña</label>
              <input type="password" id="password" v-model="registerForm.contraseña" placeholder="Cree una contraseña">
            </div>
            
            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? 'Procesando...' : 'Registrarme' }}
            </button>
            <p class="switch-link" @click="isLogin = true">¿Ya tienes cuenta? Inicia sesión</p>
          </div>
        </form>
        
        <!-- Mensaje de respuesta -->
        <div v-if="message" class="message" :class="{ 'error': isError }">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      isLogin: true, // Mostrar login por defecto
      isSubmitting: false,
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        nombres_completos: '',
        correo: '',
        contraseña: ''
      },
      message: '',
      isError: false
    }
  },
  methods: {
    async handleSubmit() {
      try {
        this.message = '';
        this.isSubmitting = true;
        
        if (this.isLogin) {
          // Login con manejo JWT
          const response = await axios.post('http://localhost:8000/api/login/', this.loginForm);
          
          // Manejar tokens JWT recibidos
          if (response.data.access_token) {
            this.storeTokens(response.data.access_token, response.data.refresh_token);
            
            // Configurar axios para futuras peticiones
            this.setAuthHeader(response.data.access_token);
            
            this.message = response.data.mensaje || '¡Inicio de sesión exitoso!';
            this.isError = false;
            
            // Redirigir al usuario (puedes usar vue-router)
            setTimeout(() => {
              // Si usas vue-router: this.$router.push('/dashboard');
              // Si no, puedes redirigir así:
              // window.location.href = '/dashboard';
              console.log('Redirigiendo al dashboard...');
            }, 1500);
          } else {
            this.message = response.data.mensaje || 'Inicio de sesión exitoso, pero no se recibieron tokens.';
            this.isError = false;
          }
        } else {
          // Registro
          const response = await axios.post('http://localhost:8000/api/register/', this.registerForm);
          this.message = response.data.mensaje || 'Registro exitoso.';
          this.isError = false;
          
          // Limpiar formulario
          this.registerForm = { nombres_completos: '', correo: '', contraseña: '' };
          
          // Opcional: cambiar a login automáticamente después del registro
          setTimeout(() => {
            this.isLogin = true;
          }, 2000);
        }
      } catch (error) {
        this.isError = true;
        if (error.response) {
          this.message = error.response.data.error || 'Ocurrió un error';
        } else {
          this.message = 'Error de conexión al servidor';
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    
    // Métodos para manejo de JWT
    storeTokens(accessToken, refreshToken) {
      localStorage.setItem('access_token', accessToken);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
    },
    
    setAuthHeader(token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },
    
    async refreshToken() {
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No hay token de actualización disponible');
        }
        
        const response = await axios.post('http://localhost:8000/api/refresh/', {
          refresh_token: refreshToken
        });
        
        if (response.data.access_token) {
          this.storeTokens(response.data.access_token, response.data.refresh_token);
          this.setAuthHeader(response.data.access_token);
          return response.data.access_token;
        } else {
          throw new Error('No se recibió un nuevo token de acceso');
        }
      } catch (error) {
        // Limpiar tokens y forzar nuevo login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw error;
      }
    }
  },
  created() {
    // Configurar interceptor para renovar tokens expirados
    axios.interceptors.response.use(
      response => response,
      async error => {
        const originalRequest = error.config;
        
        // Si es error 401 (no autorizado) y no es un intento de refresh ya en progreso
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Intentar renovar el token
            const newToken = await this.refreshToken();
            
            // Actualizar la solicitud original con el nuevo token
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return axios(originalRequest);
          } catch (refreshError) {
            // Si falla la renovación, redirigir a login
            this.isLogin = true;
            this.message = 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.';
            this.isError = true;
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Verificar si hay un token guardado al iniciar la aplicación
    const token = localStorage.getItem('access_token');
    if (token) {
      this.setAuthHeader(token);
    }
  }
}
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #ffffff;
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100%;
}

.background-container {
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('https://wallpapers.com/images/featured/fondos-de-paisajes-naturales-k9tfch0hpfjbaxel.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

.form-container {
  max-width: 420px;
  width: 90%;
  padding: 35px;
  border-radius: 12px;
  background-color: rgba(0, 0, 0, 0.4);
  /* Transparent light background */
  backdrop-filter: blur(10px);
  box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

h1 {
  margin-bottom: 25px;
  font-weight: 600;
  font-size: 28px;
  color: #ffffff;
  text-align: center;
  text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.5);
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #ffffff;
  font-size: 15px;
  text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.4);
}

input {
  width: 100%;
  padding: 12px 15px;
  box-sizing: border-box;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 15px;
  transition: all 0.3s ease;
}

input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

input:focus {
  outline: none;
  border-color: #4a90e2;
  background-color: rgba(255, 255, 255, 0.3);
}

button {
  width: 100%;
  padding: 12px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
  transition: all 0.3s ease;
}

button:hover {
  background-color: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

button:active {
  transform: translateY(0);
}

button:disabled {
  background-color: #6c757d;
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.switch-link {
  margin-top: 20px;
  color: #ffffff;
  cursor: pointer;
  text-align: center;
  font-size: 14px;
  text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.4);
}

.switch-link:hover {
  color: #4a90e2;
  text-decoration: underline;
}

.message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 6px;
  text-align: center;
  background-color: rgba(74, 144, 226, 0.3);
}

.message.error {
  background-color: rgba(220, 53, 69, 0.3);
}

@media (max-width: 480px) {
  .form-container {
    padding: 25px;
  }
  
  h1 {
    font-size: 24px;
  }
}
</style>