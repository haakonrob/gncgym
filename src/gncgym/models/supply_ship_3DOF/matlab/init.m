clear all;
close all;
clc;

addpath('./gnc_mfiles')

%% Initial state of ship
x0 = -200;
y0 = 200;
psi0 = 0;
u0 = 0;
v0 = 0;
r0 = 0;

%% Guidance parameters
global u_des Delta;
u_des = 4; %Desired surge velocity
Delta = 75; %Lookahead distance

%% Model-based constants used in controller, do not change

M = [7.22*10^6  0               0;
    0           1.21*10^7       -3.63*10^7;
    0           -3.63*10^7      4.75*10^9];

D = [95070      0               0;
    0           4.34*10^6       -2.27*10^6;
    0           -1.88*10^7      7.57*10^8];

B = [1          0;
    0           -1.13*10^6;
    0           9.63*10^7];

eps = -(M(3,3)*B(2,2)-M(2,3)*B(3,2))/(M(2,2)*B(3,2)-M(2,3)*B(2,2));

H = eye(3);
H(2,3) = -eps;

M_p = H'*M*H;
D_p = H'*D*H;
B_p = H'*B;

K1 = B(1,1)/M(1,1);
K2 = (M(2,2)*B(3,2)-M(2,3)*B(2,2))/(M(2,2)*M(3,3)-M(2,3)*M(2,3));

%% Simulation constants
global delta_t;
delta_t  = 0.05; %Time step

%% Run simulation
sim('supply_ship_mdl');

%Plot figures
figures
