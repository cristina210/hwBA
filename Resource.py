from SimulationManager import *
from DataCollection import *

class Resource:
    ''' Classe astratta che rappresenta una risorsa generica all'interno del sistema di simulazione.
    Definisce gli stati comuni (idle, busy, failed, reserved) e l'interfaccia per aggiornare
    lo stato della risorsa in risposta agli eventi.'''
    def __init__(self, sim = None, store = None):
        self.sim = sim
        self.state = "idle"   # idle, busy, failed, reserved
    def update_resource_after_event(self, type_of_update, entity_target, *args, **kwargs):
        ''' Metodo astratto per aggiornare lo stato della risorsa in base a un tipo di evento.
        Questo metodo è implementato nelle sottoclassi.'''
        pass
    def reset(self):
        ''' Metodo astratto per resettare lo stato della risorsa ai valori iniziali.
        E' implementato nelle sottoclassi.'''
        pass

class Doctor(Resource):
    ''' Sottoclasse che rappresenta una risorsa di tipo "Dottore".
    Estende la classe Resource aggiungendo proprietà specifiche come capacità massima,
    coda associata e liste di entità processate o prenotate.'''
    entity_counter = 0
    def __init__(self, sim=None, capacity_max = 1, queue = None):
        super().__init__(sim=sim)
        self.queue = queue                                  # Riferimento alla coda di attesa associata a questo dottore
        self.capacity_max = capacity_max                    # Capacità massima 
        self.capacity_available = self.capacity_max         # Capacità attualmente disponibile
        self.entity_who_reserved = []                       # Lista delle entità che hanno prenotato questa risorsa
        self.entity_processed = []                          # Lista delle entità attualmente in fase di processamento
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
        ''''Aggiorna lo stato del dottore e le sue proprietà in base al tipo di evento.'''

        if type_of_update == "StartProcess":
            # Evento: Inizio del processamento di un paziente
            self.entity_processed.append(entity_target)
            self.capacity_available = self.capacity_available - entity_target.capacity_req_to_doc   
            if self.capacity_available < 0:
                print("Errore capacità negativa del dottore")
            if self.capacity_available == 0:    
                self.state = "busy"

        # La gestione dell'evento di 'fine processo' (EndProcess) è divisa in due tipi di aggiornamento distinti:
        # 1) Aggiornamento di base ("EndProcess"): il dottore rilascia il paziente e la sua capacità viene ripristinata,
        #    tornando "idle". Questo avviene sempre alla fine del trattamento di un paziente.
        # 2) Aggiornamento di prenotazione ("EndProcess2"): il dottore passa allo stato "reserved" se è immediatamente
        #    prenotato da un nuovo paziente. Questo aggiornamento non si verifica sempre: dipende dalla presenza di
        #    pazienti in coda o dalla capacità richiesta dal prossimo paziente.
        # Questa separazione avviene perché non ogni fine processo porta a un'immediata prenotazione della risorsa;
        # il dottore potrebbe semplicemente tornare disponibile senza un'assegnazione immediata.
        elif type_of_update == "EndProcess":
            self.capacity_available= self.capacity_available  + entity_target.capacity_req_to_doc
            self.entity_processed.remove(entity_target)
            self.state = "idle"

        elif type_of_update == "EndProcess2":
            self.state = "reserved"
            self.entity_who_reserved.append(entity_target)

        elif type_of_update == "Failure":
            # Evento: Guasto del dottore
            self.state = "failed"

        elif type_of_update == "Recovery":
            # Evento: Recupero del dottore dal guasto
            self.state = "idle"

        elif type_of_update == "Arrival":
            # Evento: Un paziente appena arrivato prenota il dottore
            self.state = "reserved"
            self.entity_who_reserved.append(entity_target)

        else:
            print(f"update non riconosciuto: {type_of_update}")

    def reset(self):
        self.capacity_available = self.capacity_max
        self.state = "idle"
        self.entity_counter = 0

class Nurse(Resource):
    '''  Classe che rappresenta una risorsa di tipo "Infermiere".
    Estende la classe Resource aggiungendo proprietà specifiche come il livello di skill,
    lo store (stanza) associato e la raccolta di statistiche sulla differenza di skill.'''
    entity_counter = 0
    def __init__(self, sim=None, skill_level=1, store = None):
        super().__init__(sim=sim)
        self.skill_level = skill_level
        self.store = store                  # Riferimento alla stanza a cui l'infermiere è associato
        self.name = self.name_unique()
        self.entity_who_reserved = []       # Pazienti che hanno prenotato il posto nella stanza dove si trova l'infermiere
        self.entity_processed = []          # Pazienti attualmente in fase di processamento (ricovero)

        # Collezione di dati per registrare la differenza di skill tra paziente e infermiere
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
            # Evento: Inizio del processamento di un paziente (ricovero in stanza)
            self.state = "busy"
            self.entity_who_reserved.remove(entity_target)
            self.entity_processed.append(entity_target)

        elif type_of_update == "EndProcess":
            # Evento: Fine del processamento di un paziente (dimissione dalla stanza)
            self.delta_skill_level.add_to_data_collected(value_to_add = abs(min(0,(self.skill_level - entity_target.skill_level_req))))
            self.state = "idle"
            self.entity_processed.remove(entity_target)

        elif type_of_update == "Failure":
            # Evento: Guasto dell'infermiere
            self.state = "failed"

        elif type_of_update == "Recovery":
            # Evento: Recupero dell'infermiere dal guasto
            self.state = "idle"

        elif type_of_update == "EndProcessDoctor":
            # Evento: Un paziente ha terminato il trattamento con il dottore e ora prenota l'infermiere
            self.state = "reserved"
            self.entity_who_reserved.append(entity_target)

        else:
            print("update non riconosciuto")
        
    def reset(self):
        self.state = "idle"
        
