import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export default function Layout({ title, children }) {
    return (
        <div className="font-display bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 flex min-h-screen">
            <Sidebar />
            
            {/* Main Content */}
            <main className="flex-1 ml-64 min-h-screen">
                <Header title={title} />
                {children}
            </main>
        </div>
    );
}
