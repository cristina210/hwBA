from Resource import *
from Event import *
from Entity import *
from Queues import *
from Store import *
from Distribution import *
from DataCollection import *

class SimulationManager: 
    ''' Gestisce l'intera logica della simulazione a eventi discreti.
    Mantiene l'orologio di simulazione, la lista degli eventi futuri,
    registra e deregistra gli oggetti del sistema (entità, risorse, code, store)
    e coordina l'esecuzione degli eventi.'''
    def __init__(
        self,
        random_seed: int,
        name: str = None,
        par_arrival: float = 1,
        par_process_1: float = 1.2,
        par_process_2: list = [50,1],
        par_failure: float = 1000,
        par_recovery: float = 1000
    ):
        self.random_seed = random_seed
        self.name = name

        # Parametri per i tempi di processo, failure e recovery:
        self.par_arrival = par_arrival
        self.par_process_1 = par_process_1
        self.mu_process_2 = par_process_2[0]   
        self.sig_process_2 = par_process_2[1]
        self.par_failure = par_failure
        self.par_recovery = par_recovery

        self.list_of_event = []     # Lista degli eventi futuri, ordinata per tempo di occorrenza
        self.clock = 0         # Orologio di simulazione, rappresenta il tempo corrente
        self.registered_objects = {}    # Dizionario per tenere traccia di tutti gli oggetti presenti all'interno della simulazione (entità, risorse, ecc.)
        random.seed(self.random_seed)
        self.entity_arrived = 0    # Contatore delle entità totali arrivate nel sistema
    
    def register(self, obj):
        '''Registra un oggetto'''
        class_name = obj.__class__.__name__
        if class_name not in self.registered_objects:
            self.registered_objects[class_name] = []
        self.registered_objects[class_name].append(obj)
        
    def deregister(self, obj):
        '''Deregistra un oggetto '''
        class_name = obj.__class__.__name__
        if class_name in self.registered_objects:
            try:
                self.registered_objects[class_name].remove(obj)
            except ValueError:
                print(f"Oggetto non trovato nella lista di {class_name}.")
        else:
            print(f"Nessun oggetto registrato con classe {class_name}.")


    def search_resource(self, entity_target, resource_type=None):
        '''Cerca risorse disponibili di un tipo specifico che possono servire un'entità target.'''
        available_resources = []
        if resource_type == None:
            print("errore nella ricerca di risorse")
        elif resource_type == "Doctor":
            #print("cerco dottori available:")
            for obj_list in self.registered_objects.values():
                for obj in obj_list:
                    if (isinstance(obj, Doctor) and (obj.state == "idle" or  obj.state == "reserved")
                        and obj.queue == entity_target.queue and obj.capacity_available - entity_target.capacity_req_to_doc >= 0):
                        #print("trovato +1")
                        available_resources.append(obj)
        elif resource_type == "Nurse":
            for obj_list in self.registered_objects.values():
                for obj in obj_list:
                    if isinstance(obj, Nurse) and (obj.store.capacity_available_on_hand - obj.store.capacity_reserved - 1) >= 0 and (obj.state != "failed"):
                        #print("trovato +1")
                        available_resources.append(obj)
        else:
            print("Risorsa non riconosciuta")
        return available_resources
    
    def extract_event(self, sim):
        '''Estrae l'evento con il tempo di occorrenza più basso dalla lista degli eventi futuri.
        Aggiorna l'orologio di simulazione e esegue la logica dell'evento estratto.'''

        if not self.list_of_event:
            return -1
        
        # Ordina la lista degli eventi per tempo di occorrenza 
        self.list_of_event.sort(key=lambda x: x[0])

        # Estrae l'evento più vicino nel tempo
        next_event = self.list_of_event.pop(0)

        event_time = next_event[0]
        event_obj = next_event[1]

        # Aggiorna l'orologio della simulazione
        self.clock = event_time

        # Esegue la logica dell'evento, passando il gestore della simulazione e il tempo corrente
        event_obj.event_manager(sim = self, time_for_event = event_time)
        return event_time 
    
    def create_event_and_insert(self, type_of_event= None, resource_target=None, entity_target=None, queue_target=None, store_target=None, time_for_event=None):
        '''Crea un nuovo oggetto evento del tipo specificato e lo inserisce nella lista degli eventi futuri.
        Calcola anche il tempo di occorrenza dell'evento basandosi sulle distribuzioni appropriate.'''
        if time_for_event is None or type_of_event is None:
            print("Errore: impossibile creare evento, parametri non esplicitati correttamente")
            return 0
        
        if type_of_event ==  "StartProcessDoctor":
            new_event_start_process = StartProcessDoctor(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                queue_current=queue_target,
            )

        elif type_of_event ==  "StartProcessNurse":
            new_event_start_process = StartProcessNurse(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                store_current=store_target,
            )

        elif type_of_event == "EndProcessNurse":
            time_for_event =self._schedule_next_time(time_for_event, type_distr = "norm", par_list = [self.mu_process_2, self.sig_process_2])
            new_event_start_process = EndProcessNurse(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                store_current=store_target,
            )
            
        elif type_of_event == "EndProcessDoctor":
            time_for_event =  self._schedule_next_time(time_for_event, type_distr = "exp", par_list = self.par_process_1)
            new_event_start_process = EndProcessDoctor(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                queue_current=queue_target,
            )

        elif type_of_event == "Arrival":
            time_for_event = self._schedule_next_time(time_for_event, type_distr="exp", par_list=self.par_arrival)
            new_event_start_process = Arrival(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                queue_current=queue_target,
            )

        elif type_of_event == "Failure":
            time_for_event = self._schedule_next_time(time_for_event , type_distr = "exp", par_list = self.par_failure)
            new_event_start_process = Failure(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                queue_current=queue_target,
            )

        elif type_of_event == "Recovery": 
            time_for_event = self._schedule_next_time(time_for_event , type_distr = "exp", par_list = self.par_recovery)
            new_event_start_process = Recovery(
                sim=self,
                resource_current=resource_target,
                entity_current=entity_target,
                queue_current=queue_target,
            )

        else:
            print("evento non riconosciuto")
        time_event_and_info = [time_for_event, new_event_start_process]

        self.list_of_event.append(time_event_and_info)
        
    
    def _schedule_next_time(self,time_prec, type_distr, par_list):
        '''Metodo privato per calcolare il tempo di occorrenza del prossimo evento
        basandosi su una distribuzione di probabilità specificata.'''

        if type_distr == "norm":
            mu = par_list[0]
            sig = par_list[1]
            dist = NormalDistribution(mu=mu, sig=sig)
            interarrival_time = dist.sample()

        elif type_distr == "exp":
            dist = ExponentialDistribution(lambd=par_list)
            interarrival_time = dist.sample()

        else: 
            print("Distribuzione non supportata")
            return time_prec  
        
        return time_prec + interarrival_time
    

    def reset(self):
        '''Metodo per resettare la simulazione'''

        # Resettare lo stato degli oggetti presenti nella simulazione
        for class_list in self.registered_objects.values():
            for obj in class_list:
                if hasattr(obj, "reset"):   
                    obj.reset()

        # Resettare lo stato interno dell’ambiente
        self.clock = 0
        self.list_of_event = []
        self.registered_objects = {}

    def reset_all_statistics(self):
        '''Resetta tutte le collezioni di dati statistiche (istanze di DataCollection)
        all'interno di una data lista di oggetti.'''
        for obj_list in self.registered_objects.values():
            for obj in obj_list:
                for attr_name in dir(obj):
                    if not attr_name.startswith("__"):
                        attr = getattr(obj, attr_name)
                        if isinstance(attr, DataCollection):
                            attr.reset()
            
    def initialize_first_events(self, queue_1, list_doc, list_nurse):
        ''' Inizializza la lista degli eventi futuri con gli eventi iniziali della simulazione.
        Questo include il primo arrivo di un paziente e gli eventi di guasto iniziali
        per tutti i dottori e gli infermieri. '''
        self.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=self, queue=queue_1), 
                                    queue_target = queue_1, store_target = None, time_for_event = 1)
        for doc in list_doc:
            self.create_event_and_insert(type_of_event = "Failure", resource_target = doc, entity_target = None, 
                                    queue_target = None, store_target = None, time_for_event = 1)
        for nurs in list_nurse:
            self.create_event_and_insert(type_of_event = "Failure", resource_target = nurs, entity_target = None, 
                                    queue_target = None, store_target = None, time_for_event = 1)
            

    def stamp_list_events(self):
        ''' Stampa la lista degli eventi futuri ordinati per tempo di occorrenza.'''
        lista_eventi = self.list_of_event
        print("Lista degli eventi:")
        for time, event in sorted(lista_eventi, key=lambda x: x[0]):
            nome_evento = getattr(event, 'name', type(event).__name__)
            print(f"- Tempo: {time:.1f}, Evento: {nome_evento}")

    def visualize_queue_doctors_nurses(self):
        ''''Visualizza lo stato attuale della coda, dei dottori e degli infermieri'''
        queues = self.registered_objects.get("Queue", [])
        if not queues:
            print("No queue registered.")
            return
        queue = queues[0]  
        
        doctors_list = self.registered_objects.get("Doctor", [])
        nurses_list = self.registered_objects.get("Nurse", [])
        current = queue.tail.successor
        queue_str = "Queue Tail -> "
        while current != queue.head:
            priority = getattr(current.entity, "priority", "?")
            patient_name = getattr(current.entity, "name", "Unknown")
            queue_str += f"[P{priority} {patient_name}] -> "
            current = current.successor
        queue_str += "Queue Head"
        
        max_width = max(len(queue_str), 60)
        pos_queue_head = queue_str.find("Queue Head")
        if pos_queue_head == -1:
            pos_queue_head = len(queue_str) // 2 
        
        print(queue_str.center(max_width))
        indent = " " * pos_queue_head
        print(f"{indent}↓")
        print(f"{indent}Doctors Processing Patients:")
        for doc in doctors_list:
            patients_processing = getattr(doc, "entity_processed", [])
            patient_names = [getattr(p, "name", "Unknown") for p in patients_processing]
            state = doc.state
            line = f"{doc.name} [{state}]: " + (", ".join(patient_names) if patient_names else "Idle")
            print(f"{indent}{line}")
        print(f"\n{indent}↓")
        print(f"{indent}Patients transitioning from doctors to nurses")
        for nurse in nurses_list:
            patients_assigned = getattr(nurse, "entity_who_reserved", [])
            patient_names = [getattr(p, "name", "Unknown") for p in patients_assigned]
            line = f"{nurse.name} : " + (", ".join(patient_names) if patient_names else "No patient")
            print(f"{indent}{line}")
        print(f"\n{indent}↓")
        print(f"{indent}Nurses Processing Patients:")
        for nurse in nurses_list:
            patients_assigned = getattr(nurse, "entity_processed", [])
            patient_names = [getattr(p, "name", "Unknown") for p in patients_assigned]
            state = nurse.state
            line = f"{nurse.name} [{state}]: " + (", ".join(patient_names) if patient_names else "No patient")
            print(f"{indent}{line}")

        





        
    