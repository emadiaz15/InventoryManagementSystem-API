# Backend para Sistema de Gestión de Productos

Este proyecto es el backend de un sistema de gestión de productos orientado a la administración de inventarios, especializado en la gestión de un producto en particular (en esta versión, cables). El sistema permite a los administradores y operarios gestionar productos, monitorear niveles de stock, realizar seguimientos de órdenes de corte, y generar reportes. El backend está construido utilizando **Django** y **Django REST Framework (DRF)**.

## **Índice**

- [Descripción del proyecto](#Descripcion-del-proyecto)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Pruebas](#pruebas)
- [Arquitectura](#arquitectura)

## **Descripción del Proyecto**

Nombre del Proyecto: Inventory Management System

**Propósito**: Este sistema facilita la gestión de inventario y permite realizar un seguimiento detallado de productos dentro de una empresa o tienda. Inicialmente se centra en la gestión de cables, permitiendo a los administradores organizar productos, supervisar niveles de stock, manejar órdenes de corte, y generar reportes. Los operarios también pueden acceder a funciones como la consulta de productos y el cambio de estado de las órdenes de corte.

## **Características**

- CRUD para productos, categorías, tipos y marcas.
- Gestión de stock y visualización de la ubicación de productos en el depósito.
- Sistema de autenticación y autorización basado en JWT.
- Gestión de usuarios, roles y permisos.
- Gestión de órdenes de corte con cambio de estado (pendiente, en proceso, finalizado).
- Generación de reportes de inventarios, incluyendo órdenes de corte y productos faltantes.

## **Requisitos**

Antes de empezar, asegúrate de tener instalado lo siguiente en tu entorno:

- **Python 3.8+**
- **Django 3.2+**
- **PostgreSQL**
- **Pipenv** (opcional, para manejo de entornos virtuales)

## **Instalación**

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/emadiaz15/InventoryManagementSystem-API.git
   cd InventoryManagementSystem-API
   ```

2. **Crear entorno virtual (opcional)**: Si usas pipenv, puedes crear un entorno virtual con el siguiente comando:

   ```bash
   python3 -m venv env
   ```

3. **Instalar dependencias**: Si no usas pipenv, instala las dependencias con:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**: Configura tu archivo `settings/local.py` para que apunte a tu base de datos PostgreSQL. Asegúrate de haber creado la base de datos localmente.

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

- **Autenticación**: `/api/v1/user/`
- **Productos**: `/api/v1/products/`
- **Categorías**: `/api/v1/categories/`
- **Tipos**: `/api/v1/types/`

## **API Endpoints**

| Método| Endpoint              | Descripción                           |
| ------| -------------------   | ------------------------------------- |
| POST  |/api/v1/user/login/    | Inicia sesión y obtiene el token JWT. |
| GET   |/api/v1/products/      | Obtiene la lista de productos.        |
| POST  |/api/v1/products       | Crea un nuevo producto.               |
| GET   |/api/v1/products/<id>/ | Obtiene los detalles de un producto.  |
| PUT   |/api/v1/products/<id>/ | Actualiza un producto existente.      |
| DELETE|/api/v1/products/<id>/ | Elimina un producto.                  |

## **Arquitectura**

La arquitectura de este proyecto sigue un patrón tradicional de MVC (Modelo-Vista-Controlador) y está dividida en módulos clave para la gestión de productos, categorías y tipos.

### Estructura del Proyecto:

- **Django** como el framework para el backend.
- **Django REST Framework (DRF)** para la creación de la API.
- **PostgreSQL** como base de datos relacional.

## **Tecnologías Utilizadas**

- **Back-End**: Django, Django REST Framework
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)
- **Control de Versiones**: Git y GitHub
