from SimulationManager import *
from Queues import Queue
from Resource import *
from Store import *
from Queues import * 
from Entity import *
from output_analysis import *


seed = 43  # Valore del seme per la generazione casuale (riproducibilità)
period_max = 100  # Numero massimo di unità di tempo della simulazione
num_sim = 1  # Numero di simulazioni da eseguire
par_arrival = 0.6  # Tasso di arrivo (λ) per il processo di arrivo (distribuzione esponenziale)
par_recovery = 0.9  # Tasso di recupero (λ) dalla failure, ovvero il parametro della distribuzione esponenziale del tempo di guarigione
par_failure = 0.0003  # Tasso di guasto (λ), ovvero il parametro della distribuzione esponenziale del tempo tra due guasti
par_process_1 = 0.5  # Tasso di servizio (λ) per il primo processo (dottori)
par_process_2 = [3, 1]  # Parametri per il secondo processo (media e deviazione standard)
cap_max_queue1 = 15  # Capacità massima della coda 1 (numero massimo di elementi accodabili)

# inizializzazione l'ambiente di simulazione
sim = SimulationManager(random_seed = seed, par_arrival=par_arrival, par_process_1=par_process_1, par_process_2=par_process_2, par_recovery=par_recovery, par_failure=par_failure)  # se facciamo poi il ciclo qua si può mettere un nome che cambia ogni volta

list_stat_length_of_stay = []

for i in range(0,num_sim):

    print("Inizio simulazione")
    print(i)

    # reset ambiente di simulazione
    sim.reset()

    # inizializzazione code e store
    queue_1 = Queue(sim=sim, capacity_max=cap_max_queue1)
    store_1 = Store(sim=sim, capacity_max=1)
    store_2 = Store(sim=sim, capacity_max=3)
    store_3 = Store(sim=sim, capacity_max=2)

    # inizializzazione risorse
    nurse_1 = Nurse(sim=sim, skill_level=3, store = store_1)
    nurse_2 = Nurse(sim=sim, skill_level=2, store = store_2)
    nurse_3 = Nurse(sim=sim, skill_level=4, store = store_3)
    doc_1 = Doctor(sim=sim, queue = queue_1)
    doc_2 = Doctor(sim=sim, queue = queue_1)

    # Inserimento i primi eventi nella lista degli eventi (quelli autoschedulanti: arrivi e failure)
    sim.initialize_first_events(queue_1, list_doc=[doc_1,doc_2], list_nurse=[nurse_1, nurse_2,nurse_3])

    # Simulazione:
    while (sim.clock < period_max or len(sim.list_of_event) == 0):   
        print("------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------")
        # sim.stamp_list_events()
        current_time =  sim.extract_event(sim=sim)
        print("Clock di simulazione")
        print(current_time)
        # sim.visualize_queue_doctors_nurses()
        print("------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------")
        if current_time == -1:
            break

    list_stat_length_of_stay.append(queue_1.length_of_stay.value)


print_and_plot_stat(sim, queue_1, store_1, store_2, store_3, nurse_1, nurse_2, nurse_3)
if len(list_stat_length_of_stay) > 1 and period_max > 1000:
    output_analysis_length_of_stay(list_stat_length_of_stay)




    