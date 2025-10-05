# Simulazione a Eventi Discreti – Caso Studio Ospedaliero

## Descrizione
Questo progetto implementa una simulazione a eventi discreti (Discrete Event Simulation – DES) con classi astratte generiche e un esempio applicativo in un contesto ospedaliero. 
La simulazione gestisce pazienti, risorse (dottori e infermieri), code e stanze, permettendo di analizzare il flusso dei pazienti e l’utilizzo delle risorse.
Il framework è generalizzabile: le classi astratte possono essere estese per altri casi di studio.
## Struttura del Progetto
- **SimulationManager**: gestisce tempo, eventi, entità e risorse.  
- **Event**: definisce gli eventi e il metodo `event_manager`.  
- **Entity**: rappresenta entità (es. pazienti) con stato e posizione.  
- **Resource**: risorse generiche (stato: idle, busy, failed, reserved).  
- **Queue / Queues.py**: code prioritarie con gestione lista doppiamente collegata.  
- **Store**: spazi limitati (stanze).  
- **Distribution**: generazione di campioni da distribuzioni probabilistiche.  
- **DataCollection**: raccolta dati (temporali, non temporali, statistiche aggregate).

## Caso Studio Ospedaliero
- Pazienti arrivano, attendono in coda per i dottori, poi eventualmente ricevono assistenza in stanze con infermieri.  
- Gestione code con priorità e stanze con capacità limitata.  
- Supporta assenze temporanee di dottori e infermieri.  
- Eventi principali: `Arrival`, `Start/EndProcessDoctor`, `Start/EndProcessNurse`, `Failure`, `Recovery`.

