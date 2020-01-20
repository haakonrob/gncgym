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

    def draw(self, val=None):
        raise NotImplementedError("The draw method has not been implemented for this indicator.")

    def draw_arrow(self, x, y, angle, length, color=(0.9, 0.9, 0.9)):
        L = 50
        T = np.clip(7 * length, 0, 7)
        hx, hy = x + length * L * np.cos(angle), y + length * L * np.sin(angle)

        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(2)
        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(*color)
        gl.glVertex2f(x, y)
        gl.glVertex2f(hx, hy)
        gl.glEnd()

        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex2f(hx + T * np.cos(angle), hy + T * np.sin(angle))
        gl.glVertex2f(hx + T * np.cos(angle + 2 * np.pi / 3), hy + T * np.sin(angle + 2 * np.pi / 3))
        gl.glVertex2f(hx + T * np.cos(angle + 4 * np.pi / 3), hy + T * np.sin(angle + 4 * np.pi / 3))
        gl.glEnd()

    def draw_boat(self, x, y, width, height):
        # Draw basic boat shape
        width = 1.3 * 25
        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(0.9, 0.9, 0.9)
        gl.glVertex2f(x, y)
        gl.glVertex2f(x + width, y)
        gl.glVertex2f(x + width, y)
        gl.glVertex2f(x + width, y + 2 * height)
        gl.glVertex2f(x + width, y + 2 * height)
        gl.glVertex2f(x + width / 2, y + 2.5 * height)
        gl.glVertex2f(x + width / 2, y + 2.5 * height)
        gl.glVertex2f(x, y + 2 * height)
        gl.glVertex2f(x, y + 2 * height)
        gl.glVertex2f(x, y)
        gl.glEnd()


class Dashboard(Indicator):
    def __init__(self, height, width):
        self.H = height
        self.W = width

    def draw(self):
        gl.glBegin(gl.GL_QUADS)
        gl.glColor4f(0, 0, 0, 1)
        gl.glVertex3f(self.W, 0, 0)
        gl.glVertex3f(self.W, 5 * self.H, 0)
        gl.glVertex3f(0, 5 * self.H, 0)
        gl.glVertex3f(0, 0, 0)
        gl.glEnd()


class VerticalIndicator(Indicator):
    def __init__(self, position, dim, val_range, goal_val=None, color=(0, 0.8, 0), color_range=None, val_fn=lambda: 0):
        self.position = np.array(position)
        self.width, self.height = dim
        if color_range is not None:
            self.color_min, self.color_max = np.array(color_range[0]), np.array(color_range[1])
        else:
            self.color_min = self.color_max = np.array(color)
        self.color_interpol = self.color_max - self.color_min

        self._min, self._max = val_range
        self._range = self._max - self._min
        self._value_fn = val_fn
        self._marker = (np.clip(goal_val, self._min, self._max) - self._min)/self._range

    def draw(self, val=None):
        if val is None:
            val = self._value_fn()
        val = (np.clip(val, self._min, self._max) - self._min)/self._range  # Percentage
        color = tuple(self.color_min + self.color_interpol * val)

        # Draw rectangle starting at pos, with height and color proportional to val
        ox, oy = self.position

        gl.glBegin(gl.GL_QUADS)
        gl.glColor3f(*color)
        gl.glVertex3f(ox, oy, 0)
        gl.glVertex3f(ox + self.width, oy, 0)
        gl.glVertex3f(ox + self.width, oy + val * self.height, 0)
        gl.glVertex3f(ox, oy + val * self.height, 0)
        gl.glEnd()

        # Draw marker for desired value
        if self._marker is not None:
            gl.glBegin(gl.GL_LINES)
            gl.glColor3f(0.2, 0.2, 0.2)
            gl.glVertex3f(ox + 1.05 * self.width, oy + self._marker * self.height, 0)
            gl.glVertex3f(ox - 0.05 * self.width, oy + self._marker * self.height, 0)
            gl.glEnd()


class TextLabel(Indicator):
    def __init__(self, position, fontsize, color, val_fn=lambda: 0):
        self.x, self.y = position
        self.val_fn = val_fn
        self.score_label = pyglet.text.Label('0000', font_size=fontsize,
                                             x=self.x, y=self.y, anchor_x='left', anchor_y='center',
                                             color=color)

    def draw(self, val=None):
        if val is None:
            val = self.val_fn()
        self.score_label.text = "{:2.2f}".format(val)
        self.score_label.draw()


class ObstacleVectorsIndicator(Indicator):
    def __init__(self, position, dim, veclen):
        self.x, self.y = position
        self.w, self.h = dim
        self.veclen = veclen

    def draw(self, val=None):
        self.draw_boat(self.x, self.y, self.w, self.h)
        val = [] if val is None else val
        for closeness, angle in val:
            self.draw_arrow(self.x, self.y, angle, self.veclen * closeness,
                            color=(np.clip(1.2*closeness, 0, 1), 0.5, 0.1))
