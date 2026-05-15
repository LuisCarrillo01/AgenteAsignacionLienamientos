# Despliegue en Dokploy

Este proyecto queda preparado para desplegar frontend y backend con Docker Compose.

## 1. Subir el repositorio

Sube este repositorio a GitHub, GitLab o el proveedor Git que uses.

## 2. Crear el proyecto en Dokploy

1. En Dokploy crea un proyecto nuevo.
2. Agrega una aplicacion de tipo **Docker Compose**.
3. Conecta el repositorio.
4. Usa `docker-compose.yml` como archivo compose.
5. Despliega.

## 3. Dominio

En la aplicacion Docker Compose, agrega el dominio al servicio `frontend` usando el puerto interno `80`.

El backend no necesita dominio publico: Nginx reenvia las rutas `/clasificar` y `/health` al servicio interno `backend:8000`.

## 4. Variables de entorno

Si quieres usar el LLM, configura estas variables en Dokploy:

```env
LLM_API_KEY=tu_api_key
LLM_PROVIDER=github
LLM_BASE_URL=https://models.inference.ai.azure.com
LLM_MODEL=gpt-4.1-mini
LLM_TIMEOUT=60
```

Si no configuras `LLM_API_KEY`, el backend conserva el fallback de scoring local.

## 5. Verificacion

Cuando termine el despliegue:

- Abre `https://tu-dominio.com/health`; debe responder `{"status":"ok"}`.
- Abre `https://tu-dominio.com` y prueba el formulario.

## Nota

Dokploy recomienda enrutar con su panel de dominios y usar `expose` en Compose, no `ports`, para que Traefik gestione el acceso publico.
