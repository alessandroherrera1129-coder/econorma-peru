# Guía de Despliegue en la Nube (24/7 Gratis) — EcoNorma Perú

Esta guía te explica paso a paso cómo publicar **EcoNorma Perú** en internet de forma permanente y gratuita para que cualquier persona en el mundo pueda acceder desde su celular o computadora.

---

## Opción Recomendada: Despliegue en Render.com (Gratis con HTTPS automático)

Render es una de las plataformas en la nube más estables, modernas y gratuitas para aplicaciones Python / FastAPI.

### Paso 1: Subir el proyecto a GitHub

1. Ingresa a [github.com](https://github.com) e inicia sesión con tu cuenta.
2. Crea un nuevo repositorio (por ejemplo llamado: `econorma-peru`).
3. En tu computadora, abre la terminal en la carpeta del proyecto:
   ```powershell
   cd C:\Users\USER\.gemini\antigravity\scratch\econorma-peru
   ```
4. Inicializa git y sube los archivos:
   ```powershell
   git init
   git add .
   git commit -m "Publicación inicial de EcoNorma Perú"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/econorma-peru.git
   git push -u origin main
   ```

---

### Paso 2: Conectar con Render.com

1. Ve a [dashboard.render.com](https://dashboard.render.com/) y regístrate o inicia sesión con tu cuenta de GitHub.
2. Haz clic en el botón azul **«New +»** en la parte superior derecha y selecciona **«Web Service»**.
3. Selecciona la opción **«Build and deploy from a Git repository»** y haz clic en **Next**.
4. Elige tu repositorio `econorma-peru` y dale a **Connect**.

---

### Paso 3: Configurar el servicio (Render lo detecta automáticamente con `render.yaml`)

Render leerá automáticamente el archivo `render.yaml` que dejamos listo. Si te solicita confirmar los campos:

* **Name**: `econorma-peru` (o el nombre que prefieras)
* **Region**: `Oregon (US West)` o `Ohio (US East)`
* **Branch**: `main`
* **Runtime**: `Python 3`
* **Build Command**:
  ```bash
  pip install -r requirements.txt && python scripts/generate_seed_parameters.py && python scripts/verify_data.py
  ```
* **Start Command**:
  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
  ```
* **Instance Type**: **Free** (Gratis)

---

### Paso 4: Variables de Entorno (Opcional)

En la sección **Environment Variables**, puedes definir o personalizar:

* `APP_NAME`: `EcoNorma Perú`
* `APP_TAGLINE`: `Plataforma de Consulta de Estándares Ambientales del Perú`
* `PROJECT_AUTHOR`: `Alessandro Piero Herrera Balladares`
* `PROJECT_PHONE`: `+51 981520990`
* `PROJECT_EMAIL`: `alessandroherrera1129@gmail.com`
* `ADMIN_TOKEN`: `tu_clave_secreta_aqui`

---

### Paso 5: ¡Listo!

Haz clic en **«Create Web Service»**. 

Render compilará el proyecto en aproximadamente 2 minutos y te otorgará un enlace público permanente con certificado de seguridad SSL incluido:

👉 **`https://econorma-peru.onrender.com`**

Cualquier persona desde cualquier celular, tablet o computadora en el mundo podrá ingresar directamente a esa URL.

---

## Configurar un Dominio Propio (ej. `econorma.pe`)

Si más adelante compras un dominio en NIC.pe o Namecheap:
1. En el panel de tu servicio en Render, ve a **Settings** > **Custom Domains**.
2. Escribe tu dominio (ej. `econorma.pe` o `www.econorma.pe`).
3. Agrega los registros CNAME o DNS que te indique Render.
4. Render generará automáticamente el certificado HTTPS gratuito para tu dominio propio.
