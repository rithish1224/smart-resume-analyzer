import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useProvider } from '../../context/ProviderContext';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const providerContext = useProvider();
  const navigate = useNavigate();
  const location = useLocation();

  const activeProvider = providerContext?.activeProvider || 'OpenAI';
  const primaryProvider = providerContext?.primaryProvider || 'openai';

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (e) {
      console.error('Logout error', e);
    }
  };

  const isRecruiterOrAdmin = user && ['recruiter', 'admin'].includes(user.role?.toLowerCase());

  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 100, damping: 20 }}
      className="fixed w-full z-50 bg-[#0a0a1a]/80 backdrop-blur-xl border-b border-white/10"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🧠</span>
            <span className="text-xl font-outfit font-bold bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 text-transparent bg-clip-text">
              SmartCD
            </span>
          </Link>

          <div className="hidden md:flex items-center space-x-8">
            <NavLink to="/">Home</NavLink>
            <NavLink to="/analyze">Analyze</NavLink>
            <NavLink to="/compare">Compare</NavLink>
            {isRecruiterOrAdmin && (
              <NavLink to="/admin">Admin</NavLink>
            )}
            <NavLink to="/about">About</NavLink>
          </div>

          <div className="hidden md:flex items-center gap-6">
            {activeProvider && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-gray-300">
                <span className={`w-2 h-2 rounded-full ${primaryProvider === 'openrouter' ? 'bg-green-500' : 'bg-indigo-400'}`} />
                AI: {activeProvider}
              </div>
            )}
            
            {isAuthenticated && user ? (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
                    {(user.name || user.full_name || user.email || 'U').charAt(0).toUpperCase()}
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-medium text-white">{user.name || user.full_name || user.email}</span>
                    <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-semibold bg-indigo-500/10 px-1.5 rounded w-fit">
                      {user.role}
                    </span>
                  </div>
                </div>
                <button 
                  onClick={handleLogout}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login" className="text-gray-300 hover:text-white font-medium text-xs px-3 py-1.5 transition-colors">
                  Login
                </Link>
                <Link to="/register" className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium text-xs transition-all shadow-md">
                  Register
                </Link>
              </div>
            )}
          </div>
          
          <div className="md:hidden flex items-center">
             <button onClick={() => setIsOpen(!isOpen)} className="text-gray-300 hover:text-white p-2">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {isOpen ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /> : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
                </svg>
             </button>
          </div>
        </div>
      </div>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#0a0a1a]/95 border-b border-white/10"
          >
             <div className="px-4 pt-2 pb-4 space-y-2">
               <MobileNavLink to="/" setIsOpen={setIsOpen}>Home</MobileNavLink>
               <MobileNavLink to="/analyze" setIsOpen={setIsOpen}>Analyze</MobileNavLink>
               <MobileNavLink to="/compare" setIsOpen={setIsOpen}>Compare</MobileNavLink>
               {isRecruiterOrAdmin && (
                 <MobileNavLink to="/admin" setIsOpen={setIsOpen}>Admin</MobileNavLink>
               )}
               <MobileNavLink to="/about" setIsOpen={setIsOpen}>About</MobileNavLink>
               
               <div className="pt-4 border-t border-white/10 flex flex-col gap-2">
                 {isAuthenticated ? (
                   <button onClick={() => { setIsOpen(false); handleLogout(); }} className="w-full text-left py-2 text-sm text-red-400">
                     Logout ({user?.name || user?.email})
                   </button>
                 ) : (
                   <div className="flex gap-2">
                     <Link to="/login" onClick={() => setIsOpen(false)} className="flex-1 text-center py-2 bg-white/10 rounded-lg text-xs">Login</Link>
                     <Link to="/register" onClick={() => setIsOpen(false)} className="flex-1 text-center py-2 bg-indigo-600 rounded-lg text-xs">Register</Link>
                   </div>
                 )}
               </div>
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

const NavLink = ({ to, children }) => (
  <Link
    to={to}
    className="text-gray-300 hover:text-white font-medium text-sm transition-colors"
  >
    {children}
  </Link>
);

const MobileNavLink = ({ to, children, setIsOpen }) => (
  <Link
    to={to}
    onClick={() => setIsOpen(false)}
    className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-white/5"
  >
    {children}
  </Link>
);

export default Navbar;
