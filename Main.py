from SimulationManager import *
from Queues import Queue
from Resource import *
from Store import *
from Queues import * 
from Entity import *
import random

seed = 42
period_max = 10
num_sim = 1 # numero di simulazioni
par_arrival = 0.65  # prova ad aumentare
par_recovery = 0.8    # parametro di intertempo (esponenziale) che intercorre tra failure e guarigione
par_failure = 0.02    # parametro di intertempo (esponenziale) tra due failure
par_process_1 = [3,1]
par_process_2 = [8,1]

# inizializzo l'ambiente di simulazione
sim = SimulationManager(random_seed= seed, par_arrival=par_arrival, par_process_1=par_process_1, par_process_2=par_process_2, par_recovery=par_recovery, par_failure=par_failure)  # se facciamo poi il ciclo qua si può mettere un nome che cambia ogni volta

for i in range(0,num_sim):

    sim.reset()
    
    # resetto le statistiche
    # sim.reset_all_stat(list_obj=[queue_1,store_1,store_2,store_3,nurse_1,nurse_2,nurse_3,doc_1,doc_2,doc_3])

    # inizializzo code e store
    queue_1 = Queue(sim=sim, capacity_max=20)
    store_1 = Store(sim=sim, capacity_max=5)
    store_2 = Store(sim=sim, capacity_max=6)
    store_3 = Store(sim=sim, capacity_max=2)

    # inizializzo risorse
    nurse_1 = Nurse(sim=sim, skill_level=3, store = store_1)
    nurse_2 = Nurse(sim=sim, skill_level=2, store = store_2)
    nurse_3 = Nurse(sim=sim, skill_level=4, store = store_3)
    doc_1 = Doctor(sim=sim, queue = queue_1)
    doc_2 = Doctor(sim=sim, queue = queue_1)
    #doc_3 = Doctor(sim=sim, queue = queue_1)

    # Inserisco i primi eventi nella lista degli eventi (quelli autoschedulanti: arrivi e failure)
    #sim.initialize_first_events(queue_1, list_doc=[doc_1,doc_2, doc_3], list_nurse=[nurse_1, nurse_2,nurse_3])
    sim.initialize_first_events(queue_1, list_doc=[doc_1,doc_2], list_nurse=[nurse_1, nurse_2,nurse_3])

    while (sim.clock < period_max or len(sim.list_of_event) == 0):   # eventualmente spostarlo in un metodo nella classe SimulationManager
        print("------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------")
        sim.stamp_list_events()
        current_time =  sim.extract_event(sim=sim)
        print("Clock di simulazione")
        print(current_time)
        print("------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------")
        if current_time == -1:
            break
    # resetto l'ambiente di simulazione

    # fare cose con le statistiche: salvarsele o fare plot
    # per esempio con la statistica quella con il tempo sarebbe utile fare una classe dove si calcola l'integrale: magari come metodo di DataTime
        
