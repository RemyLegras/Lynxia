import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import logo from '../assets/logo.png';

export default function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    
    const [showSettings, setShowSettings] = useState(false);
    const [isDark, setIsDark] = useState(document.documentElement.classList.contains('dark'));
    const settingsRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (settingsRef.current && !settingsRef.current.contains(e.target)) {
                setShowSettings(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const toggleDarkMode = () => {
        const newDark = !isDark;
        setIsDark(newDark);
        if (newDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/");
    };

    const navItems = [
        { path: '/dashboard', icon: 'dashboard', label: 'Tableau de bord' },
        { path: '/upload', icon: 'upload_file', label: 'Importer' }
    ];

    return (
        <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col fixed h-full z-20">
            <div className="p-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg overflow-hidden flex items-center justify-center bg-white cursor-pointer" onClick={() => navigate('/dashboard')}>
                    <img src={logo} alt="Logo" className="w-full h-full object-contain" />
                </div>
                <div className="flex flex-col">
                    <h1 className="text-slate-900 dark:text-white text-base font-bold leading-none">LynxIA</h1>
                </div>
            </div>

            <nav className="flex-1 px-4 py-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                                isActive 
                                    ? 'bg-[#093fb4]/10 text-[#093fb4]' 
                                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                            }`}
                        >
                            <span className={`material-symbols-outlined text-[20px] ${isActive ? 'fill-1' : ''}`}>{item.icon}</span>
                            <span className={`text-sm ${isActive ? 'font-semibold' : 'font-medium'}`}>{item.label}</span>
                        </button>
                    );
                })}
            </nav>

            <div className="px-4 py-4 border-t border-slate-200 dark:border-slate-800 space-y-1 relative">
                <div ref={settingsRef}>
                    <button 
                        onClick={() => setShowSettings(!showSettings)}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${showSettings ? 'bg-slate-100 dark:bg-slate-800 text-primary' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                    >
                        <span className="material-symbols-outlined text-[20px]">settings</span>
                        <span className="text-sm font-medium">Paramètres</span>
                    </button>
                    
                    {showSettings && (
                        <div className="absolute bottom-full left-4 mb-2 w-56 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 p-2 z-50">
                            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 mb-1">
                                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Préférences</p>
                            </div>
                            <div className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group">
                                <div className="flex items-center gap-3">
                                    <span className="material-symbols-outlined text-sm text-slate-400 group-hover:text-primary transition-colors">
                                        {isDark ? 'dark_mode' : 'light_mode'}
                                    </span>
                                    <span className="text-xs font-medium">Mode sombre</span>
                                </div>
                                <button 
                                    onClick={toggleDarkMode}
                                    className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${isDark ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                                >
                                    <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${isDark ? 'translate-x-5' : 'translate-x-1'}`} />
                                </button>
                            </div>
                        </div>
                    )}
                </div>
                
                <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ed3500] hover:bg-[#ed3500]/5 dark:hover:bg-[#ed3500]/10 transition-colors"
                >
                    <span className="material-symbols-outlined text-[20px]">logout</span>
                    <span className="text-sm font-medium">Déconnexion</span>
                </button>
            </div>
        </aside>
    );
}
