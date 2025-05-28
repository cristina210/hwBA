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
        queue_target = self.queue 
        sim.entity_arrived = sim.entity_arrived + 1
        #print("Arriva il paziente:")
        #print(entity_target.name)
        # registro l'entità nel registro della simulazione
        self.sim.register(entity_target)
        # lista dei dottori che possono operare
        #print("list doc available")
        list_doctor_available = sim.search_resource(entity_target = entity_target, resource_type = "Doctor")
        #print("Queue current length:", queue_target.current_length)
        #print("Queue capacity max:", queue_target.capacity_max)
        if queue_target.current_length == 0 and list_doctor_available : 
            #print("Non c'è ancora nessuno in coda")
            # -> se non ci sono entità in coda e ci sono dottori disponibili allora processo subito l'entità
            resource_req = list_doctor_available[0]
            # Prenoto la risorsa
            #print("Prenoto la risorsa:")
            #print(resource_req.name)
            #print("al paziente:")
            #print(entity_target.name)
            #print(resource_req.state)
            #print(resource_req.entity_who_reserved)
            resource_req.update_resource_after_event(type_of_update = "Arrival", entity_target = entity_target)
            #print(resource_req.state)
            #print([e.name for e in resource_req.entity_who_reserved])
            # schedulo evento inizio processamento "immediato", ovvero tempo di processamento = clock 
            sim.create_event_and_insert(type_of_event = "StartProcessDoctor", resource_target = resource_req, 
                                        entity_target = entity_target, queue_target = queue_target, store_target = None,
                                          time_for_event = time_for_event)
            sim.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=sim, queue=queue_target), 
                                    queue_target = queue_target, store_target = None, time_for_event = time_for_event)
            return 0
        if queue_target.current_length >= queue_target.capacity_max:  # l'entità non si mette in coda balking
            # -> se la coda ha raggiunto capacità massima il cliente non si mette in coda (balking)
            #print("Paziente non entra in coda dai dottori: balking")
            queue_target.lost_entities.update_stat_sum(value_to_add=1)
            self.sim.deregister(entity_target)
            sim.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=sim, queue=queue_target), 
                                    queue_target = queue_target, store_target = None, time_for_event = time_for_event)
            return 0
        # -> l'entità si mette in coda
        # queue_target.visualize_queue()
        #print("Paziente si mette in coda")
        #print("lunghezza coda prima dell'inserimento:")
        #print(queue_target.current_length)
        queue_target.insert_in_queue(entity_target, time_for_event) 
        #print("lunghezza coda dopo l'inserimento:")
        #print(queue_target.current_length)
        # queue_target.visualize_queue()
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
        #print(resource_target.name)
        #print(resource_target.state)
        #print(entity_target.name)
        #print([e.name for e in resource_target.entity_who_reserved])
        if resource_target.state != "idle" and entity_target not in resource_target.entity_who_reserved:
            print("Errore, risorsa prenotata per il paziente non più disponibile")
            sim.deregister(entity_target)
            return
        if queue_target == None:
            print("coda non valida")
        if not isinstance(resource_target, Doctor):
            print("risorsa non valida")
        # Aggiornamento variabili di stato
        #print("Dottore:")
        #print(resource_target.name)
        #print( "Processa:")
        #print(entity_target.name)
        #print("Stato e capacità del dottore prima del processamento")
        #print(resource_target.state)
        #print(resource_target.capacity_available)
        resource_target.update_resource_after_event(type_of_update = "StartProcess", entity_target = entity_target)
        #print("Stato e capacità del dottore dopo il processamento")
        #print(resource_target.state)
        #print(resource_target.capacity_available)
        entity_target.update_entity_after_event(type_of_update = "StartProcess")
        #print("Si osserva la coda:")
        #queue_target.visualize_queue()
        # Aggiornamento coda: rimuovere il primo elemento
        if queue_target.current_length != 0: 
            #print("la coda non era vuota, rimuovo il paziente che inizia il processamento")
            # -> non sono nel caso in cui l'entità viene immediatamente processata senza entrare in coda
            #print("lunghezza coda prima della rimozione:")
            #print(queue_target.current_length)
            entity_target = queue_target.remove_first(sim) 
            #print("lunghezza coda dopo la rimozione:")
            #print(queue_target.current_length)
            #queue_target.visualize_queue()
        else:
            #print("Non rimuovo alcun paziente")
            pass
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
        #print(entity_target.name)
        #print(resource_target.name)
        #print([e.name for e in resource_target.entity_who_reserved])
        if resource_target.state != "idle" and entity_target not in resource_target.entity_who_reserved:
            print("Errore, risorsa prenotata per il paziente non più disponibile")
            sim.deregister(entity_target)
            return
        if store_target == None:
            print("store non valido")
        if not isinstance(resource_target, Nurse):
            print("risorsa non valida")
        #print("Infermiere:")
        #print(resource_target.name)
        #print( "Processa:")
        #print(entity_target)
        # Aggiornamento variabili di stato
        #print("Stato dell'infermiere prima del processamento:")
        resource_target.update_resource_after_event(type_of_update = "StartProcess", entity_target = entity_target)
        #print("Stato dell'infermiere dopo il processamento:")
        entity_target.update_entity_after_event(type_of_update = "StartProcess")
        # Aggiornamento store
        #print("store in cui inserisco il paziente")
        #print(store_target.name)
        #print("capacità available e riservata prima dell'inserimento:")
        #print(store_target.capacity_available_on_hand)
        #print(store_target.capacity_reserved)
        store_target.add_in_store(entity_target, sim)
        #print("capacità available e riservata dopo l'inserimento:")
        #print(store_target.capacity_available_on_hand)
        #print(store_target.capacity_reserved)
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
        #print("Dottore che termina l'operaziore:")
        #print(resource_target.name)
        #print("paziente che termina:")
        #print(entity_target.name)
        #print("Stato e capacità del dottore prima del termine:")
        #print(resource_target.state)
        #print(resource_target.capacity_available)
        resource_target.update_resource_after_event(type_of_update = "EndProcess", entity_target = entity_target)
        #print("Stato del dottore dopo il termine:")
        #print(resource_target.state)
        #print(resource_target.capacity_available)
        entity_target.update_entity_after_event(type_of_update = "EndProcess")
        # Schedulazione evento StartProcess (eventuale: deve esserci qualcuno in coda e ci devono essere sufficienti risorse)
        if queue_target.current_length > 0:
            # -> c'è qualcuno in coda
            #print("visto che c'è qualcuno in coda si schedula un altro starting, cerchiamo dottori available")
            entity_for_the_new_processing = queue_target.first_entity_in_queue()
            list_resources_available = sim.search_resource(entity_target = entity_for_the_new_processing, resource_type = "Doctor")
            if list_resources_available: # ci sono risorse available
                # Prenoto la risorsa
                doc_available = list_resources_available[0]
                #print("Prenoto la risorsa:")
                #print(doc_available.name)
                #print("al paziente:")
                #print(entity_for_the_new_processing.name)
                #print(doc_available.state)
                #print([e.name for e in doc_available.entity_who_reserved])
                doc_available.update_resource_after_event(type_of_update = "EndProcess2", entity_target= entity_for_the_new_processing)
                #print(doc_available.state)
                #print([e.name for e in doc_available.entity_who_reserved])
                # Schedulo evento "StartProcess"
                sim.create_event_and_insert(type_of_event = "StartProcessDoctor", resource_target = doc_available, 
                                            entity_target = entity_for_the_new_processing, queue_target = queue_target, store_target = None, 
                                            time_for_event = time_for_event)
            else:
                pass 
                # idea schedulare uno start quando esiste almeno una risorsa attiva (dottore) che può processare il paziente presente in
                # coda
                # in realtà forse non è un problema perchè anche se non rischedulo un nuovo start, prima o poi se mi trovo nella situa in cui
                # non posso processare perchè risorsa occupata (e lo sono se sono in questo else) 
                # allora vuol dire che prima o poi ci sarà un evento end_process e quindi un nuovo start
        if entity_target.store == None: 
            #print("il paziente appena processato non è ancora stato in stanza post ricovero, schedulo anche l'arrivo dagli infermieri")
            #print(entity_target.name)
            # -> l'entità non è ancora andata nella stanza (store) per il post operazione:
            #  se non ci sono posti liberi allora mando a casa il paziente, altrimenti inizio un processo rappresentante il soggiorno del paziente nella stanza
            list_available_nurses = sim.search_resource(entity_target = entity_target, resource_type = "Nurse")
            if not list_available_nurses:
                # -> non ci sono posti liberi
                #print("non ci sono posti liberi, mando il paziente a casa")
                queue_target.lost_entities_after_queue.update_stat_sum(value_to_add=1)
                sim.deregister(entity_target)
            else:
                # Schedulazione evento StartProcessNurse (considero un delay temporale costante di 2min)
                nurse_available = list_available_nurses[0]
                # Prenoto la risorsa
                #print("Prenoto la risorsa:")
                #print(nurse_available.name)
                #print("al paziente:")
                #print(entity_target.name)
                #print("Cambio di stato dell'infermiere")
                #print(nurse_available.state)
                #print([e.name for e in nurse_available.entity_who_reserved])
                nurse_available.update_resource_after_event(type_of_update = "EndProcessDoctor", entity_target= entity_target)
                #print(nurse_available.state)
                #print([e.name for e in nurse_available.entity_who_reserved])
                #print("Riservo un posto nello store, ecco la capacità riservata:")
                #print(nurse_available.store.capacity_reserved)
                nurse_available.store.add_capacity_reserved()
                #print(nurse_available.store.capacity_reserved)
                sim.create_event_and_insert(type_of_event = "StartProcessNurse", resource_target = nurse_available, 
                                            entity_target = entity_target, queue_target = None, store_target = nurse_available.store, 
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
        #print("store in cui rimuovo il paziente")
        #print(store_target.name)
        resource_target.update_resource_after_event(type_of_update = "EndProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "EndProcess")
        # Aggiornamento store
        #print("capacità available prima della rimozione:")
        #print(store_target.capacity_available_on_hand)
        store_target.remove_from_store(entity_target, sim)
        #print("capacità available dopo la rimozione:")
        #print(store_target.capacity_available_on_hand)
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
        # si ipotizza possa avvenire un failure solo se la risorsa non sta processando una entità
        if self.resource.state == "busy":
            #print("La risorsa (dottore o infermiera) è occupata nel processamento, rischedulo un failure")
            sim.create_event_and_insert(type_of_event = "Failure", resource_target = self.resource, time_for_event = time_for_event)
            return 0
        elif self.resource.state == "reserved":
            #print("La risorsa è prenotata per un processo di una entità, rischedulo il failure")
            sim.create_event_and_insert(type_of_event = "Failure", resource_target = self.resource, time_for_event = time_for_event)
            return 0
        #print("stato prima del failure:")
        #print(self.resource.state)
        self.resource.update_resource_after_event(type_of_update="Failure",entity_target=None)
        #print("stato dopo il failure:")
        #print(self.resource.state)
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
