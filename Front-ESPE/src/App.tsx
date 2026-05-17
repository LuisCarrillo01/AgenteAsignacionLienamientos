
import { useState } from 'react';
import './App.css';
import { clasificarDocumento } from './services/iaService';
import type { ClassificationResponse } from './services/iaService';

function App() {
  const [resumen, setResumen] = useState('');
  const [objetivo, setObjetivo] = useState('');
  const [alcance, setAlcance] = useState('');
  const [propuesta, setPropuesta] = useState('');
  const [resultados, setResultados] = useState<null | ClassificationResponse>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResultados(null);
    setError(null);
    try {
      const res = await clasificarDocumento(resumen, objetivo, alcance, propuesta);
      setResultados(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error de conexión con el servicio de IA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="background-gradient"></div>
      <div className="app-container">
        <h1>Generador de Campos por IA</h1>
        <div className="info-box">
          <div style={{display:'flex',alignItems:'center',gap:'14px',marginBottom:'8px'}}>
            <span style={{fontSize:'2.1rem',color:'#1976d2'}}>💡</span>
            <h2 style={{margin:0, color:'#1976d2', fontWeight:700, fontSize:'1.25rem'}}>Optimiza tu gestión con IA</h2>
          </div>
          <p style={{margin:'0 0 6px 0', color:'#333', fontSize:'1.08rem'}}>
            Ingresa los detalles técnicos de tu proyecto.<br/>
            Nuestra IA analizará la información para sugerir la clasificación académica e institucional más adecuada.
          </p>
          <ul style={{margin:'10px 0 0 18px', color:'#1976d2', fontSize:'1.01rem',lineHeight:1.7}}>
            <li>Resultados inmediatos y personalizados</li>
            <li>Mejora la calidad y coherencia de tus entregables</li>
            <li>Reduce el tiempo de redacción y validación</li>
            <li>Clasificación basada en lineamientos vigentes</li>
            <li>Justificación técnica automática</li>
            <li>Sugerencia de capacidades estratégicas</li>
          </ul>
        </div>
        <form className="ia-form" onSubmit={handleSubmit}>
          <label>
            Resumen / Introducción
            <textarea
              value={resumen}
              onChange={e => setResumen(e.target.value)}
              required
              placeholder="Describe brevemente de qué trata el documento..."
            />
          </label>
          <label>
            Objetivo
            <textarea
              value={objetivo}
              onChange={e => setObjetivo(e.target.value)}
              required
              placeholder="¿Qué se busca lograr?"
            />
          </label>
          <label>
            Alcance
            <textarea
              value={alcance}
              onChange={e => setAlcance(e.target.value)}
              required
              placeholder="Describe el alcance..."
            />
          </label>
          <label>
            Propuesta
            <textarea
              value={propuesta}
              onChange={e => setPropuesta(e.target.value)}
              required
              placeholder="¿Cuál es la solución o propuesta técnica?"
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Procesando...' : 'Generar'}
          </button>
        </form>
        {error && <div className="error-message" style={{color: '#d32f2f', marginBottom: '20px'}}>⚠️ {error}</div>}

        {resultados && resultados.recomendada && (
          <div className="resultados-box">
            <h2 style={{color: '#2e7d32'}}>✔ Clasificación Sugerida</h2>
            <div><strong>Línea de Investigación:</strong> {resultados.recomendada.linea_investigacion}</div>
            <div><strong>Área de Conocimiento:</strong> {resultados.recomendada.area_conocimiento}</div>
            <div><strong>Capacidades Estratégicas:</strong> {resultados.recomendada.capacidades_estrategicas.join(', ')}</div>
            <div><strong>Confianza:</strong> {(resultados.recomendada.confianza * 100).toFixed(1)}%</div>
            <div style={{marginTop: '15px', padding: '10px', background: '#fff', borderRadius: '8px', border: '1px solid #e0e0e0'}}>
              <strong>Justificación:</strong>
              <p style={{fontSize: '0.95rem', fontStyle: 'italic', margin: '5px 0 0 0'}}>{resultados.recomendada.justificacion}</p>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
// ...existing code...
