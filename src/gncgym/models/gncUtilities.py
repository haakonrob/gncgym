import numpy as np
from numpy import pi
from math import sin, cos


"""
Utilities adapted from MATLAB functions in the MSS GNC toolbox, originally written by Thor Inge Fossen.
"""


def m2c(M, nu):
    nu1 = nu[:3]
    nu2 = nu[3:]

    # Extract symmetric component
    Msym = 0.5 * (M + np.transpose(M))
    M = Msym

    M11 = M[:3, :3]
    M12 = M[:3, 3:]
    M21 = np.transpose(M12)
    M22 = M[3:, 3:]

    dt_dnu1 = M11.dot(nu1) + M12.dot(nu2)
    dt_dnu2 = M21.dot(nu1) + M22.dot(nu2)

    return np.vstack([
        np.hstack([np.zeros([3, 3]),    -smtrx(dt_dnu1)]),
        np.hstack([-smtrx(dt_dnu1),   -smtrx(dt_dnu2)])
    ])


def smtrx(r):
    return np.vstack([
        np.hstack([ 0,     -r[2],   r[1]]),
        np.hstack([ r[2],   0,     -r[0]]),
        np.hstack([-r[1],   r[0],   0])
    ])


def Rzyx(phi, theta, psi):
    cphi = cos(phi)
    sphi = sin(phi)
    cth = cos(theta)
    sth = sin(theta)
    cpsi = cos(psi)
    spsi = sin(psi)

    return np.vstack([
        np.hstack([cpsi*cth, -spsi*cphi+cpsi*sth*sphi,   spsi*sphi+cpsi*cphi*sth]),
        np.hstack([spsi*cth,  cpsi*cphi+sphi*sth*spsi,  -cpsi*sphi+sth*spsi*cphi]),
        np.hstack([-sth,      cth*sphi,                  cth*cphi])
    ])


def angdiff(a1, a2):
    return ((pi + a1 - a2) % (2*pi)) - pi
