# Simulazione a Eventi Discreti – Caso Studio Ospedaliero

## Descrizione
Questo progetto implementa una simulazione a eventi discreti (Discrete Event Simulation – DES) con classi astratte generiche e un esempio applicativo in un contesto ospedaliero. 
La simulazione gestisce pazienti, risorse (dottori e infermieri), code e stanze, permettendo di analizzare il flusso dei pazienti e l’utilizzo delle risorse.
Il framework è generalizzabile: le classi astratte possono essere estese per altri casi di studio.
## Struttura del Progetto
/project-root
│
├─ DataCollection.py # Gestione e raccolta dei dati della simulazione
├─ Distribution.py # Distribuzioni di probabilità (normale, esponenziale)
├─ Entity.py # Classe base per le entità (es. pazienti)
├─ Event.py # Classe base per gli eventi
├─ Queues.py # Implementazione delle code e dei nodi
├─ Resource.py # Classe base per le risorse (dottori, infermieri)
├─ SimulationManager.py # Gestione principale della simulazione
├─ Store.py # Gestione degli spazi limitati (stanze)
├─ Main.py # Script principale per eseguire la simulazione
├─ output_analysis.py # Script per analisi dei risultati della simulazione
├─ README.md # Questo file
└─ Report hw BA_Baitan_Bergamini.pdf # Report del progetto
