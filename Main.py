from SimulationManager import *
from Queues import Queue
from Resource import *
from Store import *
from Queues import * 
from Entity import *


seed = 42
period_max = 100
num_sim = 2 # numero di simulazioni
par_arrival = 0.7  # lambda 
par_recovery = 0.9    # parametro di intertempo (esponenziale) che intercorre tra failure e guarigione
par_failure = 0.03    # parametro di intertempo (esponenziale) tra due failure
par_process_1 = 0.5   # lambda
par_process_2 = [3,1]

# inizializzo l'ambiente di simulazione
sim = SimulationManager(random_seed = seed, par_arrival=par_arrival, par_process_1=par_process_1, par_process_2=par_process_2, par_recovery=par_recovery, par_failure=par_failure)  # se facciamo poi il ciclo qua si può mettere un nome che cambia ogni volta

for i in range(0,num_sim):

    print("Inizio simulazione")
    print(i)

    # resetto ambiente di simulazione
    sim.reset()

    # inizializzo code e store
    queue_1 = Queue(sim=sim, capacity_max=10)
    store_1 = Store(sim=sim, capacity_max=1)
    store_2 = Store(sim=sim, capacity_max=3)
    store_3 = Store(sim=sim, capacity_max=2)

    # inizializzo risorse
    nurse_1 = Nurse(sim=sim, skill_level=3, store = store_1)
    nurse_2 = Nurse(sim=sim, skill_level=2, store = store_2)
    nurse_3 = Nurse(sim=sim, skill_level=4, store = store_3)
    doc_1 = Doctor(sim=sim, queue = queue_1)
    doc_2 = Doctor(sim=sim, queue = queue_1)

    # Inserisco i primi eventi nella lista degli eventi (quelli autoschedulanti: arrivi e failure)
    sim.initialize_first_events(queue_1, list_doc=[doc_1,doc_2], list_nurse=[nurse_1, nurse_2,nurse_3])

    while (sim.clock < period_max or len(sim.list_of_event) == 0):   # eventualmente spostarlo in un metodo nella classe SimulationManager
        print("------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------")
        #sim.stamp_list_events()
        current_time =  sim.extract_event(sim=sim)
        print("Clock di simulazione")
        print(current_time)
        #sim.visualize_queue_doctors_nurses()
        print("------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------")
        if current_time == -1:
            break
    print("STATISTICHE")
    print("Entità totali arrivate in totale nel sistema:")
    print(sim.entity_arrived)
    print("Entità perse per balking in coda:")
    queue_1.lost_entities.print_object_data_collection()
    print("Entità perse perchè non ci sono sufficienti posti nelle stanze:")
    queue_1.lost_entities_after_queue.print_object_data_collection()
    queue_1.length_of_stay.plot_no_time(title="Tempo di permanenza in coda per ogni entità")
    queue_1.len_queues.plot_in_time(queue_1.capacity_max, title="Lunghezza della coda nel tempo")
    print("Media integrale lunghezza della coda:")
    print(queue_1.len_queues.calculate_integral_mean())
    print("Media integrale dimensione store1")
    print(store_1.dim_store.calculate_integral_mean())
    print("Media integrale dimensione store2")
    print(store_2.dim_store.calculate_integral_mean())
    print("Media integrale dimensione store3")
    print(store_3.dim_store.calculate_integral_mean())
    nurse_1.delta_skill_level.plot_no_time("Differenza (positiva) di skill level tra paziente-infermiere")
    nurse_2.delta_skill_level.plot_no_time("Differenza (positiva) di skill level tra paziente-infermiere")
    nurse_3.delta_skill_level.plot_no_time("Differenza (positiva) di skill level tra paziente-infermiere")
    store_1.dim_store.plot_in_time(store_1.capacity_max , title="Numero di pazienti nella stanza 1 nel tempo")
    store_2.dim_store.plot_in_time(store_2.capacity_max , title="Numero di pazienti nella stanza 2 nel tempo")
    store_3.dim_store.plot_in_time(store_3.capacity_max , title="Numero di pazienti nella stanza 3 nel tempo")
    nurse_3.delta_skill_level.print_object_data_collection()
    