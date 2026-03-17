import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Header({ title }) {
    const navigate = useNavigate();
    const userEmail = localStorage.getItem("user") || "Utilisateur";
    const [showNotif, setShowNotif] = useState(false);
    const notifRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (notifRef.current && !notifRef.current.contains(e.target)) {
                setShowNotif(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
            <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">{title}</h2>
            </div>
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-4">
                    <div className="relative" ref={notifRef}>
                        <button onClick={() => setShowNotif(!showNotif)} className="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors relative">
                            <span className="material-symbols-outlined">notifications</span>
                            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-[#ed3500] ring-2 ring-white dark:ring-slate-900"></span>
                        </button>
                        {showNotif && (
                            <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 z-50 overflow-hidden">
                                <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                                    <h4 className="text-sm font-bold">Notifications</h4>
                                </div>
                                <div className="px-4 py-8 flex flex-col items-center justify-center text-slate-400">
                                    <span className="material-symbols-outlined text-3xl mb-2">notifications_off</span>
                                    <p className="text-sm">Pas de notification</p>
                                </div>
                            </div>
                        )}
                    </div>
                    <button 
                        onClick={() => navigate('/profile')}
                        className="flex items-center gap-3 px-2 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all group"
                    >
                        <div className="text-right hidden sm:block">
                            <p className="text-sm font-bold leading-none group-hover:text-primary transition-colors">{userEmail}</p>
                            <p className="text-xs text-slate-500 mt-1">Admin</p>
                        </div>
                        <img 
                            alt="Profil" 
                            className="h-9 w-9 rounded-full object-cover border-2 border-transparent group-hover:border-primary transition-all" 
                            src={`https://ui-avatars.com/api/?name=${encodeURIComponent(userEmail)}&background=093fb4&color=fff`} 
                        />
                    </button>
                </div>
            </div>
        </header>
    );
}
