from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SimulationManager import SimulationManager
from DataCollection import *


class QueueMember:
    '''  Rappresenta un membro all'interno di una coda.
    Ogni QueueMember incapsula un'entità (es. un paziente) e gestisce i riferimenti
    al membro successivo e precedente nella coda, formando una lista doppiamente linkata.'''
    def __init__(self, entity_which_rapresent, enter_time=0.0):
        self.entity = entity_which_rapresent   # L'entità associata (es. paziente
        self.enter_time = enter_time   # Tempo di ingresso dell'entità in coda
        self.successor = None    # Riferimento al QueueMember successivo nella coda
        self.predecessor = None  # Riferimento al QueueMember precedente nella coda

    def __eq__(self, other):
        '''   Definisce l'operatore di uguaglianza per gli oggetti QueueMember.
        Due QueueMember sono considerati uguali se rappresentano la stessa entità.'''
        return isinstance(other, QueueMember) and self.entity == other.entity

class Queue:
    '''  Implementa una coda a priorità doppiamente linkata per gestire le entità.
    Le entità vengono inserite in base alla loro priorità e al tempo di arrivo (FIFO per stessa priorità).
    La coda mantiene anche statistiche sulla sua lunghezza e sulle entità perse.'''
    entity_counter = 0
    def __init__(
        self,
        sim: 'SimulationManager' = None,
        capacity_max: float = None
    ):
        self.name = self.name_unique()
        self.lost_entities = DataStat( name = "lost_patient_in"+self.name)  # Contatore delle entità perse per "balking" (non entrano in coda perché piena)
        self.lost_entities_after_queue =  DataStat( name = "lost_patient_after_queue"+self.name)  # Contatore delle entità perse dopo essere uscite dalla coda (es. non trovano risorse (infermieri) successive)
        self.sim = sim
        self.capacity_max = capacity_max   # Lunghezza massima della coda
        self.current_length = 0  # Lunghezza attuale della coda

        # Nodi "sentinella": non contengono entità reali,
        # ma semplificano le operazioni di inserimento/rimozione.
        self.tail = QueueMember(entity_which_rapresent=None)
        self.head = QueueMember(entity_which_rapresent=None)

        # Inizializza la lista doppiamente linkata vuota con i nodi sentinella
        self.tail.successor = self.head
        self.head.predecessor = self.tail

        # Collezioni di dati per le statistiche della coda
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
        self.entity_counter = 0

    def visualize_queue(self):
        '''  Stampa una rappresentazione testuale della coda, mostrando la priorità
        e il nome di ogni paziente in ordine.'''
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
        ''' Inserisce una nuova entità (paziente) nella coda, mantenendo l'ordine di priorità.
        Le entità con priorità più alta hanno precedenza.
        A parità di priorità, l'ordine è FIFO.'''

        self.len_queues.add_to_data_collected( time_to_insert = time_for_event, value_to_add=self.current_length+1)

        node_to_insert = QueueMember(entity_which_rapresent = entity_target, enter_time = time_for_event )

        # Caso 1: Coda vuota
        if self.current_length == 0:
            node_to_insert.successor = self.head
            node_to_insert.predecessor = self.tail
            self.tail.successor = node_to_insert
            self.head.predecessor = node_to_insert

        # Caso 2: Inserimento all'inizio della coda (priorità più alta del primo elemento)
        elif node_to_insert.entity.priority <= self.tail.successor.entity.priority:
            current_node = self.tail.successor 
            current_node.predecessor = node_to_insert
            node_to_insert.successor = current_node
            node_to_insert.predecessor = self.tail
            self.tail.successor = node_to_insert 

        # Caso 3: Inserimento alla fine della coda (priorità più bassa dell'ultimo elemento)
        elif node_to_insert.entity.priority > self.head.predecessor.entity.priority:
            current_node = self.head.predecessor
            current_node.successor = node_to_insert
            node_to_insert.successor = self.head
            node_to_insert.predecessor = current_node 
            self.head.predecessor = node_to_insert 

        # Caso 4: Inserimento nel mezzo della coda
        else:
            current_node = self.tail.successor
            next_node = current_node.successor
            while next_node != self.head:  
                if (node_to_insert.entity.priority < next_node.entity.priority) or (node_to_insert.entity.priority == next_node.entity.priority and node_to_insert.enter_time > next_node.enter_time):
                    node_to_insert.successor = next_node
                    node_to_insert.predecessor = current_node
                    next_node.predecessor = node_to_insert
                    current_node.successor = node_to_insert
                    break
                current_node = current_node.successor
                next_node = current_node.successor
            
        # Aggiornamento delle variabili di stato dell'entità e della coda
        entity_target.state = "wait"
        entity_target.queue = self   # per tenere traccia in quale coda è stato
        self.current_length += 1

        # trovo obj: la prima entità che si incontra con medesima priorità dell'oggetto da inserire

    def remove_first(self, sim):
        ''' Rimuove l'entità in testa alla coda.
        Aggiorna le statistiche sulla lunghezza della coda e il tempo di permanenza.'''

        node_to_remove = self.head.predecessor   # Il nodo da rimuovere è quello prima del nodo sentinella 'head'

        if self.current_length < 0 or self.tail.successor == self.head:
            print("Errore, grandezze riferite alla coda non feasible")

        self.current_length -= 1  # Decrementa la lunghezza attuale della coda

        # Rimozione nodo
        node_to_remove = self.head.predecessor
        precedent_node = node_to_remove.predecessor
        self.head.predecessor = precedent_node
        precedent_node.successor = self.head

        # Aggiorna le statistiche della coda
        self.len_queues.add_to_data_collected(time_to_insert = sim.clock, value_to_add=self.current_length)
        self.length_of_stay.add_to_data_collected( value_to_add = (sim.clock - node_to_remove.enter_time))

        return node_to_remove.entity
    
    
    def first_entity_in_queue(self):
        ''' Restituisce l'entità che si trova in testa alla coda (quella che sarà servita per prima)
        senza rimuoverla.'''
        if self.head.predecessor == self.tail:
            print("coda vuota")
            return -1
        return self.head.predecessor.entity
    
    @classmethod
    def name_unique(cls):
        cls.entity_counter += 1
        return f"Queue_{cls.entity_counter}"
    

