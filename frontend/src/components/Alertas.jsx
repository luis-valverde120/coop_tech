import { useState, useEffect } from 'react';
import { Mail, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Alertas = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('pantojacarlos2003@gmail.com');

  useEffect(() => {
    const fetchAlertas = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/alertas');
        setData(res.data);
      } catch (error) {
        console.error("Error fetching alertas", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAlertas();
  }, []);

  const handleDescartar = (id) => {
    if(data) {
      setData({
        ...data,
        alertas: data.alertas.filter(a => a.id !== id)
      });
    }
  };

  if (loading || !data) return <div className="p-8">Cargando alertas...</div>;

  const getAlertIcon = (tipo) => {
    if (tipo === 'Crítico') return <AlertCircle className="text-red-500" size={24} />;
    if (tipo === 'Alto') return <AlertTriangle className="text-orange-500" size={24} />;
    return <Info className="text-yellow-500" size={24} />;
  };

  const getAlertColor = (tipo) => {
    if (tipo === 'Crítico') return 'bg-red-50 border-red-100';
    if (tipo === 'Alto') return 'bg-orange-50 border-orange-100';
    return 'bg-yellow-50 border-yellow-100';
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alertas</h1>
          <p className="text-gray-500 text-sm">Notificaciones de riesgo activas</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center gap-3">
        <Mail size={18} className="text-coopverde" />
        <span className="text-sm text-gray-600">Notificaciones a:</span>
        <input 
          type="email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="flex-1 outline-none text-sm font-medium text-gray-800"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex justify-between items-center">
          <span className="text-gray-500 text-sm font-semibold">Críticas</span>
          <span className="text-xl font-black text-red-500">{data.criticas}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex justify-between items-center">
          <span className="text-gray-500 text-sm font-semibold">Altas</span>
          <span className="text-xl font-black text-orange-500">{data.altas}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex justify-between items-center">
          <span className="text-gray-500 text-sm font-semibold">Medias</span>
          <span className="text-xl font-black text-yellow-500">{data.medias}</span>
        </div>
      </div>

      <div className="space-y-4 mt-6">
        {data.alertas.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No hay alertas activas en este momento.</p>
        ) : (
          data.alertas.map(alerta => (
            <div key={alerta.id} className={`p-4 rounded-xl border ${getAlertColor(alerta.tipo)} flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 transition-all hover:shadow-md`}>
              <div className="flex gap-4">
                <div className="mt-1">{getAlertIcon(alerta.tipo)}</div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-gray-900">Socio {alerta.id_cliente}</h3>
                    <span className={`text-[10px] uppercase font-bold tracking-wider ${
                      alerta.tipo === 'Crítico' ? 'text-red-500' : 'text-orange-500'
                    }`}>
                      {alerta.tipo}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{alerta.motivo}</p>
                  <p className="text-xs text-gray-500 mt-1">{alerta.fecha} &middot; Cuota: ${alerta.cuota}</p>
                </div>
              </div>
              <div className="flex gap-2 w-full sm:w-auto mt-4 sm:mt-0">
                <button className="flex-1 sm:flex-none px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-semibold hover:bg-red-50 transition-colors flex items-center justify-center gap-2">
                  <Mail size={14} /> Notificar
                </button>
                <Link to={`/socios/${alerta.id_cliente}`} className="flex-1 sm:flex-none px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-semibold hover:bg-white transition-colors text-center">
                  Ver socio
                </Link>
                <button 
                  onClick={() => handleDescartar(alerta.id)}
                  className="flex-1 sm:flex-none px-4 py-2 border border-transparent text-gray-500 hover:text-gray-800 rounded-lg text-sm font-semibold transition-colors"
                >
                  Descartar
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Alertas;
