from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from Queues import Queue
from Store import Store
import random



class Entity:
    '''Classe astratta che rappresenta un'entità generica all'interno del sistema di simulazione.
    Definisce le proprietà comuni a tutte le entità come lo stato e la priorità.'''
    def __init__(
        self,
        sim: SimulationManager = None,
        queue: Queue = None,   
        store: Store = None     
    ):
        self.sim = sim
        self.queue = queue  # Riferimento all'ultima coda visitata dall'entità
        self.store = store  # Riferimento all'ultimo store visitato dall'entità
        self.state = "active"   # Stato attuale dell'entità: "active", "wait", "processing"
    def _create_priority(self):
        '''Genera una priorità casuale per l'entità.'''
        return random.randint(1, 3)

class Patient(Entity):
    ''' Classe concreta che rappresenta un paziente.
    Estende la classe Entity aggiungendo proprietà specifiche del paziente
    come requisiti di capacità, tempo di permanenza in store e livello di skill richiesto.'''
    entity_counter = 0
    def __init__(
        self,
        sim: SimulationManager = None,
        queue: Queue = None,
        store: Store = None,
        capacity_req_to_doc: int = 1   # nel caso di default la capacità richiesta è 1
    ):
        super().__init__(sim=sim, queue=queue, store=store)
        if self.sim is not None:
            self.sim.register(self)
        self.priority = self._create_priority()
        self.resources = None    # Risorsa assegnata al paziente
        self.name = self.name_unique()
        self.length_of_stay_room = self._create_length_of_stay()   # Tempo di permanenza richiesto nella stanza
        self.skill_level_req = self._generate_skill_level()   # Livello di skill richiesto
        self.capacity_req_to_doc = capacity_req_to_doc    # Capacità richiesta al medico
    
    def _create_capacity(self):
        return random.randint(1, 4)
    
    def _create_length_of_stay(self):
        return random.randint(1, 4)
    
    def _generate_skill_level(self):
        return random.randint(1, 4)
    
    def update_entity_after_event(self, type_of_update):
        '''Aggiorna lo stato del paziente in base al tipo di evento che si è verificato.'''
        if type_of_update == "StartProcess":
            self.state = "processing"
        elif type_of_update == "EndProcess":
            self.state = "active"
        elif type_of_update == "Enter_in":
            self.state = "wait"
        else:
            print("update non riconosciuto")

    def reset(self):
        self.entity_counter = 0
   
    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Patient_{cls.entity_counter}"
        
        

        
        
    