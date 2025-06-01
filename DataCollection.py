import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

class DataCollection:
    '''
    Classe astratta per la raccolta di dati statistici all'interno di una simulazione.
    Fornisce un'interfaccia comune per l'inizializzazione, l'aggiunta di dati,
    il reset e la stampa delle collezioni di dati.
    '''
    def __init__(
        self,
        name: str = None,
        stats_only=False,  
        time=False        
    ):
        if stats_only and time:
            print("Statistica non supportata: stats_only e time both activated")
            return -1
        self.stats_only = stats_only
        self.name = name
        if stats_only is True:
            self.value = 0
        else:
            self.value = []

    def add_to_data_collected(self, *argv): 
        '''
        Metodo astratto per aggiungere dati alla collezione.
        Deve essere implementato dalle sottoclassi.
        '''
        pass

    def reset(self):
        '''
        Metodo astratto per resettare la collezione di dati.
        Deve essere implementato dalle sottoclassi.
        '''
        pass

    def print_object_data_collection(self):
        '''
        Metodo astratto per stampare i dati della collezione.
        Deve essere implementato dalle sottoclassi.
        '''
        pass

class DataTime(DataCollection):
    '''
    Classe per la raccolta di dati che variano nel tempo.
    Memorizza coppie (tempo, valore) e fornisce metodi per il calcolo
    della media integrale e la visualizzazione tramite grafici a gradini.
    '''
    def __init__(self, name: str = None):
        super().__init__( name=name, time=True, stats_only=False)
        self.reset()
    
    def add_to_data_collected(self, time_to_insert, value_to_add):
        self.value.append((time_to_insert, value_to_add))
        return 0
    
    def reset(self):
        self.value = [(0,0)]

    def print_object_data_collection(self):
        print(f"[{self.name}] variabile di stato nel tempo:")
        for t, v in self.value:
            print(f"  Tempo: {t} | Valore: {v}")
    

    def calculate_integral_mean(self):
        '''
        Calcola la media integrale (media temporale) della variabile di stato.
        Utilizzabile per variabili che cambiano a gradini.
        '''
        area = 0
        for i in range(len(self.value) - 1):
            t1, v1 = self.value[i]
            t2, v2 = self.value[i + 1]
            base = t2 - t1
            area += base * v1
        total_time = self.value[-1][0] - self.value[0][0]
        if total_time == 0:
            return 0  
        return area / total_time

    def plot_in_time(self, line=None, title = ""):
        if not self.value or len(self.value) < 2:
            print("Non ci sono dati sufficienti per fare il plot")
            return

        times = []
        values = []

        for pair in self.value:
            t, v = pair 
            times.append(t)
            values.append(v)
        plt.figure(figsize=(8, 4))
        plt.step(times, values, where='post', label=self.name or "Step Function")
        if line is not None:
            plt.axhline(y=line, color='red', linestyle='--', linewidth=2, label='Capacità massima')
        plt.xlabel("Tempo")
        plt.ylabel("Valore")
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


class DataWithoutTime(DataCollection):
    '''
    Classe per la raccolta di dati che non sono associati a un timestamp specifico.
    Memorizza una sequenza di valori.
    '''
    def __init__(self,name: str = None, stats_only=False):
        super().__init__( name=name, stats_only=stats_only, time=False)
        self.reset()
    def add_to_data_collected(self, value_to_add):
        self.value.append(value_to_add)
        return 0

    def reset(self):
        self.value = [0]

    def print_object_data_collection(self):
        print(f"[{self.name}]:")
        print("  Valori:", self.value)

    def plot_no_time(self, title = ""):
        if not self.value or self.value == [0]:
            print("Non ci sono dati di cui fare il plot")
            return

        x = list(range(len(self.value)))
        y = self.value

        plt.figure(figsize=(6, 3))
        plt.vlines(x, ymin=0, ymax=y, color='blue', linewidth=1.5, label=self.name or "Valori")
        plt.xlabel("Unità (indice)")
        plt.ylabel("Valore")
        plt.title(title)
        plt.grid(axis='y', linestyle='--', linewidth=0.5)
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

        plt.tight_layout()
        plt.show()

class DataStat(DataCollection):
    '''
    Classe per la raccolta di una singola statistica aggregata come una somma
    Memorizza un singolo valore numerico.
    '''
    def __init__(self, name: str = None, stats_only=True):
        super().__init__( name=name, stats_only=stats_only, time=False)

    def update_stat_sum(self, value_to_add):
        ''' Aggiorna il valore aggregato della statistica aggiungendo il valore fornito.
        Questo metodo è specifico per le statistiche che rappresentano una somma o un conteggio.'''
        self.value = self.value + value_to_add
        return 0
    
    def reset(self):
        self.value = 0
    
    def print_object_data_collection(self):
        print(f"[{self.name}]: {self.value}")


