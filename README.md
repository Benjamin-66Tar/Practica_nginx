# Práctica: Nginx Beginner's Guide

Plantilla basada en la sección **"Setting Up a Simple Proxy Server"** de la [Guía Oficial de Nginx](https://nginx.org/en/docs/beginners_guide.html).

---

## 📁 Estructura del Proyecto

```text
.
├── docker-compose.yml       # Configuración para levantar el contenedor Nginx
├── nginx.conf               # Configuración completa de Nginx con los 2 servidores
└── data/
    ├── up1/
    │   └── index.html       # Servido por el puerto 8080 (root /data/up1)
    └── images/
        └── sample.svg       # Servido por el puerto 80 en /images/ (root /data)
```

---

## ⚙️ ¿Cómo funciona esta configuración?

En [nginx.conf](nginx.conf) se definen **dos bloques `server`**:

1. **Servidor Backend (puerto 8080):**
   ```nginx
   server {
       listen 8080;
       root /data/up1;

       location / {
       }
   }
   ```
   Escucha peticiones en el puerto 8080 y busca los archivos solicitados directamente dentro de `/data/up1/`.

2. **Servidor Proxy Inverso (puerto 80):**
   ```nginx
   server {
       listen 80;

       location / {
           proxy_pass http://localhost:8080;
       }

       location /images/ {
           root /data;
       }
   }
   ```
   - Si la ruta comienza con `/images/`, busca el archivo en `/data/images/`.
   - Cualquier otra ruta se envía mediante proxy al servidor interno en `http://localhost:8080`.

---

## 🚀 Cómo ejecutar la práctica

### Con Docker (Recomendado)

1. **Iniciar el contenedor:**
   ```powershell
   docker compose up -d
   ```

2. **Probar los accesos:**
   - **Acceso directo al backend (8080):**
     Abre [http://localhost:8080](http://localhost:8080) en el navegador o ejecuta:
     ```powershell
     curl http://localhost:8080
     ```
     *(Verás el contenido de `/data/up1/index.html`)*

   - **Acceso a través del Proxy (puerto 80):**
     Abre [http://localhost/](http://localhost/) en el navegador o ejecuta:
     ```powershell
     curl http://localhost
     ```
     *(El proxy en el puerto 80 redirige la petición internamente a `localhost:8080`)*

   - **Acceso a imágenes estáticas:**
     Abre [http://localhost/images/sample.svg](http://localhost/images/sample.svg) en el navegador:
     *(Nginx sirve el archivo directamente desde `/data/images/sample.svg` sin pasar por el puerto 8080)*

3. **Recargar la configuración sin reiniciar el contenedor:**
   Si modificas `nginx.conf`, puedes probar el comando de la guía oficial:
   ```powershell
   docker compose exec nginx nginx -s reload
   ```

4. **Detener el contenedor:**
   ```powershell
   docker compose down
   ```
