import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, AlertTriangle, TrendingUp, CheckCircle, DollarSign, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/dashboard/kpis');
        setData(res.data);
      } catch (error) {
        console.error("Error fetching KPIs", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !data) {
    return <div className="p-8">Cargando...</div>;
  }

  const COLORS = ['#008A4B', '#F59E0B', '#EF4444', '#B91C1C'];
  const pieData = [
    { name: 'Bajo', value: data.distribucion_riesgo.Bajo },
    { name: 'Medio', value: data.distribucion_riesgo.Medio },
    { name: 'Alto', value: data.distribucion_riesgo.Alto },
    { name: 'Crítico', value: data.distribucion_riesgo.Critico },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm">Resumen general del sistema</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Créditos Activos</p>
            <Users size={16} className="text-coopverde" />
          </div>
          <h3 className="text-3xl font-black text-gray-900">{data.creditos_activos}</h3>
          <p className="text-xs text-gray-500 mt-2">Total de socios con crédito</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-red-100 shadow-sm shadow-red-50 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">En Mora</p>
            <AlertTriangle size={16} className="text-red-500" />
          </div>
          <h3 className="text-3xl font-black text-red-500">{data.en_mora}</h3>
          <p className="text-xs text-gray-500 mt-2">{data.porcentaje_mora}% del portafolio</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">En Riesgo</p>
            <TrendingUp size={16} className="text-coopnaranja" />
          </div>
          <h3 className="text-3xl font-black text-gray-900">{data.en_riesgo}</h3>
          <p className="text-xs text-gray-500 mt-2">Señales de alerta detectadas</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Recuperados</p>
            <CheckCircle size={16} className="text-coopverde" />
          </div>
          <h3 className="text-3xl font-black text-gray-900">{data.recuperados}</h3>
          <p className="text-xs text-gray-500 mt-2">Este mes</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Portafolio</p>
            <DollarSign size={16} className="text-coopverde" />
          </div>
          <h3 className="text-3xl font-black text-gray-900">{data.portafolio}</h3>
          <p className="text-xs text-gray-500 mt-2">Total cartera activa</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h3 className="text-sm font-bold text-gray-800 mb-6">Tendencia de Mora (%)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.tendencia_mora} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorMora" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="mes" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
                <Tooltip />
                <Area type="monotone" dataKey="valor" stroke="#EF4444" strokeWidth={3} fillOpacity={1} fill="url(#colorMora)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h3 className="text-sm font-bold text-gray-800 mb-2">Distribución de Riesgo</h3>
          <div className="h-48 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
            {pieData.map((item, i) => (
              <div key={i} className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i] }}></div>
                  <span className="text-gray-600">{item.name}</span>
                </div>
                <span className="font-bold text-gray-800">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Footer shortcut to Socios */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex justify-between items-center">
        <h3 className="text-sm font-bold text-gray-800">Socios con Mayor Riesgo</h3>
        <Link to="/socios" className="text-sm font-semibold text-coopverde flex items-center gap-1 hover:underline">
          Ver todos <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
