# Sistema de Clasificación de Documentos Militares

Sistema de gestión y clasificación de documentos de investigación militar utilizando IA para asignar líneas de investigación, áreas de conocimiento y capacidades estratégicas basado en el catálogo del Anexo C.

## Arquitectura

- **Backend**: API Flask con Python + LangGraph para orquestación de workflow de clasificación
- **Frontend**: React + TypeScript + Vite para interfaz de usuario
- **LLM**: GPT-4.1-mini vía GitHub Models (opcional, con fallback a scoring local)

## Requisitos Previos

### Backend
- Python 3.8+
- pip

### Frontend
- Node.js 18+
- npm

## Instalación y Ejecución

### Backend

1. **Navegar al directorio del backend**
```bash
cd AgenteAsignacionLienamientos/BackEnd
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno (opcional)**
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env si necesitas configurar el LLM
# Por defecto funciona sin API key usando scoring local
```

6. **Iniciar el servidor**
```bash
python app/main.py
```

El backend correrá en: `http://127.0.0.1:8000`

### Frontend

1. **Navegar al directorio del frontend**
```bash
cd Front-ESPE
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Iniciar el servidor de desarrollo**
```bash
npm run dev
```

El frontend correrá en: `http://localhost:5173` (o el puerto que asigne Vite)

## Uso

1. Abre el navegador en la URL del frontend (ej: `http://localhost:5173`)
2. Completa los 4 campos del formulario:
   - **Resumen/Introducción**: Descripción breve del documento
   - **Objetivo**: Qué se busca lograr
   - **Alcance**: Ámbito de aplicación
   - **Propuesta**: Solución o propuesta técnica
3. Haz clic en "Generar"
4. El sistema mostrará:
   - Clasificación recomendada con línea de investigación, área de conocimiento y capacidades estratégicas
   - Justificación técnica
   - Otras candidatas alternativas
   - Evidencia detectada en el texto

## Ejemplo de Prueba

**Resumen/Introducción:**
```
El presente trabajo de investigación analiza la situación actual de la ciberdefensa en la Fuerza Terrestre. Se inicia con el planteamiento del problema y objetivos de investigación, desarrollando una revisión bibliográfica respecto al ciberespacio y la ciberdefensa en el contexto militar.
```

**Objetivo:**
```
Proponer un sistema de gestión para mejorar la ciberdefensa en la Fuerza Terrestre.
```

**Alcance:**
```
El alcance plantea un sistema de gestión de ciberdefensa transversal, considerando la estructura de la Fuerza Terrestre a nivel táctico y operacional, el cual se enlaza con su escalón técnico superior constituido por el COCIBER del CCFFAA como el nivel estratégico militar.
```

**Propuesta:**
```
Se propone un sistema de gestión de ciberdefensa compuesto por: conceptualizaciones internas, fundamentos, estructura organizacional, arquitectura de la red de información de la Fuerza Terrestre, y un proceso de ciberdefensa.
```

## Endpoints del Backend

### GET `/health`
Verifica que la API esté levantada.

**Respuesta:**
```json
{
  "status": "ok"
}
```

### POST `/clasificar`
Clasifica un documento en línea de investigación, área de conocimiento y capacidades estratégicas.

**Body:**
```json
{
  "resumen": "Texto del resumen...",
  "objetivo": "Texto del objetivo...",
  "alcance": "Texto del alcance...",
  "propuesta": "Texto de la propuesta..."
}
```

**Respuesta:**
```json
{
  "recomendada": {
    "linea_investigacion": "Ciberdefensa (ciberarmas, diseño operacional, hacking, hardening y juegos de guerra)",
    "area_conocimiento": "Ciberespacio",
    "capacidades_estrategicas": ["Mando y control", "Maniobra"],
    "confianza": 0.99,
    "justificacion": "Selección automática basada en el mayor puntaje local del catálogo."
  },
  "candidatas": [...],
  "evidencia_detectada": ["ciberdefensa", "proponer", "gestion", ...],
  "texto_consolidado": "Resumen: ...\n\nObjetivo: ...\n\nAlcance: ...\n\nPropuesta: ..."
}
```

## Estructura del Proyecto

```
Gestion/
├── AgenteAsignacionLienamientos/
│   └── BackEnd/
│       ├── app/
│       │   ├── api/          # Rutas de la API
│       │   ├── core/         # Configuración
│       │   ├── graph/        # Workflow de LangGraph
│       │   ├── models/       # Esquemas Pydantic
│       │   └── services/     # Servicios de negocio
│       ├── requirements.txt
│       └── main.py
└── Front-ESPE/
    ├── src/
    │   ├── services/         # Servicio de comunicación con backend
    │   ├── App.tsx           # Componente principal
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

## Configuración del LLM (Opcional)

El sistema funciona sin API key usando scoring local. Si deseas usar el LLM para mejores resultados:

1. Edita `BackEnd/app/.env`
2. Configura las siguientes variables:
```env
LLM_API_KEY=tu_api_key_aqui
LLM_BASE_URL=https://models.inference.ai.azure.com
LLM_MODEL=gpt-4.1-mini
```

## Solución de Problemas

### Error de conexión CORS
- Verifica que el backend esté corriendo
- Verifica que la URL en `Front-ESPE/src/services/iaService.ts` sea correcta (localhost:8000)

### Error 404 al llamar al endpoint
- Verifica que el backend esté corriendo en el puerto 8000
- Revisa los logs del backend para ver si hay errores

### El frontend no muestra resultados
- Abre la consola del navegador (F12) para ver errores
- Verifica que el backend esté respondiendo correctamente
- Revisa la pestaña Network para ver la respuesta del backend
