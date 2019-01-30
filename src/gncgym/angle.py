from numpy import pi, unwrap


class Angle(float):
    def __new__(cls, val):
        return float.__new__(cls, ((val + pi) % (2*pi)) - pi )

    def __add__(self, other):
        return Angle(float.__add__(self, other))

    def __radd__(self, other):
        return Angle(float.__radd__(self, other))

    def __sub__(self, other):
        return Angle(float.__sub__(self, other))

    def __rsub__(self, other):
        return Angle(float.__rsub__(self, other))
    
    def __mul__(self, other):
        return Angle(float.__mul__(self, other))

    def __rmul__(self, other):
        return Angle(float.__rmul__(self, other))
    
    def __truediv__(self, other):
        return Angle(float.__truediv__(self, other))

    def __rtruediv__(self, other):
        return Angle(float.__rtruediv__(self, other))
    
    def __divmod__(self, other):
        return Angle(float.__divmod__(self, other))

    def __rdivmod__(self, other):
        return Angle(float.__rdivmod__(self, other))
    
    def __repr__(self):
        return "Angle({:.3f})".format(self)
