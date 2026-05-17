# API de Clasificacion

## Base URL

```text
http://127.0.0.1:8000
```

## Configuracion LLM

El backend usa `Gemini` como proveedor principal por defecto y conserva el proveedor legado compatible con OpenAI como alternativa.

Variables recomendadas en `.env`:

```env
LLM_PROVIDER=gemini
LLM_TIMEOUT=60

GEMINI_API_KEY=tu_key_google_ai_studio
GEMINI_MODEL=gemini-2.0-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Proveedor legado opcional
LLM_API_KEY=
LLM_MODEL=gpt-4.1-mini
LLM_BASE_URL=https://models.inference.ai.azure.com
```

Si `LLM_PROVIDER=gemini`, el backend consume la API nativa de Google AI Studio. Si la llamada falla o no hay clave configurada, el sistema mantiene el fallback local basado en puntajes del catalogo.

## Flujo de clasificacion jerarquica

El agente clasifica en **tres fases secuenciales** para evitar asignaciones incorrectas:

1. **Fase 1 - Area de Conocimiento**: El sistema puntua todas las areas y el LLM elige la mas adecuada.
2. **Fase 2 - Linea de Investigacion**: Solo se evaluan las lineas que pertenecen al area elegida. El LLM elige entre ellas.
3. **Fase 3 - Capacidades Estrategicas**: Se obtienen automaticamente desde el catalogo (sin LLM) a partir de la linea elegida.

## Endpoint de salud

### GET `/health`

Verifica que la API este levantada.

#### Respuesta `200`

```json
{
  "status": "ok"
}
```

## Endpoint de clasificacion

### POST `/clasificar`

Clasifica un documento en:

- area de conocimiento
- linea de investigacion (dentro del area)
- capacidades estrategicas (lookup automatico)

### Headers

```text
Content-Type: application/json
```

### Body

```json
{
  "resumen": "El presente trabajo analiza la ciberdefensa en la Fuerza Terrestre y sus limitaciones actuales.",
  "objetivo": "Proponer un sistema de gestion para mejorar la ciberdefensa en la Fuerza Terrestre.",
  "alcance": "La propuesta aplica al nivel tactico, operacional y su enlace con el nivel estrategico militar.",
  "propuesta": "Se propone un sistema de gestion de ciberdefensa con arquitectura de red, estructura organizacional y proceso de ciberdefensa."
}
```

### Respuesta `200`

```json
{
  "recomendada": {
    "linea_investigacion": "Ciberdefensa (ciberarmas, diseño operacional, hacking, hardening y juegos de guerra)",
    "area_conocimiento": "Ciberespacio",
    "capacidades_estrategicas": [
      "Mando y control",
      "Maniobra"
    ],
    "confianza": 0.89,
    "justificacion": "Area: ... | Linea: ..."
  },
  "candidatas": [
    {
      "linea_investigacion": "Ciberdefensa (ciberarmas, diseño operacional, hacking, hardening y juegos de guerra)",
      "area_conocimiento": "Ciberespacio",
      "capacidades_estrategicas": [
        "Mando y control",
        "Maniobra"
      ],
      "confianza": 0.89,
      "justificacion": "Area: ... | Linea: ..."
    },
    {
      "linea_investigacion": "Ciberseguridad (user behavior analytics, modelos de simulación en el ciberespacio, ...)",
      "area_conocimiento": "Ciberespacio",
      "capacidades_estrategicas": [
        "Mando y control",
        "Maniobra"
      ],
      "confianza": 0.78,
      "justificacion": "Candidata alternativa dentro de la misma area de conocimiento."
    }
  ],
  "evidencia_detectada": [
    "ciberdefensa",
    "gestion",
    "arquitectura",
    "red",
    "ciberseguridad"
  ],
  "texto_consolidado": "Resumen: ...\n\nObjetivo: ...\n\nAlcance: ...\n\nPropuesta: ..."
}
```

### Respuesta `400`

Cuando el body no es JSON valido:

```json
{
  "error": "El cuerpo de la solicitud debe ser JSON valido."
}
```

### Respuesta `422`

Cuando falta un campo obligatorio o llega vacio:

```json
{
  "error": "Solicitud invalida.",
  "details": [
    {
      "type": "missing",
      "loc": [
        "alcance"
      ],
      "msg": "Field required",
      "input": {
        "resumen": "...",
        "objetivo": "...",
        "propuesta": "..."
      }
    }
  ]
}
```

## Ejemplo con curl

```bash
curl -X POST "http://127.0.0.1:8000/clasificar" \
  -H "Content-Type: application/json" \
  -d '{
    "resumen": "Analiza la ciberdefensa en la Fuerza Terrestre.",
    "objetivo": "Proponer un sistema de gestion para mejorar la ciberdefensa.",
    "alcance": "Aplica a nivel tactico, operacional y estrategico.",
    "propuesta": "Incluye arquitectura de red, proceso y estructura organizacional."
  }'
```

## Ejemplo con PowerShell

```powershell
$body = @{
  resumen = "Analiza la ciberdefensa en la Fuerza Terrestre."
  objetivo = "Proponer un sistema de gestion para mejorar la ciberdefensa."
  alcance = "Aplica a nivel tactico, operacional y estrategico."
  propuesta = "Incluye arquitectura de red, proceso y estructura organizacional."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/clasificar" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```
