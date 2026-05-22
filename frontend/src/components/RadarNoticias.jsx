import { useState } from 'react';
import axios from 'axios';
import { Newspaper, AlertTriangle, Users } from 'lucide-react';

const RadarNoticias = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchNoticias = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:8000/api/noticias/impacto');
      setData(res.data);
    } catch (error) {
      console.error(error);
      setData({ error: "No se pudo conectar con el servidor." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mt-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-50 rounded-lg">
            <Newspaper className="text-blue-600 w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Radar de Impacto Externo</h2>
            <p className="text-sm text-gray-500">Scrapeo en tiempo real de noticias para predecir mora en la sábana de créditos</p>
          </div>
        </div>
        <button 
          onClick={fetchNoticias}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-bold text-sm transition-all shadow-md hover:shadow-lg disabled:opacity-50"
        >
          {loading ? 'Analizando con Gemma...' : 'Escanear Noticias'}
        </button>
      </div>

      {!data && !loading && (
        <div className="text-center py-12 text-gray-400 border-2 border-dashed border-gray-100 rounded-xl">
          Haz clic en "Escanear Noticias" para evaluar el impacto de los titulares de hoy.
        </div>
      )}

      {loading && (
        <div className="text-center py-16">
           <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mb-4"></div>
           <p className="text-blue-600 font-semibold animate-pulse">Leyendo noticias y cruzando datos con Sábana de Créditos...</p>
        </div>
      )}

      {data && data.error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg font-semibold">
          Error: {data.error}
        </div>
      )}

      {data && !data.error && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-5 rounded-xl border border-blue-100">
            <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
              <BrainCircuit className="w-5 h-5" />
              Análisis Macro-Económico (Gemma 4)
            </h3>
            <p className="text-blue-800 text-sm leading-relaxed">{data.analisis_general}</p>
          </div>

          <div className="grid grid-cols-1 gap-6">
            {data.impactos?.map((impacto, idx) => (
              <div key={idx} className="border border-red-200 rounded-xl overflow-hidden shadow-sm">
                <div className="bg-gradient-to-r from-red-50 to-white p-5 border-b border-red-100 flex items-start gap-4">
                  <div className="p-2 bg-red-100 rounded-full shrink-0">
                    <AlertTriangle className="text-red-500 w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-red-900 text-lg uppercase tracking-wide">{impacto.actividad}</h4>
                    <p className="text-sm text-gray-700 mt-1">{impacto.razon}</p>
                    <div className="mt-3 text-xs font-bold bg-red-100 text-red-800 inline-block px-3 py-1 rounded-full border border-red-200">
                      {impacto.total_clientes} SOCIOS POTENCIALMENTE AFECTADOS
                    </div>
                  </div>
                </div>
                
                <div className="p-0 overflow-x-auto bg-white">
                  <table className="w-full text-left text-sm text-gray-600">
                    <thead className="bg-gray-50 text-gray-500 text-xs uppercase font-bold">
                      <tr>
                        <th className="px-6 py-4">Nro. Cliente</th>
                        <th className="px-6 py-4">Actividad Socio</th>
                        <th className="px-6 py-4 text-right">Ingresos Socio</th>
                        <th className="px-6 py-4 text-right">Egresos Socio</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {impacto.ejemplos_clientes?.map((cliente, i) => (
                        <tr key={i} className="hover:bg-red-50/50 transition-colors">
                          <td className="px-6 py-4 font-bold text-gray-900">Socio {cliente.nro_cliente}</td>
                          <td className="px-6 py-4">{cliente.actividad_socio}</td>
                          <td className="px-6 py-4 text-right text-green-600 font-bold">${cliente.ingresos_socio?.toLocaleString()}</td>
                          <td className="px-6 py-4 text-right text-red-500 font-bold">${cliente.egresos_socio?.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
            
            {(!data.impactos || data.impactos.length === 0) && (
              <div className="bg-green-50 text-green-700 p-5 rounded-xl flex items-center gap-3 font-semibold border border-green-200">
                <Users className="w-6 h-6" />
                Ningún segmento de clientes parece estar en riesgo inminente por las noticias actuales.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Pequeño workaround para BrainCircuit
const BrainCircuit = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M9 13a4.5 4.5 0 0 0 3-4"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M12 13h4"/><path d="M12 18h6a2 2 0 0 1 2 2v1"/><path d="M12 8h8"/><path d="M16 8V5a2 2 0 0 1 2-2"/><path d="M16 13v-2"/></svg>
);

export default RadarNoticias;
