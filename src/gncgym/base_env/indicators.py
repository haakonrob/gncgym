import pyglet
import numpy as np
from pyglet import gl


def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]


class Indicator:
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def draw(self):
        raise NotImplementedError("The draw method has not been implemented for this indicator.")


class VerticalIndicator(Indicator):
    def __init__(self, position, dim, val_range, color, val=0):
        self.position = position
        self.length, self.width = dim
        self.color_range = color
        self.val_range = val_range
        self._value = val

    def draw(self):
        val = np.clip(self.val, *self.val_range) + self.val_range[0]

        gl.glBegin(gl.GL_QUADS)
        gl.glColor3f(*color)
        gl.glVertex3f((place + 0) * s, 2 * h + h * val, 0)
        gl.glVertex3f((place + 1) * s, 2 * h + h * val, 0)
        gl.glVertex3f((place + 1) * s, 2 * h, 0)
        gl.glVertex3f((place + 0) * s, 2 * h, 0)
        gl.glEnd()