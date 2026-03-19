import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { documentsApi } from '../services/api';

const POLLING_INTERVAL_MS = 5000;

const PROCESSING_STATUSES = new Set([
  'uploaded',
  'ocr_processing',
  'ocr_completed',
  'curation_processing',
]);

function getCuratedDataEntries(curatedData) {
  if (!curatedData || typeof curatedData !== 'object') {
    return [];
  }

  return Object.entries(curatedData).filter(([, value]) => {
    if (value === null || value === undefined) {
      return false;
    }

    if (typeof value === 'string') {
      return value.trim() !== '';
    }

    return true;
  });
}

function getProcessingSteps(document) {
  const status = (document?.status || '').toLowerCase();
  const hasUploaded = Boolean(document?.element_id);
  const hasOcr = Boolean(document?.clean_text_ref);
  const hasCuratedData = getCuratedDataEntries(document?.curated_data).length > 0;

  const uploadDone = hasUploaded;
  const ocrDone = uploadDone && hasOcr;
  const curationDone = ocrDone && hasCuratedData;
  const dbDone = curationDone;

  return [
    {
      key: 'uploaded',
      label: 'Upload du document',
      done: uploadDone,
      active: hasUploaded && !ocrDone,
    },
    {
      key: 'ocr',
      label: 'OCR dans MinIO',
      done: ocrDone,
      active: uploadDone && !ocrDone && status === 'ocr_processing',
    },
    {
      key: 'curation',
      label: 'Extraction et structuration',
      done: curationDone,
      active: ocrDone && !curationDone && ['ocr_completed', 'curation_processing'].includes(status),
    },
    {
      key: 'db',
      label: 'Données disponibles en base',
      done: dbDone,
      active: curationDone && !dbDone,
    },
  ];
}

function getStatusMeta(document) {
  const status = document?.status || 'uploaded';
  const normalizedStatus = status.toLowerCase();
  const hasCuratedData = getCuratedDataEntries(document?.curated_data).length > 0;

  if (hasCuratedData) {
    if (normalizedStatus === 'alerte') {
      return {
        label: 'Alerte',
        tone: 'bg-red-100 text-[#ed3500] dark:bg-red-900/30',
        description: 'Les champs ci-dessous proviennent de MySQL après traitement.',
      };
    }

    if (['approved', 'approuved'].includes(normalizedStatus)) {
      return {
        label: 'Approuvé',
        tone: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
        description: 'Le document a été approuvé et enregistré en base.',
      };
    }

    return {
      label: 'Traité',
      tone: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      description: 'Les champs ci-dessous proviennent de MySQL après traitement.',
    };
  }

  const statusMap = {
    uploaded: 'Document reçu, en attente du pipeline OCR.',
    ocr_processing: 'OCR en cours dans MinIO.',
    ocr_completed: 'OCR terminé, structuration en cours.',
    curation_processing: 'Curated data en cours de génération.',
  };

  return {
    label: 'En traitement',
    tone: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    description: statusMap[normalizedStatus] || 'Traitement en cours.',
  };
}

export default function Upload() {
  const [searchParams] = useSearchParams();
  const selectedDocumentId = searchParams.get('documentId');
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [documentData, setDocumentData] = useState(null);
  const [pollError, setPollError] = useState(null);
  const [isApproving, setIsApproving] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (!selectedDocumentId) {
      return undefined;
    }

    let isCancelled = false;

    const loadDocument = async () => {
      try {
        const response = await documentsApi.get(selectedDocumentId);
        if (isCancelled) {
          return;
        }

        setUploadedDoc(response.data);
        setDocumentData(response.data);
        setUploadMessage(null);
        setPollError(null);
      } catch (error) {
        if (isCancelled) {
          return;
        }

        console.error(error);
        setUploadMessage({ type: 'error', text: "Impossible d'ouvrir ce document." });
      }
    };

    loadDocument();

    return () => {
      isCancelled = true;
    };
  }, [selectedDocumentId]);

  useEffect(() => {
    if (!uploadedDoc?.element_id) {
      return undefined;
    }

    let isCancelled = false;
    let timeoutId;

    const pollDocument = async () => {
      try {
        const response = await documentsApi.get(uploadedDoc.element_id);
        if (isCancelled) {
          return;
        }

        const nextDocument = response.data;
        setDocumentData(nextDocument);
        setPollError(null);

        const hasCuratedData = getCuratedDataEntries(nextDocument?.curated_data).length > 0;
        const stillProcessing = PROCESSING_STATUSES.has(nextDocument?.status);

        if (!hasCuratedData || stillProcessing) {
          timeoutId = window.setTimeout(pollDocument, POLLING_INTERVAL_MS);
        }
      } catch (error) {
        if (isCancelled) {
          return;
        }

        console.error(error);
        setPollError("Impossible de suivre le traitement pour le moment.");
        timeoutId = window.setTimeout(pollDocument, POLLING_INTERVAL_MS);
      }
    };

    pollDocument();

    return () => {
      isCancelled = true;
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [uploadedDoc?.element_id]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setIsUploading(true);
    setUploadMessage(null);
    setPollError(null);
    setUploadedDoc(null);
    setDocumentData(null);
    try {
      const resp = await documentsApi.upload(file);
      setUploadedDoc(resp.data.document);
      setDocumentData(resp.data.document);
      setUploadMessage({ type: 'success', text: "Document téléchargé. Attente du traitement OCR et de l'écriture en base." });
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

  const handleFieldChange = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const buildCuratedPayload = () => ({
    ...curatedData,
    ...formData,
  });

  const persistCuratedData = async () => {
    if (!displayedDocument?.element_id) {
      return null;
    }

    const payload = buildCuratedPayload();
    const response = await documentsApi.updateCuratedData(displayedDocument.element_id, payload);
    setDocumentData(response.data.document);
    setFormData(response.data.document?.curated_data || {});
    return response.data.document;
  };

  const handleApprove = async () => {
    if (!displayedDocument?.element_id || !isProcessed) {
      return;
    }

    try {
      setIsApproving(true);
      await persistCuratedData();
      const response = await documentsApi.updateStatus(displayedDocument.element_id, 'approuved');
      setDocumentData(response.data);
      setFormData(response.data?.curated_data || {});
      setUploadMessage({ type: 'success', text: 'Document approuvé avec succès.' });
    } catch (error) {
      console.error(error);
      setUploadMessage({ type: 'error', text: "Impossible d'approuver le document." });
    } finally {
      setIsApproving(false);
    }
  };

  const displayedDocument = documentData || uploadedDoc;
  const curatedData = displayedDocument?.curated_data || {};
  const editableCuratedData = { ...curatedData, ...formData };
  const curatedEntries = useMemo(() => getCuratedDataEntries(curatedData), [curatedData]);
  const processingSteps = useMemo(() => getProcessingSteps(displayedDocument), [displayedDocument]);
  const statusMeta = useMemo(() => getStatusMeta(displayedDocument), [displayedDocument]);
  const isProcessed = curatedEntries.length > 0;
  const scoreLabel = displayedDocument?.status?.toLowerCase() === 'approuved' ? 'Approuvé' : editableCuratedData?.statut?.toLowerCase() === 'alerte' ? 'Alerte' : isProcessed ? 'Disponible' : 'En attente';

  useEffect(() => {
    setFormData(curatedData || {});
  }, [displayedDocument?.element_id, curatedData]);

  const handleSave = async () => {
    if (!displayedDocument?.element_id) {
      return;
    }

    try {
      setIsSaving(true);
      await persistCuratedData();
      setUploadMessage({ type: 'success', text: 'Informations enregistrées avec succès.' });
    } catch (error) {
      console.error(error);
      setUploadMessage({ type: 'error', text: "Impossible d'enregistrer les informations." });
    } finally {
      setIsSaving(false);
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
                <div className="w-full max-w-xl rounded-2xl bg-white dark:bg-slate-800 shadow-xl overflow-hidden border border-slate-300 dark:border-slate-700">
                  <div className="px-6 py-5 border-b border-primary/10 bg-slate-50 dark:bg-slate-800/80">
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <div>
                        <p className="text-sm font-semibold text-slate-900 dark:text-white">Suivi du pipeline</p>
                        <p className="text-xs text-slate-500">Document ID: {displayedDocument?.element_id || 'en attente'}</p>
                      </div>
                      <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded ${statusMeta.tone}`}>
                        {statusMeta.label}
                      </span>
                    </div>
                    <p className="text-sm text-slate-500">{statusMeta.description}</p>
                  </div>
                  <div className="p-6 space-y-4">
                    {processingSteps.map((step, index) => {
                      const stateClass = step.done
                        ? 'bg-green-500 border-green-500 text-white'
                        : step.active
                          ? 'bg-primary border-primary text-white animate-pulse'
                          : 'bg-white border-slate-300 text-slate-400 dark:bg-slate-900 dark:border-slate-700';

                      return (
                        <div key={step.key} className="flex items-start gap-3">
                          <div className="flex flex-col items-center">
                            <div className={`size-8 rounded-full border flex items-center justify-center text-xs font-bold ${stateClass}`}>
                              {step.done ? '✓' : index + 1}
                            </div>
                            {index < processingSteps.length - 1 && (
                              <div className={`w-px h-8 ${step.done ? 'bg-green-400' : 'bg-slate-300 dark:bg-slate-700'}`}></div>
                            )}
                          </div>
                          <div className="pt-1">
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">{step.label}</p>
                            <p className="text-xs text-slate-500">
                              {step.done ? 'Étape terminée' : step.active ? 'En cours...' : 'En attente'}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                    {pollError && (
                      <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/20 dark:border-red-800">
                        {pollError}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div className="xl:col-span-5 flex flex-col gap-6">
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-primary/10 shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-semibold text-lg">Résultats</h3>
                  <div className="flex gap-2">
                    <span className={`flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded ${isProcessed ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'}`}>
                      <span className="material-symbols-outlined text-xs">verified</span>
                      {isProcessed ? 'Base OK' : 'En attente'}
                    </span>
                    <span className={`flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded ${curatedData?.statut?.toLowerCase() === 'alerte' ? 'bg-red-100 text-[#ed3500] dark:bg-red-900/30' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'}`}>
                      <span className="material-symbols-outlined text-xs">warning</span>
                      Alerte
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-4 p-4 rounded-xl bg-primary/5 border border-primary/10 mb-6">
                  <div className="relative size-16">
                    <svg className="size-16 -rotate-90">
                      <circle className="text-slate-200 dark:text-slate-700" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeWidth="6"></circle>
                      <circle className="text-primary" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeDasharray="175.84" strokeDashoffset={isProcessed ? '8.79' : '70'} strokeLinecap="round" strokeWidth="6"></circle>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-primary">{isProcessed ? '95%' : '...'}</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-lg font-bold leading-tight">{scoreLabel}</p>
                    <p className="text-xs text-slate-500 mt-0.5">Source unique : MySQL</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 gap-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Type de document</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border-primary/20 rounded-lg px-3 py-2 text-sm font-medium border-transparent" type="text" value={displayedDocument?.document_type || ''} readOnly />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Date de validation</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.date_validation || ''} onChange={(e) => handleFieldChange('date_validation', e.target.value)} />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-400 uppercase">Numéro SIRET</label>
                      <div className="relative">
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium focus:ring-primary focus:border-primary" type="text" value={editableCuratedData?.siret || ''} onChange={(e) => handleFieldChange('siret', e.target.value)} />
                        {editableCuratedData?.siret && <span className="material-symbols-outlined absolute right-2 top-2 text-primary text-lg">check_circle</span>}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-400 uppercase">Numéro TVA</label>
                      <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.tva || ''} onChange={(e) => handleFieldChange('tva', e.target.value)} />
                    </div>

                    <div className="grid grid-cols-3 gap-2">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Montant HT</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.montant_ht ?? ''} onChange={(e) => handleFieldChange('montant_ht', e.target.value)} />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Montant TVA</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.montant_tva ?? ''} onChange={(e) => handleFieldChange('montant_tva', e.target.value)} />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Montant TTC</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.montant_ttc ?? editableCuratedData?.montant_total ?? ''} onChange={(e) => handleFieldChange('montant_ttc', e.target.value)} />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Devise</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.devise || ''} onChange={(e) => handleFieldChange('devise', e.target.value)} />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-400 uppercase">Description</label>
                        <input className="w-full bg-slate-50 dark:bg-slate-800 border border-primary/20 rounded-lg px-3 py-2 text-sm font-medium" type="text" value={editableCuratedData?.description || ''} onChange={(e) => handleFieldChange('description', e.target.value)} />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-8 flex gap-3">
                  <button onClick={handleSave} className="px-4 rounded-lg h-11 border border-primary/20 text-primary font-bold text-sm hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" disabled={!displayedDocument?.element_id || isSaving || isApproving}>{isSaving ? 'Enregistrement...' : 'Enregistrer'}</button>
                  <button onClick={handleApprove} className="flex-1 rounded-lg h-11 bg-primary text-white font-bold text-sm hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" disabled={!isProcessed || isApproving || displayedDocument?.status?.toLowerCase() === 'approuved'}>{isApproving ? 'Approbation...' : displayedDocument?.status?.toLowerCase() === 'approuved' ? 'Approuvé' : 'Approuver'}</button>
                  <button className="px-4 rounded-lg h-11 border border-[#ed3500]/20 text-[#ed3500] font-bold text-sm hover:bg-[#ed3500]/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" style={{ borderColor: '#ed350044' }} disabled={!isProcessed}>Signaler</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
