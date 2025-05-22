import random
# CHECKED

class Distribution:
    def __init__(self, name: str, parameters: dict = None):
        self.name = name
        self.parameters = parameters or {}

    def sample(self):
        raise NotImplementedError("Il metodo sample() deve essere implementato nella sottoclasse")


class NormalDistributionTrunc(Distribution):
    def __init__(self, mu: float, sig: float):
        if sig <= 0:
            raise ValueError("La deviazione standard deve essere positiva.")
        super().__init__(name="Normal", parameters={"mu": mu, "sig": sig})
        self.mu = mu
        self.sig = sig

    def sample(self):
        return max(0, random.gauss(self.mu, self.sig))


class ExponentialDistribution(Distribution):
    def __init__(self, lambd: float):
        if lambd <= 0:
            raise ValueError("Il parametro lambda deve essere positivo.")
        super().__init__(name="Exponential", parameters={"lambd": lambd})
        self.lambd = lambd

    def sample(self):
        return random.expovariate(self.lambd)
