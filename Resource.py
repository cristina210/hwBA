from SimulationManager import *
from DataCollection import *
import random

# CHECKATO
# punto delicato: 
# capacity_req_to_doc

class Resource:
    def __init__(self, sim = None, store = None):
        self.sim = sim
        self.state = "idle"   # idle, busy, failed, reserved
    def update_resource_after_event(self, type_of_update, entity_target, *args, **kwargs):
        pass
    def reset(self):
        pass

class Doctor(Resource):
    entity_counter = 0
    def __init__(self, sim=None, capacity_max = 1, queue = None):
        super().__init__(sim=sim)
        self.queue = queue   # coda di attesa alla cui testa c'è la risorsa
        self.capacity_max = capacity_max
        self.capacity_available = self.capacity_max
        self.entity_who_reserved = []
        self.entity_processed = []
        self.name = self.name_unique()
        if self.sim is not None:
            self.sim.register(self)
        if (self.queue == None):
            print("Errore nella creazione della risorsa dottore")
    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Doctor_{cls.entity_counter}"

    def update_resource_after_event(self, type_of_update, entity_target):
        #print(f"Update_resource_after_event called with: {type_of_update}")
        #print(type_of_update)
        if type_of_update == "StartProcess":
            # aggiorno le variabili di stato della risorsa
            self.entity_processed.append(entity_target)
            self.capacity_available = self.capacity_available - entity_target.capacity_req_to_doc   # nel caso di default la capacità richiesta è 1
            # eventuali statistiche relative al dottore (es capacità nel tempo)
            if self.capacity_available < 0:
                print("Errore capacità negativa del dottore")
            if self.capacity_available == 0:    # nel caso di default di capacità max = 1, questo if è ininfluente
                self.state = "busy"
        elif type_of_update == "EndProcess":
            self.capacity_available= self.capacity_available  + entity_target.capacity_req_to_doc
            self.entity_processed.remove(entity_target)
            self.state = "idle"
        elif type_of_update == "EndProcess2":
            self.state = "reserved"
            self.entity_who_reserved.append(entity_target)
        elif type_of_update == "Failure":
            self.state = "failed"
        elif type_of_update == "Recovery":
            self.state = "idle"
        elif type_of_update == "Arrival":
            self.state = "reserved"
            self.entity_who_reserved.append(entity_target)
        else:
            print(f"update non riconosciuto: {type_of_update}")

    def reset(self):
        self.capacity_available = self.capacity_max
        self.state = "idle"

class Nurse(Resource):
    entity_counter = 0
    def __init__(self, sim=None, skill_level=1, store = None):
        super().__init__(sim=sim)
        self.skill_level = skill_level
        self.store = store   # stanza a cui un infermiere è associato
        self.name = self.name_unique()
        self.entity_who_reserved = []   # paziente che ha riservato il posto
        self.entity_processed = []
        self.num_pat = DataTime( name="num_patients"+self.name) 
        self.delta_skill_level = DataWithoutTime(name="delta_skill_level"+self.name)
        if self.sim is not None:
            self.sim.register(self)
        if (self.store == None):
            print("Errore nella creazione della risorsa nurse")
    
    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Nurse_{cls.entity_counter}"
    
    def update_resource_after_event(self, type_of_update, entity_target):
        if type_of_update == "StartProcess":
            self.state = "busy"
            self.entity_who_reserved.remove(entity_target)
            self.entity_processed.append(entity_target)
        elif type_of_update == "EndProcess":
            self.delta_skill_level.add_to_data_collected(value_to_add = min(0,(entity_target.skill_level_req - self.skill_level)))
            self.state = "idle"
            self.entity_processed.remove(entity_target)
        elif type_of_update == "Failure":
            self.state = "failed"
        elif type_of_update == "Recovery":
            self.state = "idle"
        elif type_of_update == "EndProcessDoctor":
            self.state = "reserved"
            self.entity_who_reserved.append(entity_target)
        else:
            print("update non riconosciuto")
        
    def reset(self):
        self.state = "idle"
        
