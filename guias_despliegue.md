# Guía de Despliegue en la Web (Paso a Paso)

Este instructivo te guiará para subir tu aplicación de depósito a internet y permitir el acceso de cualquier computadora con conexión web, manteniendo tu base de datos a salvo.

---

## Opción A: Despliegue en Render.com (Recomendado y Moderno)
Render ofrece un plan gratuito para hospedar aplicaciones web y permite conectar un "disco duro persistente" para evitar que se borren los datos al reiniciar el servidor.

### Paso 1: Subir el proyecto a GitHub
1. Crea una cuenta gratuita en [GitHub](https://github.com/) si no tienes una.
2. Descarga e instala [Git](https://git-scm.com/) en tu computadora.
3. Crea un repositorio en GitHub con el nombre `deposito-stock`.
4. Sube la carpeta de tu aplicación al repositorio ejecutando estos comandos en la consola (dentro de la carpeta `Deposito`):
   ```bash
   git init
   git add .
   git commit -m "primer commit: preparar para web"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/deposito-stock.git
   git push -u origin main
   ```

### Paso 2: Crear el servicio en Render
1. Regístrate en [Render.com](https://render.com/) (puedes iniciar sesión con tu cuenta de GitHub).
2. En el panel principal, haz clic en **New +** y selecciona **Web Service**.
3. Conecta tu repositorio de GitHub `deposito-stock`.
4. Llena los siguientes campos:
   * **Name**: `deposito-stock` (o el nombre que prefieras).
   * **Region**: Elige la más cercana (ej. `Ohio (us-east-2)` o `Oregon (us-west-2)`).
   * **Branch**: `main`.
   * **Runtime**: `Python`.
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
   * **Instance Type**: Elige **Free** ($0/month).

### Paso 3: Configurar el Disco Persistente (CRÍTICO)
> [!IMPORTANT]
> Si omites este paso, cada vez que Render reinicie tu servidor, la base de datos se restablecerá y perderás los productos creados.
1. En el menú del servicio en Render, ve a la pestaña **Disks** (Discos).
2. Haz clic en **Add Disk**.
3. Completa los campos:
   * **Name**: `deposito-data`
   * **Mount Path**: `/data` (Ruta donde se montará el disco).
   * **Size**: `1 GB` (Totalmente gratis en su capa base).
4. Guarda los cambios.

### Paso 4: Configurar la variable de entorno
1. En el menú del servicio en Render, ve a la pestaña **Environment** (Entorno).
2. Haz clic en **Add Environment Variable**.
3. Define los siguientes valores:
   * **Key**: `DB_PATH`
   * **Value**: `/data/database.db` (Esto le indica a nuestro programa que guarde la base de datos dentro del disco persistente que creamos en el paso anterior).
4. Haz clic en **Save Changes**.

¡Listo! Render compilará tu aplicación en unos minutos y te dará una dirección pública (ej. `https://deposito-stock.onrender.com`) desde la cual tu equipo podrá acceder desde cualquier parte.

---

## Opción B: Despliegue en PythonAnywhere (100% Gratis y Simple)
PythonAnywhere está enfocado exclusivamente en Python, es gratuito y no requiere configuraciones de discos para SQLite, ya que tu almacenamiento de usuario es persistente por defecto.

### Paso 1: Crear cuenta y subir archivos
1. Crea una cuenta gratuita en [PythonAnywhere](https://www.pythonanywhere.com/).
2. Ve a la pestaña **Files** y sube los archivos de tu proyecto, o bien ve a **Consoles**, abre una consola **Bash** y clona tu repositorio de GitHub:
   ```bash
   git clone https://github.com/TU_USUARIO/deposito-stock.git
   ```

### Paso 2: Crear el Entorno Virtual (Virtualenv)
En la consola Bash de PythonAnywhere, crea un entorno virtual e instala las dependencias:
```bash
mkvirtualenv --python=python3.10 venv
pip install -r deposito-stock/requirements.txt
```
*(Anota la ruta de tu entorno virtual, suele ser `/home/TU_USUARIO/.virtualenvs/venv`)*

### Paso 3: Configurar la sección Web
1. En el panel de PythonAnywhere, ve a la pestaña **Web**.
2. Haz clic en **Add a new web app**.
3. Selecciona **Manual Configuration** (no elijas Flask directamente, ya que usaremos nuestro propio virtualenv) y selecciona **Python 3.10**.
4. En la configuración de la Web App:
   * **Source code**: `/home/TU_USUARIO/deposito-stock`
   * **Working directory**: `/home/TU_USUARIO/deposito-stock`
   * **Virtualenv**: Introduce la ruta del paso 2 (`/home/TU_USUARIO/.virtualenvs/venv`).

### Paso 4: Modificar el archivo WSGI de PythonAnywhere
1. En la pestaña **Web**, busca la sección **Code** y haz clic en el enlace del archivo **WSGI configuration file** (suele llamarse `/var/www/tu_usuario_pythonanywhere_com_wsgi.py`).
2. Borra todo su contenido y escribe únicamente esto:
   ```python
   import sys
   import os

   # Añadir ruta del proyecto al path
   path = '/home/TU_USUARIO/deposito-stock'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
3. Guarda el archivo.
4. Regresa a la pestaña **Web** y haz clic en el botón verde **Reload** (Recargar).

Tu aplicación estará disponible en la dirección: `http://TU_USUARIO.pythonanywhere.com`.

---

## Opción C: Despliegue en Vercel (Rápido y Moderno - Base de Datos Temporal)
Vercel es una excelente opción para publicar la aplicación de forma rápida y gratuita. Sin embargo, su infraestructura serverless utiliza un sistema de archivos de solo lectura y las funciones se apagan por inactividad.

> [!WARNING]
> **Base de Datos Efímera:**
> Por defecto, la base de datos SQLite se creará en la carpeta temporal (`/tmp/database.db`). Esto significa que cada vez que la función serverless de Vercel se reinicie (lo cual ocurre frecuentemente por inactividad), **se perderán todos los productos y movimientos registrados**.
>
> **Solución para Producción:**
> Si deseas usar Vercel con datos persistentes, debes conectar una base de datos externa en la nube (como PostgreSQL en Neon.tech, Supabase o Render PostgreSQL) y modificar el adaptador de la base de datos en el código para que apunte a ella.

### Paso 1: Configurar el proyecto
Asegúrate de que los archivos `vercel.json` y `requirements.txt` estén presentes en la raíz de tu proyecto. El archivo `vercel.json` ya ha sido configurado para que Vercel sepa cómo ejecutar la aplicación Flask usando `@vercel/python`.

### Paso 2: Subir el proyecto a GitHub
Si no lo has hecho aún, inicializa Git y sube tu proyecto a un repositorio de GitHub como se describe en el **Paso 1 de la Opción A**.

### Paso 3: Crear el proyecto en Vercel
1. Regístrate o inicia sesión en [Vercel.com](https://vercel.com/) (preferentemente con tu cuenta de GitHub).
2. En tu Dashboard principal, haz clic en **Add New...** y selecciona **Project**.
3. Importa tu repositorio `deposito-stock` desde la lista de repositorios conectados de GitHub.
4. En la configuración del proyecto:
   * **Framework Preset**: Déjalo en `Other`.
   * **Root Directory**: `./` (directorio raíz).
   * **Build and Development Settings**: No es necesario modificar nada.
5. Haz clic en **Deploy**.

---

## Opción D: Conectar Base de Datos Relacional en la Nube (Supabase PostgreSQL)
Supabase te ofrece una base de datos PostgreSQL robusta y gratuita en la nube. Es la solución ideal para conectar a servicios como **Vercel** (evitando perder tus datos al reiniciarse la app) o para desarrollo local con almacenamiento remoto.

### Paso 1: Crear el proyecto en Supabase
1. Entra a [Supabase.com](https://supabase.com/) y regístrate con tu correo o cuenta de GitHub.
2. En el panel principal, haz clic en **New Project** (Nuevo proyecto).
3. Selecciona tu organización por defecto y rellena los datos del proyecto:
   * **Name**: `deposito-db` (o el que prefieras).
   * **Database Password**: Escribe una contraseña fuerte y **guárdala muy bien**, la necesitarás para la conexión.
   * **Region**: Selecciona la región más cercana a tus usuarios (ej. `South America (São Paulo)` para Sudamérica, o `East US` / `West US`).
4. Haz clic en **Create new project** y espera unos minutos a que la base de datos termine de crearse.

### Paso 2: Obtener la URI de conexión (Connection String)
1. En el menú lateral izquierdo de tu proyecto en Supabase, haz clic en el icono de engranaje (**Project Settings**).
2. Ve a la sección **Database** (Base de datos).
3. Desplázate hacia abajo hasta la sección **Connection string** (Cadena de conexión) y selecciona la pestaña **URI**.
4. Copia la dirección que te muestra. Tendrá una estructura similar a esta:
   ```text
   postgresql://postgres.[ID_DE_TU_PROYECTO]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
5. Reemplaza `[YOUR-PASSWORD]` en la cadena de conexión con la contraseña que creaste en el **Paso 1**.

### Paso 3: Configurar la variable en el servidor o entorno local

#### A. Para uso Local (en tu computadora)
1. En la raíz del proyecto, crea un archivo llamado `.env` (si no existe ya).
2. Añade la variable `DATABASE_URL` con tu URI de conexión:
   ```env
   DATABASE_URL=postgresql://postgres.tu_id:tu_password_real@aws-0-tu_region.pooler.supabase.com:6543/postgres
   ```
3. Al iniciar la aplicación localmente (`run.py` o `python app.py`), el backend detectará automáticamente que estás usando PostgreSQL y se conectará a Supabase en lugar del archivo SQLite local.

#### B. Para uso en Vercel
1. Ve al panel de control de tu proyecto en **Vercel.com**.
2. Dirígete a la pestaña **Settings** (Configuración) -> **Environment Variables** (Variables de entorno).
3. Agrega una nueva variable:
   * **Key**: `DATABASE_URL`
   * **Value**: *(Pega la cadena de conexión de Supabase, asegurándote de haber reemplazado la contraseña)*
4. Haz clic en **Save**.
5. Ve a la pestaña **Deployments**, haz clic en los tres puntos de tu último despliegue y selecciona **Redeploy** (Redesplegar) para aplicar los cambios de variables de entorno.

#### C. Para uso en Render
1. Ve al panel de control de tu servicio en **Render.com**.
2. Dirígete a la pestaña **Environment** (Entorno).
3. Añade la variable `DATABASE_URL` con tu URI de conexión de Supabase.
4. Guarda los cambios. (El servicio se reiniciará automáticamente aplicando la base de datos de Supabase).

---

### Nota sobre la Inicialización Automática
Nuestra aplicación está configurada para inicializar la base de datos automáticamente al arrancar. Cuando conectes tu base de datos de Supabase por primera vez e inicies la app:
1. Se crearán automáticamente las tablas: `productos`, `transacciones` y `usuarios`.
2. Se registrará un usuario administrador inicial por defecto:
   * **Usuario**: `admin`
   * **Contraseña**: `admin123` (recuerda cambiar esta contraseña desde la configuración del perfil al iniciar sesión por primera vez).


¡Eso es todo! Vercel compilará la aplicación en unos segundos y te entregará una URL pública (ej. `https://deposito-stock.vercel.app`) para acceder desde cualquier dispositivo.
