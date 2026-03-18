import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { authApi } from '../services/api';

export default function Profile() {
    const navigate = useNavigate();
    const emailOnly = localStorage.getItem("user") || "Utilisateur";
    const [userEmail, setUserEmail] = useState(emailOnly);
    const [firstName, setFirstName] = useState(emailOnly.split('@')[0] || "");
    const [lastName, setLastName] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState("info");

    useEffect(() => {
        const loadProfile = async () => {
            try {
                const response = await authApi.me();
                const user = response?.data?.user || {};
                const email = user.email || emailOnly;
                setUserEmail(email);
                setFirstName(user.first_name || email.split('@')[0] || "");
                setLastName(user.last_name || "");
                localStorage.setItem("user", email);
            } catch (error) {
                if (error?.response?.status === 401) {
                    localStorage.removeItem("token");
                    navigate('/login');
                    return;
                }
                setMessageType("error");
                setMessage("Impossible de charger votre profil.");
            } finally {
                setIsLoading(false);
            }
        };

        loadProfile();
    }, [emailOnly, navigate]);

    const handleSave = async () => {
        setIsSaving(true);
        setMessage("");
        setMessageType("info");
        try {
            const response = await authApi.updateMe({
                first_name: firstName || null,
                last_name: lastName || null,
            });

            const user = response?.data?.user || {};
            if (user.email) {
                setUserEmail(user.email);
                localStorage.setItem("user", user.email);
            }
            setFirstName(user.first_name || "");
            setLastName(user.last_name || "");
            setMessageType("success");
            setMessage("Profil mis à jour avec succès.");
        } catch (error) {
            if (error?.response?.status === 401) {
                localStorage.removeItem("token");
                navigate('/login');
                return;
            }
            const apiMessage = error?.response?.data?.detail;
            setMessageType("error");
            setMessage(apiMessage || "Échec de la mise à jour du profil.");
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <Layout title="Mon Profil">
                <div className="p-8 max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

                    {/* Profile Card */}
                    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md">
                        {/* Header */}
                        <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center gap-6 bg-slate-50/50 dark:bg-slate-800/20">
                            <div className="relative group">
                                <img
                                    alt="Avatar"
                                    className="h-20 w-20 rounded-full object-cover border-2 border-white dark:border-slate-800 shadow-inner"
                                    src={`https://ui-avatars.com/api/?name=${encodeURIComponent(userEmail)}&background=093fb4&color=fff`}
                                />
                                <button className="absolute -bottom-1 -right-1 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 p-1.5 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 hover:text-primary transition-all hover:scale-110 active:scale-90">
                                    <span className="material-symbols-outlined text-sm">edit</span>
                                </button>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-slate-900 dark:text-white">{firstName} {lastName || '(Nom non renseigné)'}</h3>
                                <p className="text-slate-500 text-sm mt-1">Administrateur</p>
                            </div>
                        </div>

                        {/* Personal Info */}
                        <div className="p-8 space-y-6">
                            <div className="grid grid-cols-2 gap-6">
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Prénom</label>
                                    <input
                                        type="text"
                                        value={firstName}
                                        onChange={(e) => setFirstName(e.target.value)}
                                        disabled={isLoading || isSaving}
                                        className="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-900 dark:text-white py-2.5 px-3 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Nom</label>
                                    <input
                                        type="text"
                                        value={lastName}
                                        onChange={(e) => setLastName(e.target.value)}
                                        disabled={isLoading || isSaving}
                                        className="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-900 dark:text-white py-2.5 px-3 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                                    />
                                </div>
                                <div className="col-span-1 md:col-span-2 space-y-1.5">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Email</label>
                                    <input
                                        type="email"
                                        value={userEmail}
                                        readOnly
                                        className="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800/80 text-slate-500 py-2.5 px-3 text-sm cursor-not-allowed outline-none"
                                    />
                                </div>
                            </div>
                            {message && (
                                <p
                                    className={`text-sm rounded-lg px-3 py-2 ${
                                        messageType === 'success'
                                            ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                                            : messageType === 'error'
                                            ? 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                                            : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                                    }`}
                                >
                                    {message}
                                </p>
                            )}
                            <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-end">
                                <button
                                    onClick={handleSave}
                                    disabled={isLoading || isSaving}
                                    className="px-6 py-2.5 bg-primary text-white rounded-lg text-sm font-bold hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed"
                                >
                                    {isSaving ? 'Enregistrement...' : 'Enregistrer les modifications'}
                                </button>
                            </div>
                        </div>

                        {/* Security & Preferences */}
                        <div className="bg-slate-50/50 dark:bg-slate-900/50 p-8 border-t border-slate-100 dark:border-slate-800 space-y-6">
                            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">Sécurité & Préférences</h4>

                            <div className="flex items-center justify-between group">
                                <div>
                                    <p className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-primary transition-colors">Mot de passe</p>
                                    <p className="text-xs text-slate-500">Gérez votre mot de passe pour sécuriser votre compte</p>
                                </div>
                                <button className="text-xs font-bold text-primary hover:text-primary/80 transition-colors bg-primary/5 px-4 py-2 rounded-lg border border-primary/10">Modifier</button>
                            </div>
                        </div>

                        {/* Account Deletion */}
                        <div className="px-8 py-8 flex justify-center border-t border-slate-100 dark:border-slate-800">
                            <button className="text-xs font-bold text-[#ed3500] hover:text-[#ed3500]/80 transition-colors uppercase tracking-widest">
                                Supprimer le profil
                            </button>
                        </div>

                    </div>

                </div>
        </Layout>
    );
}
