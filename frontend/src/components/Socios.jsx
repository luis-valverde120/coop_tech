import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Socios = () => {
  const [socios, setSocios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtroRiesgo, setFiltroRiesgo] = useState('Todos');
  const [busqueda, setBusqueda] = useState('');

  const fetchSocios = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/socios?riesgo=${filtroRiesgo}&search=${busqueda}`);
      setSocios(res.data.data);
    } catch (error) {
      console.error("Error fetching socios", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSocios();
  }, [filtroRiesgo]);

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      fetchSocios();
    }
  };

  const tabs = ['Todos', 'Critico', 'Alto', 'Medio', 'Bajo'];

  const getBadgeStyle = (riesgo) => {
    switch(riesgo) {
      case 'Crítico': return 'bg-red-100 text-red-600 border-red-200';
      case 'Alto': return 'bg-orange-100 text-orange-600 border-orange-200';
      case 'Medio': return 'bg-yellow-100 text-yellow-600 border-yellow-200';
      case 'Bajo': return 'bg-green-100 text-green-600 border-green-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const getScoreColor = (riesgo) => {
    switch(riesgo) {
      case 'Crítico': return 'text-red-600';
      case 'Alto': return 'text-orange-600';
      case 'Medio': return 'text-yellow-600';
      case 'Bajo': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Socios</h1>
          <p className="text-gray-500 text-sm">Gestión y perfilamiento de socios</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
        {/* Header / Filtros */}
        <div className="p-4 border-b border-gray-100 flex flex-col md:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={16} className="text-gray-400" />
            </div>
            <input 
              type="text" 
              className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-coopverde focus:border-coopverde sm:text-sm"
              placeholder="Buscar por ID..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              onKeyDown={handleSearch}
            />
          </div>
          <div className="flex space-x-1">
            {tabs.map(tab => (
              <button
                key={tab}
                onClick={() => setFiltroRiesgo(tab)}
                className={`px-4 py-2 text-sm rounded-lg border transition-colors ${
                  filtroRiesgo === tab
                    ? 'border-coopverde text-coopverde bg-coopverdeclaro font-semibold'
                    : 'border-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Tabla */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100 text-xs uppercase tracking-wider text-gray-500">
                <th className="p-4 font-semibold">Socio</th>
                <th className="p-4 font-semibold">ID Cliente</th>
                <th className="p-4 font-semibold">Crédito</th>
                <th className="py-4 px-4 text-xs font-bold text-gray-400 tracking-wider">CRÉDITO</th>
                <th className="py-4 px-4 text-xs font-bold text-gray-400 tracking-wider">ESTADO</th>
                <th className="py-4 px-4 text-xs font-bold text-gray-400 tracking-wider">RIESGO</th>
                <th className="p-4 font-semibold text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="p-8 text-center text-gray-500">Cargando socios...</td>
                </tr>
              ) : socios.length === 0 ? (
                <tr>
                  <td colSpan="7" className="p-8 text-center text-gray-500">No se encontraron socios.</td>
                </tr>
              ) : (
                socios.map((socio) => (
                  <tr key={socio.id_cliente} className="hover:bg-gray-50 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                          socio.riesgo === 'Crítico' ? 'bg-cooprojo' : socio.riesgo === 'Alto' ? 'bg-orange-500' : 'bg-coopverde'
                        }`}>
                          {socio.iniciales}
                        </div>
                        <span className="font-semibold text-gray-800">Socio {socio.id_cliente}</span>
                      </div>
                    </td>
                    <td className="p-4 text-gray-500 text-sm">{socio.id_cliente}</td>
                    <td className="py-4 px-4 font-bold text-gray-800">
                    ${socio.credito.toLocaleString()}
                  </td>
                  <td className="py-4 px-4 text-coopverde font-medium text-sm">
                    Al día
                  </td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getBadgeStyle(socio.riesgo)}`}>
                        {socio.riesgo.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 bg-gray-200 h-1.5 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${getBadgeStyle(socio.riesgo).split(' ')[0]}`}
                            style={{ width: `${socio.score}%` }}
                          ></div>
                        </div>
                        <span className={`font-bold text-sm ${getScoreColor(socio.riesgo)}`}>{socio.score}</span>
                      </div>
                    </td>
                    <td className="p-4 text-right">
                      <Link 
                        to={`/socios/${socio.id_cliente}`}
                        className="text-coopverde font-semibold text-sm hover:underline flex items-center justify-end gap-1"
                      >
                        Ver &rarr;
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Socios;
