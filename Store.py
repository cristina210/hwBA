from Entity import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from DataCollection import *
# CHECK

class Store:
    entity_counter = 0
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        capacity_max: float = None
    ):
        self.name = self.name_unique()
        self.entity_in_store = [] # lista delle entità in quel momento
        self.sim = sim
        self.capacity_max = capacity_max
        self.capacity_available_on_hand = capacity_max
        self.capacity_reserved = 0
        self.dim_store = DataTime( name="how_many_people_in_store_over_time"+self.name) 
        if self.sim is not None:
            self.sim.register(self)

    def reset(self):
        self.entity_in_store = []
        self.capacity_available = self.capacity_max
        self.entity_counter = 0
            
    def add_in_store(self, entity_target, sim):
        # Aggiornamento variabili di stato
        self.capacity_reserved = self.capacity_reserved - 1
        entity_target.store = self
        self.entity_in_store.append(entity_target)
        # aggiorno statistiche
        self.capacity_available_on_hand = self.capacity_available_on_hand - 1
        self.dim_store.add_to_data_collected(time_to_insert=sim.clock, value_to_add = (self.capacity_max - self.capacity_available_on_hand)) 
        

    def remove_from_store(self, entity_target, sim):
        if entity_target not in self.entity_in_store:
            print("entità non presente nello store")
        else:
            self.entity_in_store.remove(entity_target)
            # aggiorno statistiche
            self.capacity_available_on_hand = self.capacity_available_on_hand + 1
            self.dim_store.add_to_data_collected(time_to_insert=sim.clock, value_to_add = (self.capacity_max - self.capacity_available_on_hand)) 
        
    def add_capacity_reserved(self):
        self.capacity_reserved = self.capacity_reserved +  1
        

    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Store_{cls.entity_counter}"