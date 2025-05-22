
class DataCollection:
    def __init__(
        self,
        name: str = None,
        stats_only=False,  # Ho impostato un valore di default per chiarezza
        time=False         # Ho impostato un valore di default per chiarezza
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
            # lista di tuple nel caso di time == True, lista di valori altrimenti. prima posizione = tempo

    def add_to_data_collected(self, *argv): # è giusto?
        pass
    # da fare

    def reset(self):
        pass
    # da fare

class DataTime(DataCollection):
    #def __init__(self, sim: SimulationManager = None, name: str = None):
    def __init__(self, name: str = None):
        super().__init__( name=name, time=True, stats_only=False)

    def add_to_data_collected(self, time_to_insert, value_to_add):
        self.value.append((time_to_insert, value_to_add))
        return 0
    
    def reset(self):
        self.value = []

class DataWithoutTime(DataCollection):
    def __init__(self,name: str = None, stats_only=False):
        super().__init__( name=name, stats_only=stats_only, time=False)
    def add_to_data_collected(self, value_to_add):
        self.value.append(value_to_add)
        return 0

    def reset(self):
        self.value = []

class DataStat(DataCollection):
    def __init__(self, name: str = None, stats_only=True):
        super().__init__( name=name, stats_only=stats_only, time=False)
    def update_stat_sum(self, value_to_add):
        self.value = self.value + value_to_add
        return 0
    def reset(self):
        self.value = 0


