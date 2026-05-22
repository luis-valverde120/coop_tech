import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import Socios from './components/Socios';
import Alertas from './components/Alertas';
import PerfilSocio from './components/PerfilSocio';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="socios" element={<Socios />} />
          <Route path="socios/:id" element={<PerfilSocio />} />
          <Route path="alertas" element={<Alertas />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
