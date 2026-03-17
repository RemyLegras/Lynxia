import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';

export default function Dashboard() {
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
            <img src={logo} alt="LynxIA Logo" className="w-full h-full object-contain" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-slate-900 dark:text-white text-base font-bold leading-none">LynxIA</h1>
          </div>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          <a className="flex items-center gap-3 px-3 py-2 rounded-lg bg-[#093fb4]/10 text-[#093fb4]" href="#">
            <span className="material-symbols-outlined text-[20px] fill-1">dashboard</span>
            <span className="text-sm font-semibold">Dashboard</span>
          </a>
          <button onClick={() => navigate('/upload')} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <span className="material-symbols-outlined text-[20px]">description</span>
            <span className="text-sm font-medium">Upload</span>
          </button>
        </nav>

        <div className="px-4 py-4 border-t border-slate-200 dark:border-slate-800 space-y-1">
          <a className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" href="#">
            <span className="material-symbols-outlined text-[20px]">settings</span>
            <span className="text-sm font-medium">Settings</span>
          </a>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ed3500] hover:bg-[#ed3500]/5 dark:hover:bg-[#ed3500]/10 transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">logout</span>
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 min-h-screen">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Dashboard</h2>
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
                <img alt="Profile" className="h-9 w-9 rounded-full object-cover" src={`https://ui-avatars.com/api/?name=${encodeURIComponent(userEmail)}&background=093fb4&color=fff`} />
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Body */}
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl text-slate-900 dark:text-white tracking-tight font-semibold">Overview</h1>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex justify-between items-start mb-2">
                <div className="text-[#093fb4]">
                  <span className="material-symbols-outlined">description</span>
                </div>
                <span className="text-green-500 text-sm font-bold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm">trending_up</span> 12%
                </span>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Analyzed</p>
              <h3 className="text-3xl font-black mt-1">1,284</h3>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex justify-between items-start mb-2">
                <div className="text-[#ed3500]">
                  <span className="material-symbols-outlined">gpp_maybe</span>
                </div>
                <span className="text-red-500 text-sm font-bold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm">trending_up</span> 5%
                </span>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Falsifications</p>
              <h3 className="text-3xl font-black mt-1">42</h3>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex justify-between items-start mb-2">
                <div className="text-amber-500">
                  <span className="material-symbols-outlined">database</span>
                </div>
                <span className="text-red-500 text-sm font-bold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm">trending_down</span> 2%
                </span>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Extracted</p>
              <h3 className="text-3xl font-black mt-1">8,902</h3>
            </div>
          </div>

          {/* Recent Activity Table */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-sm uppercase tracking-widest text-slate-400 font-bold">Recent Activity</h3>
              <button className="text-[#093fb4] text-xs font-bold uppercase hover:underline">View All</button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/50">
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Document</th>
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Date</th>
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Status</th>
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest text-right font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-slate-400 text-[20px]">picture_as_pdf</span>
                        <span className="text-sm font-semibold">invoice_q4_2023.pdf</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">Oct 24, 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 font-bold">
                        Verified
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 text-[#093fb4] hover:bg-[#093fb4]/5 rounded-lg transition-colors">
                        <span className="material-symbols-outlined text-[20px]">visibility</span>
                      </button>
                    </td>
                  </tr>

                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-slate-400 text-[20px]">description</span>
                        <span className="text-sm font-semibold">contract_v2.docx</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">Oct 24, 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-[#ed3500]/10 text-[#ed3500] font-bold">
                        Warning
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 text-[#093fb4] hover:bg-[#093fb4]/5 rounded-lg transition-colors">
                        <span className="material-symbols-outlined text-[20px]">visibility</span>
                      </button>
                    </td>
                  </tr>

                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-slate-400 text-[20px]">image</span>
                        <span className="text-sm font-semibold">passport_scan.jpg</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">Oct 23, 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 font-bold">
                        Syncing
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 text-slate-300 cursor-not-allowed">
                        <span className="material-symbols-outlined text-[20px]">visibility</span>
                      </button>
                    </td>
                  </tr>

                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-slate-400 text-[20px]">picture_as_pdf</span>
                        <span className="text-sm font-semibold">bank_stmt.pdf</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">Oct 23, 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 font-bold">
                        Falsified
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 text-[#093fb4] hover:bg-[#093fb4]/5 rounded-lg transition-colors">
                        <span className="material-symbols-outlined text-[20px]">visibility</span>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}