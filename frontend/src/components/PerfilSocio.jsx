import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, BrainCircuit } from 'lucide-react';
import { BarChart, Bar, XAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import axios from 'axios';

const PerfilSocio = () => {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [analisis, setAnalisis] = useState('');
  const [cargandoAnalisis, setCargandoAnalisis] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/socios/${id}`);
        setData(res.data);
      } catch (error) {
        console.error("Error fetching socio", error);
      }
    };
    fetchData();
  }, [id]);

  const handleAnalisis = async () => {
    setCargandoAnalisis(true);
    try {
      const res = await axios.post(`http://localhost:8000/api/socios/${id}/analisis`);
      setAnalisis(res.data.analisis);
    } catch (error) {
      setAnalisis("No se pudo obtener el análisis en este momento.");
    } finally {
      setCargandoAnalisis(false);
    }
  };

  if (!data) return <div className="p-8">Cargando perfil...</div>;

  const isRisk = data.estado === 'Crítico' || data.estado === 'Alto';

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Perfil del Socio</h1>
          <p className="text-gray-500 text-sm">Análisis detallado de comportamiento</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 relative">
        <Link to="/socios" className="absolute top-6 left-6 text-gray-500 hover:text-gray-800 flex items-center gap-1 text-sm">
          <ArrowLeft size={16} /> Volver
        </Link>
        
        <div className="absolute top-6 right-6">
          <span className={`px-4 py-1 rounded-full text-xs font-bold border ${isRisk ? 'bg-red-100 text-red-600 border-red-200' : 'bg-green-100 text-green-600 border-green-200'}`}>
            {data.estado.toUpperCase()}
          </span>
        </div>

        <div className="mt-12 flex justify-between items-end">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white ${isRisk ? 'bg-cooprojo' : 'bg-coopverde'}`}>
              {data.iniciales}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Socio {data.id_cliente}</h2>
              <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                <span>ID: {data.id_cliente}</span>
                <span>Ingresos: ${data.ingresos}</span>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`text-6xl font-black ${isRisk ? 'text-red-500' : 'text-green-500'}`}>
              {data.score}
            </div>
            <div className="text-sm font-semibold text-gray-500 uppercase tracking-widest mt-1">
              Score de riesgo
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Crédito</p>
          <p className="text-2xl font-bold text-coopverde">${data.credito.toLocaleString()}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Saldo Pendiente</p>
          <p className="text-2xl font-bold text-coopnaranja">${data.saldo_pendiente.toLocaleString()}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Ingresos</p>
          <p className="text-2xl font-bold text-green-500">${data.ingresos.toLocaleString()}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Egresos</p>
          <p className="text-2xl font-bold text-red-500">${data.egresos.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-lg flex flex-col relative overflow-hidden">
          {/* Un toque de color sutil en la parte superior para que se vea premium */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-coopverde to-green-300"></div>
          
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-green-50 rounded-lg">
              <BrainCircuit className="text-coopverde w-6 h-6" />
            </div>
            <h3 className="font-extrabold text-2xl text-gray-900 tracking-tight">Análisis Detallado de IA</h3>
          </div>
          
          <div className="mb-8 flex-1 overflow-y-auto max-h-[500px] pr-4 custom-scrollbar">
            {analisis ? (
              <div className="prose prose-green prose-lg max-w-none text-gray-700">
                {analisis.split('\n').map((line, idx) => {
                  if (!line.trim()) return <br key={idx} />;
                  
                  if (line.startsWith('### ')) return <h3 key={idx} className="text-lg font-bold text-gray-900 mt-5 mb-2">{line.replace('### ', '')}</h3>;
                  if (line.startsWith('## ')) return <h2 key={idx} className="text-xl font-bold text-gray-900 mt-6 mb-3">{line.replace('## ', '')}</h2>;
                  if (line.startsWith('# ')) return <h1 key={idx} className="text-2xl font-extrabold text-gray-900 mt-8 mb-4">{line.replace('# ', '')}</h1>;
                  
                  const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g);
                  const formattedLine = parts.map((part, i) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                      return <strong key={i} className="font-bold text-gray-900">{part.slice(2, -2)}</strong>;
                    }
                    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
                      return <em key={i} className="italic text-gray-800">{part.slice(1, -1)}</em>;
                    }
                    return part;
                  });

                  if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                    return <li key={idx} className="ml-6 list-disc my-1">{formattedLine}</li>;
                  }
                  
                  return <p key={idx} className="my-2">{formattedLine}</p>;
                })}
              </div>
            ) : (
              <div className="text-gray-500 italic prose prose-lg">
                Genera un análisis cognitivo profundo del riesgo basado en el comportamiento financiero del socio. <br/><br/>
                El reporte incluirá un diagnóstico, hipótesis de mora y recomendaciones de acción inmediata utilizando Gemma 4.
              </div>
            )}
          </div>
          <button 
            onClick={handleAnalisis}
            disabled={cargandoAnalisis}
            className="w-full sm:w-auto self-start bg-coopverde hover:bg-green-600 text-white font-bold py-3 px-8 rounded-xl shadow-md transition-all hover:shadow-lg flex items-center justify-center gap-2"
          >
            {cargandoAnalisis ? 'Generando análisis exhaustivo...' : 'Generar Análisis'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PerfilSocio;
