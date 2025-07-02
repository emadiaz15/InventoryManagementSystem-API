# Backend para Sistema de Gestión de Productos

Este proyecto es el backend de un sistema de gestión de productos orientado a la administración de inventarios, especializado en la gestión de un producto en particular (en esta versión, cables). El sistema permite a los administradores y operarios gestionar productos, monitorear niveles de stock, realizar seguimientos de órdenes de corte, y generar reportes. El backend está construido utilizando **Django** y **Django REST Framework (DRF)**.

## **Índice**

- [Descripcion del proyecto](#Descripcion-del-proyecto)
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

- **Autenticación**: `/api/user/`
- **Productos**: `/api/products/`
- **Categorías**: `/api/categories/`
- **Tipos**: `/api/types/`

## **API Endpoints**

| Método | Endpoint            | Descripción                           |
| ------ | ------------------- | ------------------------------------- |
| POST   | /api/auth/login/    | Inicia sesión y obtiene el token JWT. |
| GET    | /api/products/      | Obtiene la lista de productos.        |
| POST   | /api/products/      | Crea un nuevo producto.               |
| GET    | /api/products/<id>/ | Obtiene los detalles de un producto.  |
| PUT    | /api/products/<id>/ | Actualiza un producto existente.      |
| DELETE | /api/products/<id>/ | Elimina un producto.                  |

### Archivos de Productos y Subproductos

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| POST | /api/products/<product_id>/files/upload/ | Sube archivos para el producto | Admin |
| GET | /api/products/<product_id>/files/ | Lista archivos del producto | Autenticado |
| GET | /api/products/<product_id>/files/<file_id>/download/ | Descarga un archivo del producto | Autenticado |
| DELETE | /api/products/<product_id>/files/<file_id>/delete/ | Elimina un archivo del producto | Admin |
| POST | /api/products/<product_id>/subproducts/<subproduct_id>/files/upload/ | Sube archivos para el subproducto | Admin |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/files/ | Lista archivos del subproducto | Autenticado |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/files/<file_id>/download/ | Descarga un archivo del subproducto | Autenticado |
| DELETE | /api/products/<product_id>/subproducts/<subproduct_id>/files/<file_id>/delete/ | Elimina un archivo del subproducto | Admin |

Los endpoints de subida y eliminación requieren permisos de **administrador**. Para listar o descargar archivos basta con estar **autenticado**.

### Categorías

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/categories/ | Lista las categorías activas | Autenticado |
| POST | /api/categories/create/ | Crea una nueva categoría | Admin |
| GET | /api/categories/<id>/ | Detalles de una categoría | Autenticado |
| PUT | /api/categories/<id>/ | Actualiza una categoría | Admin |
| DELETE | /api/categories/<id>/ | Elimina una categoría | Admin |

### Tipos

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/types/ | Lista los tipos de productos | Autenticado |
| POST | /api/types/create/ | Crea un nuevo tipo | Admin |
| GET | /api/types/<id>/ | Detalles de un tipo | Autenticado |
| PUT | /api/types/<id>/ | Actualiza un tipo | Admin |
| DELETE | /api/types/<id>/ | Elimina un tipo | Admin |

### Subproductos

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/products/<product_id>/subproducts/ | Lista los subproductos de un producto | Autenticado |
| POST | /api/products/<product_id>/subproducts/create/ | Crea un subproducto | Admin |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/ | Detalles de un subproducto | Autenticado |
| PUT | /api/products/<product_id>/subproducts/<subproduct_id>/ | Actualiza un subproducto | Admin |
| DELETE | /api/products/<product_id>/subproducts/<subproduct_id>/ | Elimina un subproducto | Admin |

### Órdenes de Corte

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/cutting-orders/ | Lista todas las órdenes de corte | Autenticado |
| GET | /api/cutting-orders/assigned/ | Órdenes asignadas al usuario | Autenticado |
| POST | /api/cutting-orders/create/ | Crea una orden de corte | Admin |
| GET | /api/cutting-orders/<id>/ | Detalle de una orden | Autenticado |
| PUT | /api/cutting-orders/<id>/ | Actualiza una orden | Admin |
| PATCH | /api/cutting-orders/<id>/ | Actualiza parcialmente una orden | Admin |
| DELETE | /api/cutting-orders/<id>/ | Elimina una orden | Admin |

### Eventos de Stock

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/products/<id>/stock/events/ | Historial de stock del producto | Autenticado |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/stock/events/ | Historial de stock del subproducto | Autenticado |

### Usuarios

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| POST | /api/users/login/ | Inicia sesión y obtiene el token JWT | Público |
| POST | /api/users/register/ | Registra un nuevo usuario | Público |
| POST | /api/users/logout/ | Cierra la sesión del usuario | Autenticado |
| GET | /api/users/profile/ | Obtiene el perfil del usuario autenticado | Autenticado |
| GET | /api/users/list/ | Lista todos los usuarios | Admin |
| GET | /api/users/<id>/ | Detalles de un usuario | Autenticado |
| PUT | /api/users/<id>/ | Actualiza un usuario | Propietario/Admin |
| DELETE | /api/users/<id>/ | Elimina un usuario | Admin |
| DELETE | /api/users/image/<file_id>/delete/ | Elimina una imagen de perfil | Autenticado |
| PUT | /api/users/image/<file_id>/replace/ | Reemplaza una imagen de perfil | Autenticado |
| POST | /api/users/password-reset/confirm/<uidb64>/<token>/ | Confirma el restablecimiento de contraseña | Admin |

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

## **Pruebas**

Para ejecutar las pruebas utiliza la configuración de tests ubicada en `inventory_management.settings.test`.


```bash
DJANGO_SETTINGS_MODULE=inventory_management.settings.test python manage.py test
```
O bien con PyTest:

También puedes usar `pytest` de la siguiente forma:

```bash
DJANGO_SETTINGS_MODULE=inventory_management.settings.test python -m pytest -q
```
