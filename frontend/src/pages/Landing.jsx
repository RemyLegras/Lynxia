import React from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 relative flex min-h-screen w-full flex-col overflow-x-hidden">
      <div className="layout-container flex h-full grow flex-col">
        {/* Navigation */}
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-slate-800 px-6 md:px-20 lg:px-40 py-4 bg-background-light dark:bg-background-dark sticky top-0 z-50">
          <div className="flex items-center gap-2 text-primary">
            <div className="size-8 flex items-center justify-center overflow-hidden rounded-md bg-white">
              <img src={logo} alt="Logo" className="w-full h-full object-contain" />
            </div>
            <h2 className="text-slate-900 dark:text-white text-xl font-bold leading-tight tracking-[-0.015em]">LynxIA</h2>
          </div>
          <div className="flex flex-1 justify-end gap-8 items-center">
            <nav className="hidden md:flex items-center gap-8">
              <a className="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="#">Produit</a>
              <a className="relative text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="#">Solutions</a>
              <a className="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="#">Tarifs</a>
              <button 
                onClick={() => navigate('/login')}
                className="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors font-bold"
              >
                Connexion
              </button>
            </nav>
            <button 
              onClick={() => navigate('/login')}
              className="flex min-w-[100px] cursor-pointer items-center justify-center rounded-lg h-10 px-5 bg-primary text-white text-sm font-bold hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
            >
              <span>Démarrer</span>
            </button>
          </div>
        </header>

        <main className="flex-1">
          {/* Hero Section */}
          <section className="px-6 md:px-20 lg:px-40 py-12 lg:py-24">
            <div className="@container">
              <div className="flex flex-col gap-10 @[864px]:flex-row items-center">
                <div className="flex flex-col gap-6 flex-1 text-left">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider w-fit">
                    <span className="material-symbols-outlined text-sm">auto_awesome</span>
                    IA Intelligente de Documents
                  </div>
                  <h1 className="text-slate-900 dark:text-white text-5xl md:text-6xl font-black leading-[1.1] tracking-[-0.033em]">
                    Vérification <span className="text-primary">Instantanée</span>
                  </h1>
                  <p className="text-slate-600 dark:text-slate-400 text-lg md:text-xl font-normal leading-relaxed max-w-[480px]">
                    Détectez les falsifications et extrayez des données avec une précision inégalée. Sécurisez votre entreprise avec une fiabilité de 99,9%.
                  </p>
                  <div className="flex flex-wrap gap-4 pt-2">
                    <button 
                      onClick={() => navigate('/login')}
                      className="flex min-w-[160px] cursor-pointer items-center justify-center rounded-lg h-14 px-6 bg-primary text-white text-base font-bold shadow-xl shadow-primary/25 hover:-translate-y-1 transition-all"
                    >
                      <span>Essai Gratuit</span>
                    </button>
                  </div>
                </div>

                <div className="flex-1 w-full max-w-[600px]">
                  <div className="relative w-full aspect-square md:aspect-video rounded-2xl overflow-hidden shadow-2xl bg-gradient-to-br from-primary/20 to-slate-200 dark:to-slate-800 flex items-center justify-center border border-white/20">
                    <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1639322537228-f710d846310a?auto=format&fit=crop&q=80&w=1000')] bg-cover bg-center mix-blend-overlay opacity-40"></div>
                    <div className="relative z-10 p-8 w-full max-w-md bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-xl border border-white/20 shadow-2xl">
                      <div className="flex items-center justify-between mb-4 border-b border-slate-200 dark:border-slate-700 pb-3">
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">Traitement...</span>
                        <span className="material-symbols-outlined text-primary animate-pulse">monitoring</span>
                      </div>
                      <div className="space-y-4">
                        <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                          <div className="h-full bg-primary w-3/4"></div>
                        </div>
                        <div className="flex gap-4">
                          <div className="size-10 rounded bg-primary/20 flex items-center justify-center text-primary">
                            <span className="material-symbols-outlined text-xl">description</span>
                          </div>
                          <div className="flex-1 space-y-2">
                            <div className="h-3 w-1/2 bg-slate-300 dark:bg-slate-600 rounded"></div>
                            <div className="h-3 w-3/4 bg-slate-200 dark:bg-slate-700 rounded"></div>
                          </div>
                        </div>
                        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800/30 flex items-center gap-3">
                          <span className="material-symbols-outlined text-green-600 text-xl">verified</span>
                          <span className="text-sm font-semibold text-green-700 dark:text-green-400">Vérifié</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Process Section */}
          <section className="px-6 md:px-20 lg:px-40 py-20 bg-slate-100 dark:bg-slate-900/30">
            <div className="max-w-[1200px] mx-auto flex flex-col gap-12">
              <div className="text-center">
                <h2 className="text-slate-900 dark:text-white text-3xl font-black mb-4">Flux de travail simple</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="flex flex-col gap-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm">
                  <div className="size-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined">upload_file</span>
                  </div>
                  <h4 className="text-slate-900 dark:text-white text-lg font-bold">1. Importer</h4>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">Importez n'importe quel format via le dashboard ou l'API.</p>
                </div>
                <div className="flex flex-col gap-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm">
                  <div className="size-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined">query_stats</span>
                  </div>
                  <h4 className="text-slate-900 dark:text-white text-lg font-bold">2. Analyser</h4>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">L'IA détecte les falsifications et les altérations deepfake.</p>
                </div>
                <div className="flex flex-col gap-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm">
                  <div className="size-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined">database</span>
                  </div>
                  <h4 className="text-slate-900 dark:text-white text-lg font-bold">3. Extraire</h4>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">Recevez des données structurées directement dans votre CRM.</p>
                </div>
              </div>
            </div>
          </section>

          {/* Security */}
          <section className="px-6 md:px-20 lg:px-40 py-24">
            <div className="max-w-[1000px] mx-auto flex flex-col lg:flex-row gap-16 items-center">
              <div className="flex-1 flex flex-col gap-6">
                <h3 className="text-slate-900 dark:text-white text-3xl font-black">Sécurisé par conception</h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg">Nous priorisons la confidentialité des données avec un chiffrement de niveau bancaire et des standards mondiaux.</p>
                <div className="space-y-4 pt-4">
                  <div className="flex items-center gap-4 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                    <span className="material-symbols-outlined text-primary">lock</span>
                    <p className="text-slate-900 dark:text-white font-bold text-sm">Chiffrement AES-256</p>
                  </div>
                  <div className="flex items-center gap-4 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                    <span className="material-symbols-outlined text-primary">verified</span>
                    <p className="text-slate-900 dark:text-white font-bold text-sm">Conforme SOC2 & RGPD</p>
                  </div>
                </div>
              </div>
              <div className="flex-1 grid grid-cols-2 gap-4">
                <div className="w-full aspect-square bg-cover bg-center rounded-2xl border border-slate-200 dark:border-slate-800 shadow-lg" style={{backgroundImage: "url('https://images.unsplash.com/photo-1563986768609-322da13575f3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80')"}}></div>
                <div className="w-full aspect-square bg-cover bg-center rounded-2xl border border-slate-200 dark:border-slate-800 shadow-lg mt-8" style={{backgroundImage: "url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80')"}}></div>
              </div>
            </div>
          </section>

          {/* CTA Section */}
          <section className="px-6 md:px-20 lg:px-40 py-20">
            <div className="bg-primary rounded-3xl p-10 md:p-16 text-center flex flex-col items-center gap-8 relative overflow-hidden">
              <div className="relative z-10 flex flex-col items-center gap-6 max-w-[600px]">
                <h2 className="text-white text-4xl font-black">Éliminez la fraude aujourd'hui</h2>
                <p className="text-white/80 text-lg">Rejoignez plus de 500 entreprises sécurisant leurs flux avec LynxIA.</p>
                <div className="flex flex-wrap gap-4 justify-center pt-2">
                  <button 
                    onClick={() => navigate('/login')}
                    className="bg-white text-primary px-8 py-4 rounded-xl font-bold text-lg hover:bg-slate-100 transition-colors shadow-xl"
                  >
                    Commencer
                  </button>
                </div>
              </div>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-200 dark:border-slate-800 px-6 md:px-20 lg:px-40 py-12 bg-background-light dark:bg-background-dark">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-10">
            <div className="col-span-2">
              <div className="flex items-center gap-2 text-primary mb-6">
                <div className="size-8 overflow-hidden rounded-md bg-white">
                  <img src={logo} alt="LynxIA Logo" className="w-full h-full object-contain" />
                </div>
                <span className="text-slate-900 dark:text-white text-xl font-bold">LynxIA</span>
              </div>
            </div>
            <div>
              <h4 className="font-bold mb-6 text-sm">Produit</h4>
              <ul className="space-y-4 text-slate-500 dark:text-slate-400 text-xs">
                <li><a className="hover:text-primary transition-colors" href="#">Fonctionnalités</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Détection</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-6 text-sm">Entreprise</h4>
              <ul className="space-y-4 text-slate-500 dark:text-slate-400 text-xs">
                <li><a className="hover:text-primary transition-colors" href="#">À propos</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Carrières</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Légal</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-6 text-sm">Support</h4>
              <ul className="space-y-4 text-slate-500 dark:text-slate-400 text-xs">
                <li><a className="hover:text-primary transition-colors" href="#">Aide</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Docs</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-16 pt-8 border-t border-slate-200 dark:border-slate-800 text-slate-500 text-[10px] flex flex-col md:flex-row justify-between items-center gap-4 uppercase tracking-widest">
            <p>© 2024 LynxIA Technologies Inc.</p>
            <div className="flex gap-6">
              <a className="hover:text-primary" href="#">Confidentialité</a>
              <a className="hover:text-primary" href="#">Conditions</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
