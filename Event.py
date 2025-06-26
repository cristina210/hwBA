from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from Entity import *
from Queues import *
from Resource import *
from Entity import *
from DataCollection import *

class Event:
    ''' Classe astratta che rappresenta un evento generico all'interno della simulazione.
    Ogni evento ha un impatto su entità, risorse, code o store e viene gestito
    dal SimulationManager.'''
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        entity_current: Entity = None,
        resource_current: Resource = None,
        queue_current: Queue = None,
        store_current: Store = None
    ):
        self.entity = entity_current        # L'entità su cui l'evento ha un impatto (può essere None)
        self.resource = resource_current    # La risorsa impattata dall'evento (può essere None)
        self.sim = sim                      # Riferimento al gestore della simulazione
        self.queue = queue_current          # La coda associata all'evento (può essere None)
        self.store = store_current          # Lo store (es. stanza) associato all'evento (può essere None)
    def event_manager(self, time_for_event, *args, **kwargs):
        ''' Metodo astratto per la gestione logica dell'evento.
            Questo metodo è implementato da ogni sottoclasse concreta di Evento.
            Args: time_for_event (float): Il tempo di simulazione in cui l'evento si verifica.'''
        pass

class Arrival(Event):
    '''  Classe che rappresenta un evento di arrivo di una nuova entità (paziente) nel sistema.
    Gestisce l'inserimento dell'entità in coda o il suo immediato processamento se le risorse sono disponibili.'''
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
        '''Gestisce la logica dell'evento di arrivo.
        Incrementa il contatore delle entità arrivate, tenta di processare immediatamente
        o inserisce l'entità in coda, o la perde per balking. Schedula il prossimo arrivo.'''
        entity_target = self.entity
        queue_target = self.queue 
        sim.entity_arrived = sim.entity_arrived + 1
        self.sim.register(entity_target)

        # Cerca i dottori disponibili per processare l'entità
        list_doctor_available = sim.search_resource(entity_target = entity_target, resource_type = "Doctor")

        # Condizione: la coda è vuota e ci sono dottori disponibili
        if queue_target.current_length == 0 and list_doctor_available : 
            # -> Se non ci sono entità in coda e ci sono dottori disponibili, processa subito l'entità
            resource_req = list_doctor_available[0]

            # Prenota la risorsa (dottore) per l'entità
            resource_req.update_resource_after_event(type_of_update = "Arrival", entity_target = entity_target)

            # Schedula l'evento di inizio processamento "immediato" (al tempo corrente)
            sim.create_event_and_insert(type_of_event = "StartProcessDoctor", resource_target = resource_req, 
                                        entity_target = entity_target, queue_target = queue_target, store_target = None,
                                          time_for_event = time_for_event)
            
            # Schedula il prossimo evento di arrivo
            sim.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=sim, queue=queue_target), 
                                    queue_target = queue_target, store_target = None, time_for_event = time_for_event)
            return 0
        
        # Condizione: la coda ha raggiunto la capacità massima (balking)
        if queue_target.current_length >= queue_target.capacity_max:
            # -> Se la coda è piena, l'entità non si mette in coda (balking)
            queue_target.lost_entities.update_stat_sum(value_to_add=1) # Incrementa il contatore delle entità perse
            self.sim.deregister(entity_target)

            # Schedula il prossimo evento di arrivo
            sim.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=sim, queue=queue_target), 
                                    queue_target = queue_target, store_target = None, time_for_event = time_for_event)
            return 0
        
        # -> l'entità si mette in coda
        queue_target.insert_in_queue(entity_target, time_for_event) 
        
        # Schedula il prossimo evento di arrivo
        sim.create_event_and_insert(type_of_event = "Arrival", resource_target = None, entity_target = Patient(sim=sim, queue=queue_target), 
                                    queue_target = queue_target, store_target = None, time_for_event = time_for_event)

class StartProcessDoctor(Event):
    '''  Classe che rappresenta l'evento di inizio del processo di un paziente da parte di un medico.
    Gestisce l'aggiornamento dello stato del medico e del paziente, e la rimozione del paziente dalla coda'''
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
        ''' Gestisce la logica dell'evento di inizio processamento da parte del medico.
        Aggiorna gli stati di risorsa ed entità, rimuove l'entità dalla coda e
        schedula l'evento di fine processamento.'''
        
        resource_target = self.resource
        entity_target = self.entity
        queue_target = self.queue

        # Controllo di coerenza: la risorsa dovrebbe essere disponibile o prenotata per questa entità.
        if resource_target.state != "idle" and entity_target not in resource_target.entity_who_reserved:
            print("Errore, risorsa prenotata per il paziente non più disponibile")
            sim.deregister(entity_target)
            return
        if queue_target == None:
            print("coda non valida")
        if not isinstance(resource_target, Doctor):
            print("risorsa non valida")

        # Aggiornamento delle variabili di stato per dottore e entità in questione.
        resource_target.update_resource_after_event(type_of_update = "StartProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "StartProcess")

        # Aggiornamento della coda: rimuove il paziente dalla coda
        if queue_target.current_length != 0: 
            entity_target = queue_target.remove_first(sim) 
        else:
            pass
        
        # Schedulazione dell'evento di fine processamento del medico.
        # Il tempo di fine è il tempo corrente più il tempo di servizio del medico
        sim.create_event_and_insert(type_of_event = "EndProcessDoctor", resource_target = resource_target,
                                     entity_target = entity_target, queue_target = queue_target, store_target = None,
                                       time_for_event = time_for_event)
        

class StartProcessNurse(Event):
    '''Classe che rappresenta l'evento di inizio del processo di un paziente da parte di un infermiere.
    Gestisce l'aggiornamento dello stato dell'infermiere e del paziente, e l'aggiunta del paziente allo store (stanza).'''
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
        '''Gestisce la logica dell'evento di inizio processamento da parte dell'infermiere.
        Aggiorna gli stati di risorsa ed entità, aggiunge l'entità alla stanza e
        schedula l'evento di fine processamento.'''
        resource_target = self.resource
        entity_target = self.entity
        store_target = self.store

        # Controllo di coerenza: la risorsa dovrebbe essere disponibile o prenotata per questa entità.
        if resource_target.state != "idle" and entity_target not in resource_target.entity_who_reserved:
            print("Errore, risorsa prenotata per il paziente non più disponibile")
            sim.deregister(entity_target)
            return
        if store_target == None:
            print("store non valido")
        if not isinstance(resource_target, Nurse):
            print("risorsa non valida")
        
        # Aggiornamento delle variabili di stato dell'infermiere e dell'entità in questione:
        resource_target.update_resource_after_event(type_of_update = "StartProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "StartProcess")
        
        # Aggiornamento dello store: aggiunge il paziente alla stanza.
        store_target.add_in_store(entity_target, sim)
        
        # Schedulazione dell'evento di fine processamento dell'infermiere.
        # Il tempo di fine è il tempo corrente più il tempo di permanenza del paziente nella stanza.
        sim.create_event_and_insert(type_of_event = "EndProcessNurse", resource_target = resource_target,
                                     entity_target = entity_target, queue_target = None, store_target = store_target,
                                       time_for_event = sim.clock + entity_target.length_of_stay_room)


class EndProcessDoctor(Event):
    '''  Sottoclasse che rappresenta l'evento di fine del processo di un paziente da parte di un medico.
    Gestisce la liberazione del medico, la verifica della coda e l'eventuale passaggio del paziente
    alla fase successiva (ricovero in stanza o uscita dal sistema).'''
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
        '''Gestisce la logica dell'evento di fine processamento da parte del medico.
        Libera il medico, tenta di servire il prossimo paziente in coda e
        gestisce il passaggio del paziente alla fase successiva (stanza o uscita).'''

        resource_target = self.resource
        entity_target = self.entity
        queue_target = self.queue
        if queue_target == None:
            print("coda non valido")
        if not isinstance(resource_target, Doctor):
            print("risorsa non valida")

        # Aggiornamento delle variabili di stato:
        resource_target.update_resource_after_event(type_of_update = "EndProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "EndProcess")
        
        # Schedulazione di un eventuale nuovo evento di StartProcess se ci sono pazienti in coda
        # e risorse (dottori) disponibili.
        if queue_target.current_length > 0:
            # -> c'è qualcuno in coda
            entity_for_the_new_processing = queue_target.first_entity_in_queue()  # Vede il primo paziente in coda
            list_resources_available = sim.search_resource(entity_target = entity_for_the_new_processing, resource_type = "Doctor")

            if list_resources_available: 
                # -> Ci sono risorse (dottori) disponibili
                doc_available = list_resources_available[0]
                doc_available.update_resource_after_event(type_of_update = "EndProcess2", entity_target= entity_for_the_new_processing)

                # Schedula l'evento "StartProcessDoctor" per il prossimo paziente
                sim.create_event_and_insert(type_of_event = "StartProcessDoctor", resource_target = doc_available, 
                                            entity_target = entity_for_the_new_processing, queue_target = queue_target, store_target = None, 
                                            time_for_event = time_for_event)
            else:
                # -> Nessun dottore disponibile per il prossimo paziente in coda, il paziente rimane in coda.
                pass 
            
        # Gestione del paziente dopo il trattamento del medico: passaggio alla stanza o uscita dal sistema.
        if entity_target.store == None: 
            # -> L'entità non è ancora andata nella stanza (store) per il post-operazione:
            # Cerca infermieri disponibili per ricoverare il paziente.
            list_available_nurses = sim.search_resource(entity_target = entity_target, resource_type = "Nurse")
            
            if not list_available_nurses:
                # -> Non ci sono infermieri disponibili (e quindi stanze libere associate)
                # Il paziente viene perso perché non ci sono posti sufficienti nelle stanze.
                queue_target.lost_entities_after_queue.update_stat_sum(value_to_add=1)
                sim.deregister(entity_target)

            else:
                # -> Ci sono infermieri disponibili
                nurse_available = list_available_nurses[0]
                
                # Prenotazione della risorsa (infermiere) per il paziente
                nurse_available.update_resource_after_event(type_of_update = "EndProcessDoctor", entity_target= entity_target)
                nurse_available.store.add_capacity_reserved()

                # Schedulazione evento StartProcessNurse (considero un delay temporale costante di 2)
                sim.create_event_and_insert(type_of_event = "StartProcessNurse", resource_target = nurse_available, 
                                            entity_target = entity_target, queue_target = None, store_target = nurse_available.store, 
                                            time_for_event = time_for_event + 2)
        else:
            # l'entità ha finito il suo ciclo
            sim.deregister(entity_target)
        

class EndProcessNurse(Event):
    '''Classe che rappresenta l'evento di fine del processo di un paziente da parte di un infermiere.
    Gestisce la liberazione dell'infermiere e la rimozione del paziente dallo store (stanza),
    segnando la sua uscita definitiva dal sistema.'''
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
        '''Gestisce la logica dell'evento di fine processamento da parte dell'infermiere.
        Libera l'infermiere, rimuove il paziente dallo store e lo deregistra dal simulatore.'''
        resource_target = self.resource
        entity_target = self.entity
        store_target = self.store
        if store_target == None:
            print("store non valido")
        if not isinstance(resource_target, Nurse):
            print("risorsa non valida")

        # Aggiornamento delle variabili di stato dell'infermiere, dell'entità e dello store:
        resource_target.update_resource_after_event(type_of_update = "EndProcess", entity_target = entity_target)
        entity_target.update_entity_after_event(type_of_update = "EndProcess")
        store_target.remove_from_store(entity_target, sim)

        # Cancellazione dell'entità (uscita definitiva dal sistema)
        sim.deregister(entity_target)

class Failure(Event):
    '''  Sottoclasse che rappresenta un evento di guasto (failure) di una risorsa.
    Gestisce il cambio di stato della risorsa a "failed" e schedula l'evento di recupero.
    '''
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
        '''Gestisce la logica dell'evento di guasto di una risorsa (infermiere o dottore).
        Se la risorsa è occupata o prenotata, ri-schedula il guasto.
        Altrimenti, imposta la risorsa come "failed" e schedula il recupero e il prossimo guasto. 
        Quindi si ipotizza che un guasto possa avvenire solo se la risorsa non sta processando un'entità.'''
        if self.resource.state == "busy":
            # -> la risorsa è occupata e rischedulo l'evento failure
            sim.create_event_and_insert(type_of_event = "Failure", resource_target = self.resource, time_for_event = time_for_event)
            return 0
        
        elif self.resource.state == "reserved":
            # -> la risorsa è prenotata e rischedulo l'evento failure
            sim.create_event_and_insert(type_of_event = "Failure", resource_target = self.resource, time_for_event = time_for_event)
            return 0
        
        # -> Avviene il failure
        self.resource.update_resource_after_event(type_of_update="Failure",entity_target=None)
        
        # Schedulazione dell'evento di recupero (quando la risorsa tornerà operativa).
        # Il tempo di recupero è il tempo corrente più il tempo di riparazione della risorsa.
        sim.create_event_and_insert(type_of_event = "Recovery", resource_target = self.resource, time_for_event = time_for_event)

        # Schedulazione del prossimo evento di guasto per questa risorsa.
        # Il tempo del prossimo guasto è il tempo corrente più il tempo fino al prossimo guasto.
        sim.create_event_and_insert(type_of_event = "Failure", resource_target = self.resource, time_for_event = time_for_event)


class Recovery(Event):
    ''' Sottoclasse che rappresenta un evento di recupero (recovery) di una risorsa dopo un guasto.
    Gestisce il ripristino dello stato della risorsa a "idle".'''
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
        # Aggiorna lo stato della risorsa
        self.resource.update_resource_after_event( type_of_update="Recovery", entity_target=None)
