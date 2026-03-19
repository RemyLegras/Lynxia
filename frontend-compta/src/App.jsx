import { useState, useEffect } from 'react';
import './App.css';

// Minimalist API call simulation (or real API call)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch real documents from Gold zone
  useEffect(() => {
    const fetchGoldData = async () => {
      try {
        const response = await fetch(`${API_URL}/api/documents/gold/all`);
        if (response.ok) {
          const data = await response.json();
          setTasks(data);
        }
      } catch (error) {
        console.error("Failed to fetch Gold docs", error);
      } finally {
        setLoading(false);
      }
    };

    // Phase 1: Initial load
    fetchGoldData();

    // Phase 2: Polling (Receiving data automatically every 10 seconds)
    const interval = setInterval(fetchGoldData, 10000); // Poll every 10s

    return () => clearInterval(interval);
  }, []);

  const handleSelect = (task) => {
    setSelectedTask(task);
  };

  const handleValidate = () => {
    alert(`Écriture comptable générée avec succès pour le document ${selectedTask.id}`);
    setTasks(tasks.filter(t => t.id !== selectedTask.id));
    setSelectedTask(null);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Logiciel Comptable - Validation des Injections</h1>
        <p>Simulation du Front-End Métier recevant les données Gold</p>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <h2>Tâches à valider ({tasks.length})</h2>
          {loading ? (
            <p>Chargement...</p>
          ) : (
            <ul className="task-list">
              {tasks.map(task => (
                <li 
                  key={task.id} 
                  className={`task-item ${selectedTask?.id === task.id ? 'active' : ''}`}
                  onClick={() => handleSelect(task)}
                >
                  <div className="task-header">
                    <strong>{task.type} {task.id}</strong>
                    <span className={`badge ${task.status.includes('OK') ? 'badge-success' : 'badge-danger'}`}>
                      {task.status}
                    </span>
                  </div>
                  <p className="task-siret">SIRET: {task.curated_data.siret}</p>
                  <p className="task-amount">{task.curated_data.montant_ttc} €</p>
                </li>
              ))}
              {tasks.length === 0 && <p>Aucune tâche en attente.</p>}
            </ul>
          )}
        </aside>

        <main className="main-content">
          {selectedTask ? (
            <div className="form-container">
              <h2>Aperçu de l'écriture comptable</h2>
              <p className="subtitle">Les champs sont pré-remplis automatiquement grâce à l'extraction OCR et la validation.</p>
              
              <form className="accounting-form">
                <div className="form-group">
                  <label>Type de document</label>
                  <input type="text" readOnly value={selectedTask.type} />
                </div>
                <div className="form-group row">
                  <div className="half">
                    <label>SIRET Fournisseur</label>
                    <input type="text" readOnly value={selectedTask.curated_data.siret} />
                  </div>
                  <div className="half">
                    <label>Nom Fournisseur</label>
                    <input type="text" readOnly value={selectedTask.curated_data.fournisseur || 'Inconnu'} />
                  </div>
                </div>
                <div className="form-group row">
                  <div className="third">
                    <label>Montant HT (€)</label>
                    <input type="number" readOnly value={selectedTask.curated_data.montant_ht} className="amount-input" />
                  </div>
                  <div className="third">
                    <label>TVA (€)</label>
                    <input type="number" readOnly value={selectedTask.curated_data.montant_tva} className="amount-input" />
                  </div>
                  <div className="third">
                    <label>Montant TTC (€)</label>
                    <input type="number" readOnly value={selectedTask.curated_data.montant_ttc} className="amount-input bold" />
                  </div>
                </div>
                
                <div className="form-actions">
                  <button type="button" className="btn-validate" onClick={handleValidate} disabled={!selectedTask.status.includes('OK')}>
                    Valider & Passer en Compta
                  </button>
                  <button type="button" className="btn-reject" onClick={() => setSelectedTask(null)}>
                    Mettre en litige
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="empty-state">
              <p>Sélectionnez une tâche à gauche pour afficher le formulaire de validation pré-rempli.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
