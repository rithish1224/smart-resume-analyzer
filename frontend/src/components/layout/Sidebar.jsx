import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/analyze', label: 'Analyze', icon: '📊' },
    { path: '/compare', label: 'Compare', icon: '👥' },
    { path: '/admin', label: 'Admin', icon: '🛡️' },
    { path: '/about', label: 'About', icon: 'ℹ️' },
  ];

  return (
    <div className={`fixed left-0 top-0 h-full bg-[#111122]/90 backdrop-blur-xl border-r border-white/10 transition-all duration-300 z-50 flex flex-col ${isCollapsed ? 'w-20' : 'w-64'} hidden md:flex`}>
      {/* Header */}
      <div className="p-6 flex items-center justify-between border-b border-white/10">
        {!isCollapsed && (
          <h2 className="font-outfit font-bold text-xl text-transparent bg-clip-text bg-gradient-to-r from-[#6366f1] to-[#06b6d4] truncate">
            Smart Diagnostics
          </h2>
        )}
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2 rounded-lg hover:bg-white/10 text-gray-400 transition-colors"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `flex items-center gap-4 px-4 py-3 rounded-xl transition-all ${
                isActive 
                  ? 'bg-gradient-to-r from-[#6366f1]/20 to-[#8b5cf6]/20 text-white border border-[#6366f1]/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]' 
                  : 'text-gray-400 hover:bg-white/5 hover:text-white border border-transparent'
              }`
            }
          >
            <span className="text-xl">{item.icon}</span>
            {!isCollapsed && <span className="font-medium font-inter">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] flex items-center justify-center text-white font-bold shrink-0">
            JD
          </div>
          {!isCollapsed && (
            <div className="overflow-hidden">
              <p className="text-sm font-medium text-white truncate">Jane Doe</p>
              <p className="text-xs text-gray-500 truncate">jane@company.com</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
