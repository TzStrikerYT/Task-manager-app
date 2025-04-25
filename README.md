# Stasker

Stasker es una aplicación Flask con arquitectura hexagonal, dockerizada con base de datos PostgreSQL.

## Características
- Arquitectura hexagonal (Puertos y Adaptadores)
- API Flask para gestión de usuarios y tareas
- Base de datos PostgreSQL
- Contenerización con Docker
- Gestión de usuarios basada en roles y permisos
- Autenticación y autorización JWT
- Almacenamiento seguro de contraseñas con bcrypt
- Gestión avanzada de tareas con asignación, estados y prioridades
- Patrones de diseño: Observador y Fábrica
- Frontend moderno en Vue.js con interfaz intuitiva para gestión de tareas

## Frontend
El proyecto incluye un frontend desarrollado en Vue.js ubicado en la carpeta `taskmanager`:
- **Tecnología**: Vue.js con Composition API
- **Características**:
  - Interfaz de usuario intuitiva y responsive
  - Gestión visual de tareas con tarjetas y paneles
  - Sistema de autenticación integrado con el backend
  - Filtrado y búsqueda de tareas
  - Asignación visual de usuarios a tareas
  - Gestión de prioridades y estados con indicadores visuales
- **Integración**: El frontend se comunica con la API REST del backend mediante peticiones HTTP
- **Despliegue**: Containerizado con Docker, se ejecuta automáticamente junto con el backend

## Patrones de Diseño
- **Patrón Observador**: Implementado para notificar a los Líderes Técnicos cuando las tareas se marcan como completadas
- **Patrón Fábrica**: Utilizado para crear diferentes tipos de tareas según sus niveles de prioridad

## Configuración
1. Clonar este repositorio
2. Crear un archivo `.env` basado en `.env.example` con las variables de entorno necesarias:
   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/flask_app
   SECRET_KEY=mi-clave-secreta
   ```
3. Ejecutar con Docker Compose:
   ```
   docker compose build
   docker compose up
   ```

## Endpoints de la API

### Autenticación
- `POST /auth/login` - Iniciar sesión con email y contraseña
- `POST /auth/refresh` - Renovar token JWT

### Usuarios
- `POST /users` - Crear un nuevo usuario
- `GET /users` - Obtener lista de usuarios (filtrar por rol y término de búsqueda) - *Requiere autenticación*
- `GET /users/{id}` - Obtener un usuario específico por ID - *Requiere autenticación*

### Tareas
- `POST /tasks` - Crear una nueva tarea (con asignación a usuarios) - *Requiere autenticación*
- `GET /tasks` - Obtener lista de tareas (filtrar por estado, usuario asignado, prioridad, fecha límite) - *Requiere autenticación*
- `GET /tasks/{id}` - Obtener una tarea específica por ID - *Requiere autenticación*
- `PUT /tasks/{id}/status` - Actualizar estado de la tarea - *Requiere autenticación*
- `PUT /tasks/{id}/priority` - Actualizar prioridad de la tarea - *Requiere autenticación*
- `POST /tasks/{id}/assign/{user_id}` - Asignar usuario a tarea - *Requiere autenticación*
- `DELETE /tasks/{id}/unassign/{user_id}` - Desasignar usuario de tarea - *Requiere autenticación*

## Permisos Basados en Roles
- Los Administradores pueden acceder y modificar todos los recursos
- Los Líderes Técnicos pueden ver todas las tareas completadas de cualquier usuario
- Los Desarrolladores solo pueden ver tareas completadas a las que están asignados
- Los Líderes Técnicos y los creadores pueden cambiar las prioridades de las tareas
- Solo los usuarios asignados, creadores, administradores y líderes técnicos pueden actualizar el estado de las tareas

## Flujo de Autenticación
1. Registrar un usuario usando `POST /users`
2. Iniciar sesión usando `POST /auth/login` para obtener tokens de acceso y refresco
3. Incluir el token de acceso en el encabezado de Autorización: `Authorization: Bearer {token}`
4. Cuando el token expire, usar `POST /auth/refresh` con el token de refresco para obtener un nuevo token de acceso

## Arquitectura
Esta aplicación sigue los principios de Arquitectura Hexagonal:
- `domain`: Contiene la lógica de negocio y entidades
- `application`: Contiene casos de uso y puertos (interfaces)
- `adapters`: Contiene adaptadores para sistemas externos
- `infrastructure`: Contiene configuración y código específico del framework 

## Justificación de las Decisiones Técnicas y Arquitectónicas

### Arquitectura Hexagonal
La arquitectura hexagonal (Puertos y Adaptadores) fue seleccionada porque:
- **Desacoplamiento**: Permite separar la lógica de negocio de la infraestructura externa
- **Testabilidad**: Facilita la implementación de pruebas unitarias sin dependencias externas
- **Mantenibilidad**: La estructura clara del código reduce la deuda técnica a largo plazo
- **Adaptabilidad**: Facilita cambiar componentes externos (como base de datos) sin afectar el núcleo de la aplicación

### Tecnologías Seleccionadas
- **Flask**: Framework ligero y flexible que permite un desarrollo rápido sin imponer restricciones estructurales
- **PostgreSQL**: Base de datos relacional robusta con soporte para transacciones ACID, ideal para datos estructurados y relaciones complejas
- **Docker**: Asegura un entorno de ejecución consistente y facilita el despliegue en diferentes ambientes
- **JWT**: Proporciona un método seguro y stateless para la autenticación y autorización

### Patrones de Diseño
- **Patrón Observador**: Implementado para la notificación de tareas completadas, permitiendo un acoplamiento débil entre componentes
- **Patrón Fábrica**: Utilizado para crear diferentes tipos de tareas según su prioridad, encapsulando la lógica de creación

### Consideraciones de Escalabilidad
- **Arquitectura de Microservicios**: La estructura actual facilita la evolución hacia microservicios si fuera necesario
- **Autenticación Sin Estado**: El uso de JWT permite escalar horizontalmente sin necesidad de estado compartido
- **Contenerización**: Docker facilita el despliegue en clusters de contenedores como Kubernetes
- **Separación Backend-Frontend**: La división clara entre backend (Flask) y frontend (taskmanager) permite escalar cada componente de manera independiente

### Consideraciones de Seguridad
- **Autenticación JWT**: Implementación segura con tokens de acceso y refresco
- **Hashing de Contraseñas**: Almacenamiento seguro con bcrypt
- **Control de Acceso Basado en Roles**: Permisos granulares según el rol del usuario
- **Validación de Datos**: Validación estricta de entradas para prevenir inyecciones y otros ataques
- **Principio de Mínimo Privilegio**: Los usuarios solo pueden acceder a los recursos necesarios según su rol 

## Pruebas Unitarias

El proyecto incluye un conjunto completo de pruebas unitarias utilizando pytest para validar el funcionamiento correcto de los componentes principales:

### Tipos de Pruebas Implementadas

1. **Pruebas de Autenticación**:
   - Login exitoso y fallido
   - Renovación de tokens JWT

2. **Pruebas de Permisos**:
   - Verificación de que los Líderes Técnicos pueden ver tareas completadas
   - Verificación de que los Desarrolladores solo pueden ver tareas completadas asignadas a ellos
   - Validación de permisos para actualización de tareas por diferentes roles

3. **Pruebas de Funcionalidad**:
   - Creación, lectura, actualización y eliminación de tareas
   - Asignación y desasignación de usuarios a tareas
   - Actualización de estados y prioridades de tareas

### Cómo Ejecutar las Pruebas

#### Instalación de Dependencias

Para ejecutar las pruebas, primero debes instalar las dependencias necesarias:

#### Ejecutar Todas las Pruebas

```bash
# O Directamente con Poetry sin activar el entorno
poetry run pytest
```

#### Ejecutar Pruebas Específicas

```bash
# Ejecutar una prueba específica
poetry run pytest tests/test_api.py::test_login_success

# Ejecutar pruebas con un patrón específico
poetry run pytest tests/test_api.py -k "task"

# Ejecutar pruebas con reporte de cobertura
poetry run pytest --cov=app tests/
```

#### Ejecutar Pruebas en el Contenedor Docker

También es posible ejecutar las pruebas dentro del contenedor Docker:

```bash
# Construir la imagen con las dependencias de desarrollo
docker compose build app

# Ejecutar las pruebas dentro del contenedor
docker compose run --rm app poetry run pytest
``` 