from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from DataCollection import *

# CHECCATO

class QueueMember:
    def __init__(self, entity_which_rapresent, enter_time=0.0):
        self.entity = entity_which_rapresent   # L'entità associata (es. paziente)
        self.enter_time = enter_time  # Tempo di ingresso in coda
        self.successor = None    # entità che viene dopo in coda
        self.predecessor = None  # entità che viene prima in coda

    def make_successor(self, obj):
        # obj deve essere un altro obj di queue member
        self.successor = obj

    def make_predecessor(self, obj):
        # obj deve essere un altro obj di queue member
        self.predecessor = obj

    # sovrascrivo operatore di uguaglianza
    #def __eq__(self, other_q_member):
    #    return self.entity == other_q_member.entity and self.successor == other_q_member.successor and self.predecessor == other_q_member.predecessor


    def __eq__(self, other):
        return isinstance(other, QueueMember) and self.entity == other.entity

class Queue:
    entity_counter = 0
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        capacity_max: float = None
    ):
        self.name = self.name_unique()
        self.lost_entities = DataStat( name = "lost_patient_in"+self.name)  # contatore delle entità perse (balking)
        self.lost_entities_after_queue =  DataStat( name = "lost_patient_after_queue"+self.name)
        self.sim = sim
        self.capacity_max = capacity_max 
        self.current_length = 0
        # nodi "sentinella", non contengono entità indicano solo la fine e l'inizio della coda!
        self.tail = QueueMember(entity_which_rapresent=None)
        self.head = QueueMember(entity_which_rapresent=None)
        self.tail.successor = self.head
        self.head.predecessor = self.tail
        # Queste 3 quantità sono statistiche
        self.len_queues = DataTime( name="length_over_time_"+self.name) 
        self.length_of_stay = DataWithoutTime( name="length_of_stay"+self.name )
        if self.sim is not None:
            self.sim.register(self)

    def reset(self):
        self.current_length = 0
        self.tail = QueueMember(entity_which_rapresent=None)
        self.head = QueueMember(entity_which_rapresent=None)
        self.tail.successor = self.head
        self.head.predecessor = self.tail

    def visualize_queue(self):
        current = self.tail.successor
        queue_str = "Tail -> "
        while current != self.head:
            priority = getattr(current.entity, "priority", "?")
            patient_name = getattr(current.entity, "name", "?")
            queue_str += f"[P{priority} {patient_name}] ->"
            current = current.successor
        queue_str += "Head"
        print(queue_str)

    def insert_in_queue(self, entity_target, time_for_event):
        # aggiornamento statistiche
        self.len_queues.add_to_data_collected( time_to_insert = time_for_event, value_to_add=self.current_length)
        """Inserisce questo Qmember dopo un altro Qmember (nella stessa coda) in base alla priorità."""
        node_to_insert = QueueMember(entity_which_rapresent = entity_target, enter_time = time_for_event )
        if self.current_length == 0:
            node_to_insert.successor = self.head
            node_to_insert.predecessor = self.tail
            self.tail.successor = node_to_insert
            self.head.predecessor = node_to_insert
        elif node_to_insert.entity.priority <= self.tail.successor.entity.priority:
            current_node = self.tail.successor 
            current_node.predecessor = node_to_insert
            node_to_insert.successor = current_node
            node_to_insert.predecessor = self.tail
            self.tail.successor = node_to_insert 
        elif node_to_insert.entity.priority > self.head.predecessor.entity.priority:
            current_node = self.head.predecessor
            current_node.successor = node_to_insert
            node_to_insert.successor = self.head
            node_to_insert.predecessor = current_node 
            self.head.predecessor = node_to_insert 
        else:
            current_node = self.tail.successor
            next_node = current_node.successor
            while next_node != self.head:   # altri casi sono stati già considerati
                if (node_to_insert.entity.priority < next_node.entity.priority) or (node_to_insert.entity.priority == next_node.entity.priority and node_to_insert.enter_time > next_node.enter_time):
                    # inserisco tra current e next il nodo
                    node_to_insert.successor = next_node
                    node_to_insert.predecessor = current_node
                    next_node.predecessor = node_to_insert
                    current_node.successor = node_to_insert
                    break
                current_node = current_node.successor
                next_node = current_node.successor
                # aggiornamento variabili di stato
        entity_target.state = "wait"
        entity_target.queue = self   # per tenere traccia in quale coda è stato
        self.current_length += 1

        # trovo obj: la prima entità che si incontra con medesima priorità dell'oggetto da inserire

    def remove_first(self, sim):
        # Aggiornare variabili di stato
        node_to_remove = self.head.predecessor
        if self.current_length < 0 or self.tail.successor == self.head:
            print("Errore, grandezze riferite alla coda non feasible")
        # rimuovo il nodo
        self.current_length -= 1
        node_to_remove = self.head.predecessor
        precedent_node = node_to_remove.predecessor
        self.head.predecessor = precedent_node
        precedent_node.successor = self.head
        # Aggiornare statistiche riguardo la coda
        self.len_queues.add_to_data_collected(time_to_insert = sim.clock, value_to_add=self.current_length)
        self.length_of_stay.add_to_data_collected( value_to_add = (sim.clock - node_to_remove.enter_time))
        # Ritorno l'entità associata al nodo rimosso
        return node_to_remove.entity
    
    
    def first_entity_in_queue(self):
        if self.head.predecessor == self.tail:
            print("coda vuota")
            return -1
        return self.head.predecessor.entity
    
    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Queue_{cls.entity_counter}"
    

