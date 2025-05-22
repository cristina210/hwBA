from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from Queues import Queue
from Store import Store
import random

# CHECKATO

class Entity:
    def __init__(
        self,
        sim: SimulationManager = None,
        queue: Queue = None,    # in quale coda si trova all'inizio l'entità
        store: Store = None     # in quale store si trova all'inizio l'entità
    ):
        self.sim = sim
        self.queue = queue  # presente ultima coda dove l'entità è stata
        self.store = store
        self.state = "active"   # active, wait, processing (volendo possiamo togliere active)
    def _create_priority(self):
        return random.randint(1, 3)

class Patient(Entity):
    entity_counter = 0
    def __init__(
        self,
        sim: SimulationManager = None,
        queue: Queue = None,
        store: Store = None,
        capacity_req_to_doc: int = 1 
    ):
        super().__init__(sim=sim, queue=queue, store=store)
        if self.sim is not None:
            self.sim.register(self)
        self.priority = self._create_priority()
        self.resources = None
        self.name = self.name_unique()
        self.length_of_stay_room = self._create_length_of_stay()
        self.skill_level_req = self._generate_skill_level()
        self.capacity_req_to_doc = capacity_req_to_doc
    
    def _create_capacity(self):
        # esempio semplice
        return random.randint(1, 4)
    
    def _create_length_of_stay(self):
        # esempio semplice
        return random.randint(1, 4)
    
    def _generate_skill_level(self):
        return random.randint(1, 3)
    
    def update_entity_after_event(self, type_of_update):
        if type_of_update == "StartProcess":
            # aggiorno le variabili di stato della risorsa
            self.state = "processing"
        elif type_of_update == "EndProcess":
            # aggiorno le variabili di stato della risorsa
            self.state = "active"
        elif type_of_update == "Enter_in":
            self.state = "wait"
        else:
            print("update non riconosciuto")

    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Patient_{cls.entity_counter}"
        
        

        
        
    