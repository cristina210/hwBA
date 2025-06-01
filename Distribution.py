import random

class Distribution:
    '''Classe astratta per la definizione di distribuzioni di probabilità.
    Fornisce un'interfaccia comune per le distribuzioni, inclusi un nome
    e un dizionario di parametri.'''
    def __init__(self, name: str, parameters: dict = None):
        self.name = name
        self.parameters = parameters or {}

    def sample(self):
        '''Metodo astratto per generare un campione casuale dalla distribuzione.
        Questo metodo deve essere implementato da ogni sottoclasse.'''
        raise NotImplementedError("Il metodo sample() deve essere implementato nella sottoclasse")


class NormalDistribution(Distribution):
    '''Implementazione della distribuzione normale'''
    def __init__(self, mu: float, sig: float):
        if sig <= 0:
            raise ValueError("La deviazione standard deve essere positiva.")
        super().__init__(name="Normal", parameters={"mu": mu, "sig": sig})
        self.mu = mu
        self.sig = sig

    def sample(self):
        '''Genera un singolo campione casuale dalla distribuzione normale.
        Il valore generato è troncato a zero (non può essere negativo).'''
        return max(0, random.gauss(self.mu, self.sig))  # 


class ExponentialDistribution(Distribution):
    '''Implementazione della distribuzione esponenziale.'''
    def __init__(self, lambd: float):
        if lambd <= 0:
            raise ValueError("Il parametro lambda deve essere positivo.")
        super().__init__(name="Exponential", parameters={"lambd": lambd})
        self.lambd = lambd

    def sample(self):
        '''Genera un singolo campione casuale dalla distribuzione esponenziale.'''
        return random.expovariate(self.lambd)
