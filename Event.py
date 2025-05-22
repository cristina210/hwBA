from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from Entity import *
from Queues import *
from Resource import *
from Entity import *
from DataCollection import *

class Event:
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        self.entity = entity_current   # entità su cui si ripercuote l'evento (potrebbe anche non esserci come nel caso di failure)
        self.resource = resource_current   # risorsa impattata dall'evento   
        self.sim = sim
        self.state = "idle"
        self.queue = queue_current
        self.store = store_current
    def event_manager(self, time_for_event, *args, **kwargs):
        pass

class Arrival(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        super().__init__(
            sim=sim,
            entity_current=entity_current,
            resource_current=resource_current,
            queue_current=queue_current,
            store_current=store_current
        )
        self.name = "Arrival"

    def event_manager(self, sim, time_for_event):
        entity_target = self.entity
        print("QUI")
        print("QUI")
        print(entity_target.queue)
        queue_target = self.queue 
        # registro l'entità nel registro della simulazione
        self.sim.register(entity_target)
        # lista dei dottori che possono operare
        print("list doc available")
        list_doctor_available = sim.search_resource(entity_target = entity_target, resource_type = "Doctor")
        print("lunghezza coda")
        print(queue_target.current_length)
        if queue_target.current_length == 0 and list_doctor_available : 
            print("Non c'è ancora nessuno in coda")
            # -> se non ci sono entità in coda e ci sono dottori disponibili allora processo subito l'entità
            resource_req = list_doctor_available[0]
            # schedulo evento inizio processamento "immediato", ovvero tempo di processamento = clock 
            sim.create_event_and_insert(type_of_event = "StartProcessDoctor", resource_target = resource_req, 
                                        entity_target = entity_target, queue_target = queue_target, store_target = None,
                                          time_for_event = time_for_event)
            return 0
        if queue_target.current_length >= queue_target.capacity_max:  # l'entità non si mette in coda balking
            # -> se la coda ha raggiunto capacità massima il cliente non si mette in coda (balking)
            queue_target.lost_entities.update_stat_sum(value_to_add=1)
            self.sim.deregister(entity_target)
            return 0
        # -> l'entità si mette in coda
        queue_target.insert_in_queue(entity_target, time_for_event) 
        # schedulazione evento "Arrival"
        sim.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=sim, queue=queue_target), 
                                    queue_target = queue_target, store_target = None, time_for_event = time_for_event)

class StartProcessDoctor(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        super().__init__(
            sim=sim,
            entity_current=entity_current,
            resource_current=resource_current,
            queue_current=queue_current,
            store_current=store_current
        )
        self.name = "StartProcessDoctor"
    def event_manager(self, sim, time_for_event):
        resource_target = self.resource
        entity_target = self.entity
        queue_target = self.queue
        if resource_target.state != "idle":
            print("risorsa prenotata per processamento non più disponibile, potrebbe succedere quando ci sono eventi contemporanei.")
            sim.deregister(entity_target)
            return
        if queue_target == None:
            print("coda non valida")
        if not isinstance(resource_target, Doctor):
            print("risorsa non valida")
        # Aggiornamento variabili di stato
        print("Dottore che processa:")
        print(resource_target.name)
        resource_target.update_resource_after_event(type_of_update = "StartProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "StartProcess")
        # Aggiornamento coda: rimuovere il primo elemento
        if queue_target.current_length != 0: 
            # -> non sono nel caso in cui l'entità viene immediatamente processata senza entrare in coda
            entity_target = queue_target.remove_first(sim) 
        # Schedulazione evento "EndProcess"
        sim.create_event_and_insert(type_of_event = "EndProcessDoctor", resource_target = resource_target,
                                     entity_target = entity_target, queue_target = queue_target, store_target = None,
                                       time_for_event = time_for_event)
        

class StartProcessNurse(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        super().__init__(
            sim=sim,
            entity_current=entity_current,
            resource_current=resource_current,
            queue_current=queue_current,
            store_current=store_current
        )
        self.name = "StartProcessNurse"
    def event_manager(self, sim, time_for_event):
        resource_target = self.resource
        entity_target = self.entity
        store_target = self.store
        if resource_target.state != "idle":
            print("risorsa prenotata per processamento non più disponibile, potrebbe succedere quando ci sono eventi contemporanei.")
            sim.deregister(entity_target)
            return
        if store_target == None:
            print("store non valido")
        if not isinstance(resource_target, Nurse):
            print("risorsa non valida")
        # Aggiornamento variabili di stato
        resource_target.update_resource_after_event(type_of_update = "StartProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "StartProcess")
        # Aggiornamento store
        store_target.add_in_store(self, entity_target, sim)
        # Schedulazione evento "EndProcess"
        sim.create_event_and_insert(type_of_event = "EndProcessNurse", resource_target = resource_target,
                                     entity_target = entity_target, queue_target = None, store_target = store_target,
                                       time_for_event = sim.clock + entity_target.length_of_stay_room)


class EndProcessDoctor(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        super().__init__(
            sim=sim,
            entity_current=entity_current,
            resource_current=resource_current,
            queue_current=queue_current,
            store_current=store_current
        )
        self.name = "EndProcessDoctor"
    def event_manager(self, sim, time_for_event):
        # aggiornare variabili di stato
        resource_target = self.resource
        entity_target = self.entity
        queue_target = self.queue
        if queue_target == None:
            print("coda non valido")
        if not isinstance(resource_target, Doctor):
            print("risorsa non valida")
        resource_target.update_resource_after_event(type_of_update = "EndProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "EndProcess")
        # Schedulazione evento StartProcess (eventuale: deve esserci qualcuno in coda e ci devono essere sufficienti risorse)
        if queue_target.current_length > 0:
            # -> c'è qualcuno in coda
            entity_for_the_new_processing = queue_target.first_entity_in_queue()
            list_resources_available = sim.search_resource(entity_target = entity_for_the_new_processing, resource_type = "Doctor")
            if list_resources_available: # ci sono risorse available
                 # Schedulo evento "StartProcess"
                 sim.create_event_and_insert(type_of_event = "StartProcessDoctor", resource_target = list_resources_available[0], 
                                             entity_target = entity_target, queue_target = queue_target, store_target = None, 
                                             time_for_event = time_for_event)
            else:
                pass 
                # idea schedulare uno start quando esiste almeno una risorsa attiva (dottore) che può processare il paziente presente in
                # coda
                # in realtà forse non è un problema perchè anche se non rischedulo un nuovo start, prima o poi se mi trovo nella situa in cui
                # non posso processare perchè risorsa occupata (e lo sono se sono in questo else) 
                # allora vuol dire che prima o poi ci sarà un evento end_process e quindi un nuovo start
        if entity_target.store == None: 
            # -> l'entità non è ancora andata nella stanza (store) per il post operazione:
            #  se non ci sono posti liberi allora mando a casa il paziente, altrimenti inizio un processo rappresentante il soggiorno del paziente nella stanza
            list_available_nurses = sim.search_resource(entity_target = entity_target, resource_type = "Nurse")
            if not list_available_nurses:
                # -> non ci sono posti liberi
                sim.deregister(entity_target)
            else:
                # Schedulazione evento StartProcess (considero un delay temporale costante di 2min)
                sim.create_event_and_insert(type_of_event = "StartProcessNurse", resource_target = list_available_nurses[0], 
                                            entity_target = entity_target, queue_target = None, store_target = list_available_nurses[0].store, 
                                            time_for_event = time_for_event + 2)
        else:
            # l'entità ha finito il suo ciclo
            sim.deregister(entity_target)
        

class EndProcessNurse(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        super().__init__(
            sim=sim,
            entity_current=entity_current,
            resource_current=resource_current,
            queue_current=queue_current,
            store_current=store_current
        )
        self.name = "EndProcessNurse"
    def event_manager(self, sim, time_for_event):
        # aggiornare variabili di stato
        resource_target = self.resource
        entity_target = self.entity
        store_target = self.store
        if store_target == None:
            print("store non valido")
        if not isinstance(resource_target, Nurse):
            print("risorsa non valida")
        # Aggiornamento variabili di stato
        resource_target.update_resource_after_event(type_of_update = "EndProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "EndProcess")
        # Aggiornamento store
        store_target.remove_from_store(entity_target, sim)
        # Cancellazione entità (uscita dal sistema)
        sim.deregister(entity_target)

class Failure(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
                ):
        super().__init__(
    sim=sim,
    entity_current=entity_current,
    resource_current=resource_current,
    queue_current=queue_current,
    store_current=store_current
)
        self.name = "Failure"
    def event_manager(self, sim, time_for_event):
        # Aggiornare variabili di stato
        self.resource.update_resource_after_event(type_of_update="Failure",entity_target=None)
        # Schedulazione evento EventRecovery
        sim.create_event_and_insert(type_of_event = "Recovery", resource_target = self.resource, time_for_event = time_for_event)
        # Schedulazione evento Failure
        sim.create_event_and_insert(type_of_event = "Failure", resource_target = self.resource, time_for_event = time_for_event)


class Recovery(Event):
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
                ):
        super().__init__(
            sim=sim,
            entity_current=entity_current,
            resource_current=resource_current,
            queue_current=queue_current,
            store_current=store_current
                        )
        self.name = "Recovery"
        
    def event_manager(self, sim, time_for_event):
        # Aggiornare variabili di stato
        self.resource.update_resource_after_event( type_of_update="Recovery", entity_target=None)
