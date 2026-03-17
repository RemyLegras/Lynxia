import React from 'react';
import Layout from '../components/Layout';

export default function Dashboard() {
  return (
    <Layout title="Tableau de bord">
        {/* Dashboard Body */}
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl text-slate-900 dark:text-white tracking-tight font-semibold">Vue d'ensemble</h1>
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
              <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Analysés</p>
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
              <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Extraits</p>
              <h3 className="text-3xl font-black mt-1">8,902</h3>
            </div>
          </div>

          {/* Recent Activity Table */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-sm uppercase tracking-widest text-slate-400 font-bold">Activité récente</h3>
              <button className="text-[#093fb4] text-xs font-bold uppercase hover:underline">Voir tout</button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/50">
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Document</th>
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Date</th>
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Statut</th>
                    <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest text-right font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-slate-400 text-[20px]">picture_as_pdf</span>
                        <span className="text-sm font-semibold">facture_t4_2023.pdf</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">24 Oct. 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 font-bold">
                        Vérifié
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
                        <span className="text-sm font-semibold">contrat_v2.docx</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">24 Oct. 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-[#ed3500]/10 text-[#ed3500] font-bold">
                        Avertissement
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
                        <span className="text-sm font-semibold">passeport_scan.jpg</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">23 Oct. 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 font-bold">
                        Synchronisation
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
                        <span className="text-sm font-semibold">releve_bancaire.pdf</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">23 Oct. 2023</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 font-bold">
                        Falsifié
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
    </Layout>
  );
}