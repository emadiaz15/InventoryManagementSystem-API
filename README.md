# Backend para Sistema de Gestión de Productos con Códigos QR

Este proyecto es el backend de un sistema de gestión de productos que incluye la funcionalidad de generación y visualización de códigos QR. El backend está construido utilizando **Django** y **Django REST Framework (DRF)**. El sistema permite la creación, edición y eliminación de productos, así como la generación automática de códigos QR para cada producto. Los usuarios pueden escanear estos códigos QR para obtener información sobre los productos.

## **Índice**

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Pruebas](#pruebas)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)
- [Arquitectura](#arquitectura)
- [Cronograma de Desarrollo](#cronograma-de-desarrollo)

## **Características**

- CRUD (Crear, Leer, Actualizar, Eliminar) para **productos**, **categorías** y **tipos**.
- Generación automática de **códigos QR** para cada producto.
- Visualización del código QR en el front-end.
- Sistema de **autenticación** y **autorización** basado en JWT.
- Gestión de usuarios con diferentes permisos y roles.
- Almacenamiento y visualización de imágenes para los productos.

## **Requisitos**

Antes de empezar, asegúrate de tener instalado lo siguiente en tu entorno:

- **Python 3.8+**
- **Django 3.2+**
- **PostgreSQL**
- **Pipenv** (opcional, para manejo de entornos virtuales)

## **Instalación**

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/tu-usuario/nombre-repositorio.git
   cd nombre-repositorio
   ```

2. **Crear entorno virtual (opcional)**: Si usas pipenv, puedes crear un entorno virtual con el siguiente comando:

   ```python3 -m venv env

   ```

3. **Instalar dependencias**: Si no usas pipenv, instala las dependencias con:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**: Configura tu archivo `settings.py` para que apunte a tu base de datos PostgreSQL. Asegúrate de haber creado la base de datos localmente.

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'nombre_base_datos',
           'USER': 'tu_usuario',
           'PASSWORD': 'tu_contraseña',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Aplicar migraciones**: Ejecuta las migraciones para crear las tablas en la base de datos.

   ```bash
   python manage.py migrate
   ```

6. **Correr el servidor**: Levanta el servidor localmente para verificar que todo funcione correctamente.
   ```bash
   python manage.py runserver
   ```

## **Configuración**

### Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto y agrega las variables de entorno necesarias, como la configuración de la base de datos, las claves secretas, etc.

Ejemplo de `.env`:

```bash
DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=postgres://tu_usuario:tu_contraseña@localhost:5432/nombre_base_datos
```

## **Uso**

### Endpoints principales

- **Autenticación**: `/api/auth/`
- **Productos**: `/api/products/`
- **Categorías**: `/api/categories/`
- **Tipos**: `/api/types/`
- **Generar Código QR**: `/api/products/<id>/generate_qr_code/`
- **Mostrar Código QR**: `/api/products/<id>/show_qr_code_image/`

## **API Endpoints**

| Método | Endpoint                               | Descripción                           |
| ------ | -------------------------------------- | ------------------------------------- |
| POST   | /api/auth/login/                       | Inicia sesión y obtiene el token JWT. |
| GET    | /api/products/                         | Obtiene la lista de productos.        |
| POST   | /api/products/                         | Crea un nuevo producto.               |
| GET    | /api/products/<id>/                    | Obtiene los detalles de un producto.  |
| PUT    | /api/products/<id>/                    | Actualiza un producto existente.      |
| DELETE | /api/products/<id>/                    | Elimina un producto.                  |
| GET    | /api/products/<id>/generate_qr_code/   | Genera el código QR de un producto.   |
| GET    | /api/products/<id>/show_qr_code_image/ | Muestra la imagen del código QR.      |

## **Pruebas**

### Ejecución de pruebas unitarias

El proyecto incluye una serie de pruebas unitarias para garantizar el correcto funcionamiento de las funcionalidades clave. Puedes ejecutar las pruebas con:

```bash
python manage.py test
```

## **Arquitectura**

La arquitectura de este proyecto sigue un patrón tradicional de MVC (Modelo-Vista-Controlador) y está dividida en módulos clave para la gestión de productos, categorías y tipos, con soporte para la generación y visualización de códigos QR.

### Estructura del Proyecto:

- **Django** como el framework para el backend.
- **Django REST Framework (DRF)** para la creación de la API.
- **PostgreSQL** como base de datos relacional.
- **QR Codes** generados automáticamente usando la librería `qrcode` de Python.

### Diagrama de Arquitectura:

```plaintext
┌───────────┐      ┌───────────────┐      ┌───────────────┐
│  Cliente  │      │   API Django  │      │  Base de      │
│ (React)   │◄────►│  REST         │─────►│  Datos        │
└───────────┘      └───────────────┘      └───────────────┘
                           │
                           ▼
                    Generación de QR
```

- El cliente interactúa con el API de Django a través de peticiones HTTP.
- El API maneja las solicitudes CRUD y la generación de códigos QR.
- PostgreSQL almacena los productos, categorías y tipos.
- Los códigos QR generados se almacenan en el servidor y pueden ser accesibles a través de endpoints específicos.

## **Cronograma de Desarrollo**

| Fase                            | Descripción                                                         | Duración Estimada |
| ------------------------------- | ------------------------------------------------------------------- | ----------------- |
| **Fase 1: Diseño**              | Definición de requerimientos, diseño de base de datos y wireframes. | 2 semanas         |
| **Fase 2: Desarrollo Backend**  | Desarrollo de la API, autenticación, manejo de roles y endpoints.   | 3 semanas         |
| **Fase 3: Desarrollo Frontend** | Desarrollo de las interfaces de usuario y conexión con la API.      | 3 semanas         |
| **Fase 4: Implementación**      | Despliegue del sistema en ambiente productivo, pruebas finales.     | 1 semana          |

## **Tecnologías Utilizadas**

- **Back-End**: Django, Django REST Framework
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)
- **Control de Versiones**: Git y GitHub
