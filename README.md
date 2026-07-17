# Depósito Inteligente - Manual Técnico y Documentación de Desarrollo

Este documento sirve como guía técnica para comprender, mantener y modificar el sistema de **Gestión de Stock de Depósito Inteligente**. Proporciona una explicación detallada de la arquitectura del software, la estructura de archivos, el flujo de datos y los pasos necesarios para realizar modificaciones o compilaciones futuras.

---

## 1. Arquitectura del Sistema

La aplicación está diseñada bajo una arquitectura híbrida de **Servidor Local + Cliente de Escritorio Liviano** con opción de base de datos local o remota en la nube.

```mermaid
graph TD
    subgraph Cliente de Escritorio (Windows)
        A[desktop.exe / desktop.py] -->|Carga interfaz| B[pywebview]
        B -->|Renderiza HTML/CSS/JS| C[Frontend App]
    end

    subgraph Backend Local (Flask)
        C -->|Peticiones HTTP/REST| D[app.py - API Flask]
        D -->|Consultas SQL| E[backend/db.py]
        D -->|Generación de Reportes| F[backend/reports.py]
    end

    subgraph Almacenamiento
        E -->|SQLite (Desarrollo/Offline)| G[(database.db)]
        E -->|PostgreSQL (Producción/Cloud)| H[(Supabase Cloud DB)]
    end
```

### Componentes Clave:
* **Frontend:** Implementado con HTML5 semántico, Vanilla CSS (con variables de diseño, temas oscuro/claro y efectos premium) y Vanilla Javascript.
* **Backend:** Un servidor Flask ligero en Python que expone una API REST para interactuar con la base de datos y generar reportes.
* **Base de Datos:** Un adaptador híbrido en `db.py` que conmuta entre **SQLite** (archivo local `.db`) y **PostgreSQL** (en la nube) basándose en la presencia de la variable `DATABASE_URL` en las variables de entorno.
* **Cliente de Escritorio:** Desarrollado sobre `pywebview` para incrustar el motor de renderizado de Microsoft Edge (WebView2) de forma nativa en Windows sin mostrar barra de navegación o controles de explorador.

---

## 2. Estructura del Proyecto y Archivos

El proyecto está organizado de la siguiente manera:

```text
Deposito/
│
├── backend/                  # Código y lógica del servidor
│   ├── db.py                 # Conexiones, consultas SQL, inicialización de tablas y usuarios
│   └── reports.py            # Generación de reportes PDF (ReportLab) y Excel (Openpyxl)
│
├── static/                   # Recursos estáticos del frontend
│   ├── css/
│   │   └── style.css         # Hojas de estilo generales (variables CSS, animaciones y responsive)
│   └── js/
│       └── app.js            # Lógica interactiva del cliente (filtros, búsquedas y peticiones)
│
├── templates/                # Plantillas HTML
│   ├── index.html            # Pantalla y panel principal (Dashboard, Inventario, Reportes, etc.)
│   └── login.html            # Pantalla de inicio de sesión
│
├── .env                      # Variables de configuración y credenciales de base de datos (ignorado en Git)
├── .gitignore                # Reglas de archivos ignorados por el control de versiones Git
├── app.py                    # Servidor web Flask y definición de endpoints de la API REST
├── desktop.py                # Inicialización de la ventana gráfica pywebview
├── desktop.spec              # Archivo de especificación de PyInstaller para compilar el ejecutable
├── iniciar.bat               # Archivo ejecutable por lotes para iniciar el programa con doble clic
├── run.py                    # Automatizador del entorno virtual Python (.venv) y dependencias
├── requirements.txt          # Dependencias y librerías de Python requeridas
└── guias_despliegue.md       # Guía de pasos para desplegar en la nube (Render, Vercel, Supabase)
```

---

## 3. Variables de Entorno y Configuración (.env)

El archivo `.env` controla el comportamiento de la aplicación en la máquina en la que se ejecuta:

* `DATABASE_URL`: Cadena de conexión PostgreSQL (obligatoria para Supabase). Si no se define, el backend usa SQLite.
* `SECRET_KEY`: Llave de encriptación para firmar las cookies de sesión del usuario.
* `DB_PATH`: Ruta opcional para cambiar la ubicación de la base de datos SQLite en disco.

*Ejemplo de archivo `.env`:*
```env
DATABASE_URL=postgresql://postgres.xxx:mi_password@aws-0-ca-central-1.pooler.supabase.com:6543/postgres
SECRET_KEY=clave-secreta-de-seguridad-aqui
```

---

## 4. Endpoints de la API REST (`app.py`)

El servidor Flask actúa como API y contiene los siguientes accesos:

### Autenticación de Sesiones
* `POST /api/login`: Verifica credenciales del usuario y crea la sesión.
* `POST /api/logout`: Limpia las cookies de sesión del usuario.
* `GET /api/session-status`: Comprueba si hay una sesión activa y devuelve los datos del usuario.
* `POST /api/cambiar-password`: Permite al usuario logueado cambiar su clave.

### Inventario y Productos
* `GET /api/productos`: Lista de productos. Acepta filtros query: `?q=` (búsqueda por ID o nombre) y `?categoria=`.
* `GET /api/productos/<id>`: Devuelve los detalles de un producto específico.
* `POST /api/productos`: Crea un nuevo producto (o suma existencias si el nombre ya existe).
* `DELETE /api/productos/<id>`: Elimina permanentemente un producto e historial de transacciones asociado.

### Transacciones e Historial
* `GET /api/transacciones`: Devuelve la lista histórica de movimientos. Acepta el parámetro de paginación/límite `?limit=`.
* `POST /api/transacciones`: Registra una entrada o una salida de material hacia un área.
* `GET /api/categorias`: Devuelve la lista única de categorías de productos registradas.
* `GET /api/areas`: Devuelve la lista única de áreas de destino registradas para salidas.

### Reportes
* `GET /api/reportes/excel`: Genera y descarga un archivo `.xlsx`. Acepta filtros opcionales: `?tipo=stock|movimientos`, `?producto_id=`, `?area=`, `?tipo_movimiento=`, `?fecha_inicio=`, y `?fecha_fin=`.
* `GET /api/reportes/pdf`: Genera y descarga un reporte en formato `.pdf` utilizando los mismos filtros.

---

## 5. Guía de Mantenimiento y Modificaciones Comunes

### A. Modificar estilos visuales o colores
El diseño premium se gestiona mediante **Variables de CSS (CSS Custom Properties)** definidas al principio de [static/css/style.css](file:///c:/Users/balbi/OneDrive/Desktop/Deposito/static/css/style.css).
* Para cambiar los colores corporativos, temas de fondo o fuentes, solo edita el bloque `:root` (comunes), `body.dark-theme` (tema oscuro) y `body.light-theme` (tema claro).
* El sistema cambiará automáticamente toda la interfaz sin necesidad de editar selectores individuales.

### B. Optimización de búsquedas y rendimiento
* La búsqueda de autocompletado en el formulario de transacciones funciona localmente a través de la lista en memoria `state.productos` dentro de [static/js/app.js](file:///c:/Users/balbi/OneDrive/Desktop/Deposito/static/js/app.js). Esto se diseñó para evitar la latencia que produce la consulta directa a internet (Supabase).
* Si agregas un nuevo campo a los productos, asegúrate de añadirlo en el backend en `db.py` e hidratarlo en Javascript en las funciones `renderInventoryTable()` y `selectProductForTransaction()`.

### C. Cómo agregar un nuevo reporte o columna
1. Si necesitas una nueva columna en la tabla de productos (ej. "Ubicación en Estante"):
   * Modifica los comandos `CREATE TABLE` en `init_db()` en [db.py](file:///c:/Users/balbi/OneDrive/Desktop/Deposito/backend/db.py).
   * Modifica `crear_producto()` y `get_productos()` para mapear el nuevo valor en la consulta SQL.
   * En [reports.py](file:///c:/Users/balbi/OneDrive/Desktop/Deposito/backend/reports.py), actualiza las listas `headers_stock` y `row_data` en `generate_excel_report()` e incrementa el ancho de columnas correspondiente. Realiza el mismo ajuste en la tabla `stock_table` dentro de `generate_pdf_report()`.

---

## 6. Proceso de Compilación (PyInstaller)

Cuando modifiques el código del backend (`.py`), las plantillas (`.html`), o los estilos (`.css`/`.js`), el archivo ejecutable (`desktop.exe`) **debe volver a compilarse**.

### Comando de compilación:
Desde la terminal del proyecto (con el entorno virtual activo), ejecuta:
```bash
.venv\Scripts\pyinstaller --clean desktop.spec
```

### Configuración crítica del archivo `desktop.spec`:
* `upx=False`: La compresión UPX está desactivada para prevenir problemas de descompresión de librerías nativas y DLLs en ordenadores de destino.
* `collect_all('clr_loader')` y `collect_all('pythonnet')`: Estos módulos recopilan de forma forzosa las DLLs nativas de comunicación de interfaz .NET (`ClrLoader.dll`) necesarias para que `pywebview` funcione en cualquier versión de Windows sin crasheos.
* **Nota:** Tras compilar, recuerda que el ejecutable `dist/desktop.exe` requiere tener una copia del archivo `.env` en su mismo directorio para saber a qué base de datos conectarse.
