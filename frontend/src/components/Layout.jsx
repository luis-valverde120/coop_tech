import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, Bell, LogOut } from 'lucide-react';

const Layout = () => {
  const location = useLocation();
  
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Socios', path: '/socios', icon: Users },
    { name: 'Alertas', path: '/alertas', icon: Bell, badge: true },
  ];

  return (
    <div className="flex h-screen bg-coopgris">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-coopverde flex items-center justify-center text-white font-bold">
            C
          </div>
          <span className="font-bold text-gray-800 tracking-tight text-lg leading-tight">
            <span className="text-coopnaranja">TULCÁN</span> LTDA.
          </span>
        </div>
        
        <nav className="flex-1 px-4 mt-6 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            
            return (
              <NavLink
                key={item.name}
                to={item.path}
                className={`flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-coopverdeclaro text-coopverde font-semibold' 
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon size={20} className={isActive ? 'text-coopverde' : 'text-gray-400'} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                    6
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
        
        <div className="p-4 border-t border-gray-200">
          <div className="mb-4 px-4">
            <p className="text-sm font-semibold text-gray-800">Administrador</p>
            <p className="text-xs text-gray-500">Gerencia</p>
          </div>
          <button className="flex items-center gap-3 px-4 py-2 text-gray-500 hover:text-gray-800 w-full transition-colors text-sm">
            <LogOut size={18} />
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
