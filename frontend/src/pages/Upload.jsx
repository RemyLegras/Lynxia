import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';

export default function Upload() {
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

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="font-display bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 flex min-h-screen">
      {/* Side Navigation */}
      <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col fixed h-full z-20">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg overflow-hidden flex items-center justify-center bg-white">
            <img src={logo} alt="Logo" className="w-full h-full object-contain" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-slate-900 dark:text-white text-base font-bold leading-none">LynxIA</h1>
          </div>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          <button onClick={() => navigate('/dashboard')} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span className="material-symbols-outlined text-[20px]">dashboard</span>
            <span className="text-sm font-medium">Tableau de bord</span>
          </button>
          <a className="flex items-center gap-3 px-3 py-2 rounded-lg bg-[#093fb4]/10 text-[#093fb4]" href="#">
            <span className="material-symbols-outlined text-[20px] fill-1">upload_file</span>
            <span className="text-sm font-semibold">Importer</span>
          </a>
        </nav>

        <div className="px-4 py-4 border-t border-slate-200 dark:border-slate-800 space-y-1">
          <a className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" href="#">
            <span className="material-symbols-outlined text-[20px]">settings</span>
            <span className="text-sm font-medium">Paramètres</span>
          </a>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ed3500] hover:bg-[#ed3500]/5 dark:hover:bg-[#ed3500]/10 transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">logout</span>
            <span className="text-sm font-medium">Déconnexion</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 min-h-screen">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Importer</h2>
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
              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-bold leading-none">{userEmail}</p>
                  <p className="text-xs text-slate-500 mt-1">Admin</p>
                </div>
                <img alt="Profil" className="h-9 w-9 rounded-full object-cover" src={`https://ui-avatars.com/api/?name=${encodeURIComponent(userEmail)}&background=093fb4&color=fff`} />
              </div>
            </div>
          </div>
        </header>

        {/* Upload Body */}
        <div className="p-8">
          <div className="space-y-6 max-w-7xl mx-auto">
            <div className="flex flex-col gap-1">
              <h2 className="text-2xl font-bold tracking-tight">Nouveau scan</h2>
            </div>
            <div className="w-full">
              <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-primary/30 bg-white dark:bg-slate-900/50 px-6 py-10 transition-all hover:border-primary/50 group cursor-pointer">
                <div className="bg-primary/10 rounded-full p-4 mb-3 group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-primary text-3xl">upload_file</span>
                </div>
                <h3 className="text-lg font-bold mb-4">Importer un document</h3>
                <button className="flex items-center justify-center rounded-lg h-10 px-8 bg-primary text-white font-bold transition-all hover:bg-primary/90 shadow-md">
                  Sélectionner un fichier
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              <div className="xl:col-span-7 bg-white dark:bg-slate-900 rounded-xl border border-primary/10 shadow-sm overflow-hidden flex flex-col">
                <div className="px-4 py-3 border-b border-primary/10 flex justify-between items-center bg-slate-50 dark:bg-slate-800/50">
                  <h3 className="font-semibold text-sm flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-lg">visibility</span>
                    Aperçu
                  </h3>
                  <div className="flex gap-2">
                    <button className="p-1 hover:bg-primary/10 rounded text-slate-500 transition-colors">
                      <span className="material-symbols-outlined text-lg">zoom_in</span>
                    </button>
                    <button className="p-1 hover:bg-primary/10 rounded text-slate-500 transition-colors">
                      <span className="material-symbols-outlined text-lg">rotate_right</span>
                    </button>
                  </div>
                </div>
                <div className="p-6 flex-1 flex items-center justify-center bg-slate-100 dark:bg-slate-950/50 min-h-[400px]">
                  <div className="relative w-full max-w-md aspect-[1.6/1] bg-white dark:bg-slate-800 rounded shadow-xl overflow-hidden border border-slate-300 dark:border-slate-700">
                    <div className="absolute inset-0 bg-slate-200 dark:bg-slate-700/50 opacity-20" style={{backgroundImage: "radial-gradient(#1152d4 0.5px, transparent 0.5px)", backgroundSize: "10px 10px"}}></div>
                    <div className="absolute top-4 left-4 w-16 h-16 bg-primary/20 border-2 border-primary rounded-lg flex items-center justify-center">
                      <span className="material-symbols-outlined text-primary/50 text-3xl">account_circle</span>
                    </div>
                    <div className="absolute top-4 left-24 right-4 space-y-2">
                      <div className="h-4 bg-primary/10 rounded w-3/4 border border-primary/30 relative overflow-hidden">
                        <div className="absolute inset-0 bg-primary/5 animate-pulse"></div>
                      </div>
                      <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
                      <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/3"></div>
                    </div>
                    <div className="absolute bottom-4 left-4 right-4 grid grid-cols-2 gap-4">
                      <div className="h-8 bg-primary/10 border border-primary/30 rounded"></div>
                      <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded"></div>
                    </div>
                    <div className="absolute top-[22px] left-[94px] w-[150px] h-[20px] ring-2 ring-primary ring-offset-2 ring-offset-white dark:ring-offset-slate-800 rounded-sm"></div>
                    <div className="absolute bottom-[14px] left-[14px] w-[185px] h-[36px] ring-2 ring-primary ring-offset-2 ring-offset-white dark:ring-offset-slate-800 rounded-sm"></div>
                  </div>
                </div>
              </div>
              <div className="xl:col-span-5 flex flex-col gap-6">
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-primary/10 shadow-sm p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-semibold text-lg">Résultats</h3>
                    <div className="flex gap-2">
                      <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                        <span className="material-symbols-outlined text-xs">verified</span>
                        Valide
                      </span>
                      <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-red-100 text-[#ed3500] dark:bg-red-900/30">
                        <span className="material-symbols-outlined text-xs">warning</span>
                        Alerte
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-primary/5 border border-primary/10 mb-6">
                    <div className="relative size-16">
                      <svg className="size-16 -rotate-90">
                        <circle className="text-slate-200 dark:text-slate-700" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeWidth="6"></circle>
                        <circle className="text-primary" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeDasharray="175.84" strokeDashoffset="8.79" strokeLinecap="round" strokeWidth="6"></circle>
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-lg font-bold text-primary">95%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-lg font-bold leading-tight">Authentique</p>
                      <p className="text-xs text-slate-500 mt-0.5">Score de confiance</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Nom complet</label>
                        <div className="relative">
                          <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium focus:ring-primary focus:border-primary border-transparent" type="text" defaultValue="ALEXANDER J. STERLING"/>
                          <span className="material-symbols-outlined absolute right-2 top-2 text-primary text-lg">check_circle</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <label className="text-xs font-semibold text-slate-400 uppercase">Date de naissance</label>
                          <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="12 MAI 1988"/>
                        </div>
                        <div className="space-y-1">
                          <label className="text-xs font-semibold text-slate-400 uppercase">Expire le</label>
                          <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="24 AOÛT 2029"/>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Numéro d'identité</label>
                        <div className="relative">
                          <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="G-2944-1002-9981"/>
                          <span className="material-symbols-outlined absolute right-2 top-2 text-primary text-lg">check_circle</span>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Adresse</label>
                        <textarea className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" rows="2" defaultValue="422 Oakwood Drive, Redwood City, CA 94063"></textarea>
                      </div>
                    </div>
                  </div>
                  <div className="mt-8 flex gap-3">
                    <button className="flex-1 rounded-lg h-11 bg-primary text-white font-bold text-sm hover:bg-primary/90 transition-colors">Approuver</button>
                    <button className="px-4 rounded-lg h-11 border border-[#ed3500]/20 text-[#ed3500] font-bold text-sm hover:bg-[#ed3500]/5 transition-colors" style={{borderColor: '#ed350044'}}>Signaler</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
