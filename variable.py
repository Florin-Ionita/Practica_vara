# Custom Variable class with operator overloading for SAT literals
class Variable:
    def __init__(self, name, positive=True):
        self.name = name
        self.positive = positive
    
    def __neg__(self):
        return Variable(self.name, not self.positive)
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name and self.positive == other.positive
    
    def __hash__(self):
        return hash((self.name, self.positive))
    
    def __repr__(self):
        return ("-" if not self.positive else "") + self.name
