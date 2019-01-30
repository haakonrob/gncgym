import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from .gncUtilities import Rzyx

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'ro', animated=True)


def plot_ship(*args):
    if type(args[0]) is list:
        data = args[0]
        _plot_ship_only(data)
    else:
        ax = args[0]
        data = args[1]
        return _plot_ship_on_axes(ax, data)


def _plot_ship_on_axes(ax, data):

    T = [d['t'] for d in data]
    x = np.array([d['state'][0] for d in data])
    y = np.array([d['state'][1] for d in data])

    # T = [d['control_input'][0] for d in data]
    # delta_r = [180/pi*d['control_input'][1] for d in data]

    # Plot position
    ax.plot(-y[1:], x[1:], 'r')

    # Overlay boat outline at regular intervals
    n = 5
    m = 0
    interval = T[-1]/n

    for i, t in enumerate(T):
        if t > m*interval:
            cx, cy = get_ship_corners(data[i]['state'])
            ax.plot(-cy, cx, 'k')
            m += 1


def _plot_ship_only(data):

    T = [d['t'] for d in data]
    x = [d['state'][0] for d in data]
    y = [d['state'][1] for d in data]

    # T = [d['control_input'][0] for d in data]
    # delta_r = [180/pi*d['control_input'][1] for d in data]

    # Plot position
    plt.plot(-y[1:], x[1:], 'r')

    # Overlay boat outline at regular intervals
    n = 5
    m = 0
    interval = T[-1]/n

    for i, t in enumerate(T):
        if t > m*interval:
            cx, cy = get_ship_corners(data[i]['state'])
            plt.plot(-cy, cx, 'k')
            m += 1

    plt.axis('equal')
    plt.show()


def animate_data(data):
    ani = FuncAnimation(fig, update, frames=data,
                        init_func=init, blit=True, interval=1)
    plt.show()


def init():
    plt.axis('equal')
    return ln,


def update(frame):
    t = frame['time']
    state = frame['state']
    x, y, psi, u, v, r = state
    xdata.append(x)
    ydata.append(y)
    ln.set_data(xdata, ydata)
    return ln,


def get_ship_corners(eta):
    # Ship dimensions
    w = 25
    l = 45

    # Current position and heading of the ship
    x = eta[0]
    y = eta[1]
    psi = eta[2]

    # Pack the ship position into a column matrix
    p = np.array([[x], [y]])

    # Make a rotation matrix using the GNC utility Rzyx
    R = Rzyx(0, 0, psi)
    R = R[0:2, 0:2]

    # Create basic boat shape centered at origin
    p1 = np.array([[1.4 * l], [0]])
    p2 = np.array([[l], [w]])
    p3 = np.array([[-l], [w]])
    p4 = np.array([[-l], [-w]])
    p5 = np.array([[l], [ -w]])

    # Rotate and translate the boat shape to the state
    p1 = R.dot(p1) + p
    p2 = R.dot(p2) + p
    p3 = R.dot(p3) + p
    p4 = R.dot(p4) + p
    p5 = R.dot(p5) + p

    # Return 2 1D arrays containing the x and y coordinates of the vertices
    P = np.concatenate([p1, p2, p3, p4, p5, p1], axis=1)
    X, Y = P[0, :], P[1, :]
    return X, Y




