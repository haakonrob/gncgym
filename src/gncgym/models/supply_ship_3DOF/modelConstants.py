import numpy as np


M = np.array([
        [7.22e6, 0, 0],
        [0, 1.21e7, -3.63e7],
        [0, -3.63e7, 4.75e9]
    ])

D = np.array([
    [95070, 0, 0],
    [0, 4.34e6, -2.27e6],
    [0, -1.88e7, 7.57e8]
])

B = np.array([
    [1, 0],
    [0, -1.13e6],
    [0, 9.63e7]
])

eps = -(M[2, 2]*B[1, 1] - M[1, 2]*B[2, 1]) / (M[1, 1]*B[2, 1] - M[1, 2]*B[1, 1])

H = np.eye(3)
H[1, 2] = -eps

M_p = np.transpose(H).dot(M).dot(H)
D_p = np.transpose(H).dot(D).dot(H)
B_p = np.transpose(H).dot(B)

K1 = B[0, 0]/M[0, 0]
K2 = (M[1, 1]*B[2, 1]-M[1, 2]*B[1, 1])/(M[1, 1]*M[2, 2]-M[1, 2]*M[1, 2])

M_6DOF = np.zeros([6, 6])
M_6DOF[0:2, 0:2] = M_p[0:2, 0:2]
M_6DOF[1, 5] = M_p[1, 2]
M_6DOF[5, 1] = M_p[1, 2]
M_6DOF[5, 5] = M_p[2, 2]