# Tests para la API de Flask

Este directorio contiene pruebas unitarias para los endpoints de la API de Flask usando pytest.

## Pruebas implementadas

1. **Autenticación**: Login exitoso y fallido
2. **Permisos de tareas completadas**: 
   - Verificación de que los Líderes Técnicos pueden ver tareas completadas
   - Verificación de que los Desarrolladores y Administradores no pueden ver tareas completadas
3. **Acceso a tareas por ID**: 
   - Líderes Técnicos pueden acceder a tareas completadas específicas
   - Desarrolladores no pueden acceder a tareas completadas específicas
4. **Actualización de usuario**: Prueba de actualización exitosa de un usuario
5. **Creación de tareas**: Validación de campos requeridos

## Cómo ejecutar las pruebas

### Instalación de dependencias

Para instalar las dependencias necesarias para las pruebas, utilizamos Poetry:

```bash
# Instalar todas las dependencias, incluyendo las de desarrollo
poetry install --with dev --no-root

# Activar el entorno virtual de Poetry (opcional)
poetry shell
```

### Ejecutar todas las pruebas

```bash
# Si estás dentro del entorno virtual de Poetry
pytest

# O directamente con Poetry sin activar el entorno
poetry run pytest
```

### Ejecutar pruebas específicas

```bash
# Ejecutar una única prueba
poetry run pytest tests/test_api.py::test_login_success

# Ejecutar pruebas con un patrón específico
poetry run pytest tests/test_api.py -k "task"

# Ejecutar pruebas con reportes de cobertura
poetry run pytest --cov=app tests/
```

### Ejecutar pruebas con salida detallada

```bash
poetry run pytest -v
``` 