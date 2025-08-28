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
    
    def is_positive(self):
        """Return True if this is a positive literal"""
        return self.positive
    
    def is_negative(self):
        """Return True if this is a negative literal"""
        return not self.positive
