import React, { useRef, useState } from 'react';
import Layout from '../components/Layout';
import { documentsApi } from '../services/api';

export default function Upload() {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploadMessage, setUploadMessage] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setIsUploading(true);
    setUploadMessage(null);
    try {
      const resp = await documentsApi.upload(file);
      setUploadedDoc(resp.data.document);
      setUploadMessage({ type: 'success', text: "Document téléchargé avec succès" });
    } catch (error) {
      console.error(error);
      setUploadMessage({ type: 'error', text: "Erreur lors de l'envoi du document" });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDivClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  return (
    <Layout title="Importer">
      {/* Upload Body */}
      <div className="p-8">
        <div className="space-y-6 max-w-7xl mx-auto">
          <div className="flex flex-col gap-1">
            <h2 className="text-2xl font-bold tracking-tight">Nouveau scan</h2>
          </div>
          <div className="w-full">
            <input type="file" ref={fileInputRef} onChange={handleFileChange} style={{ display: 'none' }} accept=".pdf,.png,.jpg,.jpeg" />
            <div
              onClick={handleDivClick}
              className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-primary/30 bg-white dark:bg-slate-900/50 px-6 py-10 transition-all hover:border-primary/50 group cursor-pointer ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
            >
              <div className="bg-primary/10 rounded-full p-4 mb-3 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-primary text-3xl">upload_file</span>
              </div>
              <h3 className="text-lg font-bold mb-4">
                {isUploading ? "Importation en cours" : "Importer un document"}
              </h3>
              <button type="button" onClick={(e) => { e.stopPropagation(); handleDivClick(); }} className="flex items-center justify-center rounded-lg h-10 px-8 bg-primary text-white font-bold transition-all hover:bg-primary/90 shadow-md">
                {isUploading ? "Veuillez patienter" : "Sélectionner un fichier"}
              </button>
            </div>

            {uploadMessage && (
              <div className={`mt-4 p-3 rounded-lg text-sm font-semibold text-center ${uploadMessage.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:border-green-800' : 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:border-red-800'}`}>
                {uploadMessage.text}
              </div>
            )}
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
                  <div className="absolute inset-0 bg-slate-200 dark:bg-slate-700/50 opacity-20" style={{ backgroundImage: "radial-gradient(#1152d4 0.5px, transparent 0.5px)", backgroundSize: "10px 10px" }}></div>
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
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Type de document</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="attestation" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Date de validation</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="2026-01-10" />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-400 uppercase">Numéro SIRET</label>
                      <div className="relative">
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium focus:ring-primary focus:border-primary border-transparent" type="text" defaultValue="12345678900012" />
                        <span className="material-symbols-outlined absolute right-2 top-2 text-primary text-lg">check_circle</span>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-400 uppercase">Numéro TVA</label>
                      <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="FR12345678901" />
                    </div>

                    <div className="grid grid-cols-3 gap-2">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Montant HT</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="1000" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Montant TVA</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Montant TTC</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="1200" />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Devise</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="EUR" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Description</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" defaultValue="boulanger" />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-8 flex gap-3">
                  <button className="flex-1 rounded-lg h-11 bg-primary text-white font-bold text-sm hover:bg-primary/90 transition-colors">Approuver</button>
                  <button className="px-4 rounded-lg h-11 border border-[#ed3500]/20 text-[#ed3500] font-bold text-sm hover:bg-[#ed3500]/5 transition-colors" style={{ borderColor: '#ed350044' }}>Signaler</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
