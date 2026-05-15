// src/services/iaService.ts
// Servicio para comunicación con el API de IA

// Interfaces basadas en el backend
export interface CandidateResult {
  linea_investigacion: string;
  area_conocimiento: string;
  capacidades_estrategicas: string[];
  confianza: number;
  justificacion: string;
}

export interface ClassificationResponse {
  recomendada: CandidateResult;
  candidatas: CandidateResult[];
  evidencia_detectada: string[];
  texto_consolidado: string;
}

// Cambia la URL según dónde corra tu backend
const API_URL = "http://localhost:8000/clasificar";

export async function clasificarDocumento(
  resumen: string,
  objetivo: string,
  alcance: string,
  propuesta: string
): Promise<ClassificationResponse> {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ resumen, objetivo, alcance, propuesta }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.error || "Error al comunicarse con el backend");
  }
  return response.json();
}
