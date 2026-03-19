import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { authApi, documentsApi } from '../services/api';

function normalizeStatus(document) {
  const status = (document?.status || document?.curated_data?.statut || '').toLowerCase();

  if (['approved', 'approuved'].includes(status)) {
    return 'success';
  }

  if (['alerte', 'warning', 'falsifie', 'falsifié'].includes(status)) {
    return 'warning';
  }

  if (['uploaded', 'ocr_processing', 'ocr_completed', 'curation_processing', 'valide', 'validé', 'verified', 'processed'].includes(status)) {
    return 'processing';
  }

  return 'processing';
}

function getStatusUi(document) {
  const normalized = normalizeStatus(document);

  if (normalized === 'success') {
    return {
      label: 'Approuvé',
      className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      icon: 'verified',
    };
  }

  if (normalized === 'warning') {
    return {
      label: 'Alerte',
      className: 'bg-[#ed3500]/10 text-[#ed3500]',
      icon: 'warning',
    };
  }

  return {
    label: 'En attente',
    className: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    icon: 'sync',
  };
}

function formatDate(value) {
  if (!value) {
    return 'N/A';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getDocumentName(document) {
  return document?.raw_path || `${document?.document_type || 'document'}-${document?.element_id || ''}`;
}

function getDocumentIcon(documentName = '') {
  const lower = documentName.toLowerCase();

  if (lower.endsWith('.pdf')) {
    return 'picture_as_pdf';
  }

  if (lower.endsWith('.png') || lower.endsWith('.jpg') || lower.endsWith('.jpeg')) {
    return 'image';
  }

  return 'description';
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isCancelled = false;

    const loadDashboard = async () => {
      try {
        setIsLoading(true);
        const [statsResponse, documentsResponse] = await Promise.all([
          authApi.stats(),
          documentsApi.list(20, 0),
        ]);

        if (isCancelled) {
          return;
        }

        setStats(statsResponse.data);
        setDocuments(documentsResponse.data || []);
        setError(null);
      } catch (err) {
        if (isCancelled) {
          return;
        }

        console.error(err);
        setError('Impossible de charger le tableau de bord.');
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      isCancelled = true;
    };
  }, []);

  const computedStats = useMemo(() => {
    const successCount = documents.filter((document) => normalizeStatus(document) === 'success').length;
    const warningCount = documents.filter((document) => normalizeStatus(document) === 'warning').length;
    const processingCount = documents.filter((document) => normalizeStatus(document) === 'processing').length;

    return {
      total: stats?.document_stats?.total_documents || documents.length,
      processed: stats?.document_stats?.processed_documents || successCount + warningCount,
      uploaded: stats?.document_stats?.uploaded_documents || processingCount,
      warnings: warningCount,
      success: successCount,
    };
  }, [documents, stats]);

  return (
    <Layout title="Tableau de bord">
      <div className="p-8">
        <div className="mb-8 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl text-slate-900 dark:text-white tracking-tight font-semibold">Vue d'ensemble</h1>
            <p className="text-sm text-slate-500 mt-2">Suivi des documents stockés et traités depuis MySQL.</p>
          </div>
          <Link to="/upload" className="rounded-lg h-11 px-5 inline-flex items-center bg-primary text-white font-bold text-sm hover:bg-primary/90 transition-colors">
            Importer un document
          </Link>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-900/20 dark:border-red-800">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <div className="text-[#093fb4]">
                <span className="material-symbols-outlined">description</span>
              </div>
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Documents totaux</p>
            <h3 className="text-3xl font-black mt-1">{isLoading ? '...' : computedStats.total}</h3>
          </div>

          <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <div className="text-green-600">
                <span className="material-symbols-outlined">verified</span>
              </div>
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Validés avec succès</p>
            <h3 className="text-3xl font-black mt-1">{isLoading ? '...' : computedStats.success}</h3>
          </div>

          <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <div className="text-[#ed3500]">
                <span className="material-symbols-outlined">warning</span>
              </div>
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">Alertes</p>
            <h3 className="text-3xl font-black mt-1">{isLoading ? '...' : computedStats.warnings}</h3>
          </div>

          <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <div className="text-amber-500">
                <span className="material-symbols-outlined">sync</span>
              </div>
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">En cours de traitement</p>
            <h3 className="text-3xl font-black mt-1">{isLoading ? '...' : computedStats.uploaded}</h3>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <h3 className="text-sm uppercase tracking-widest text-slate-400 font-bold">Documents récents</h3>
            <span className="text-xs text-slate-500">{documents.length} résultat(s)</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/50">
                  <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Document</th>
                  <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Type</th>
                  <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Date</th>
                  <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest font-medium">Statut</th>
                  <th className="px-6 py-3 text-[10px] text-slate-400 uppercase tracking-widest text-right font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {!isLoading && documents.length === 0 && (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-sm text-slate-500 text-center">
                      Aucun document disponible pour le moment.
                    </td>
                  </tr>
                )}

                {documents.map((document) => {
                  const documentName = getDocumentName(document);
                  const statusUi = getStatusUi(document);

                  return (
                    <tr key={document.element_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <span className="material-symbols-outlined text-slate-400 text-[20px]">{getDocumentIcon(documentName)}</span>
                          <div>
                            <p className="text-sm font-semibold">{documentName}</p>
                            <p className="text-xs text-slate-500">ID: {document.element_id}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500">{document.document_type || 'unknown'}</td>
                      <td className="px-6 py-4 text-xs text-slate-500">{formatDate(document.updated_at || document.created_at)}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${statusUi.className}`}>
                          <span className="material-symbols-outlined text-xs">{statusUi.icon}</span>
                          {statusUi.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link to={`/upload?documentId=${document.element_id}`} className="p-2 text-[#093fb4] hover:bg-[#093fb4]/5 rounded-lg transition-colors inline-flex">
                          <span className="material-symbols-outlined text-[20px]">visibility</span>
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}