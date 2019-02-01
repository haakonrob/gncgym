function [ ship_out ] = supply_ship_model( ship_in )
%The dynamic model of the supply ship
%ship_in = [eta;nu;f;V] where f is the controlled
%inputs and V is the two-dimentional ocean current
%ship_out = [eta_dot;nu_dot]

eta = ship_in(1:3);
nu = ship_in(4:6);
f = ship_in(7:8);

x = eta(1);
y = eta(2);
psi = eta(3);

u = nu(1);
v = nu(2);
r = nu(3);


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

M_6DOF = zeros(6,6);
M_6DOF(1:2,1:2) = M_p(1:2,1:2);
M_6DOF(2,6) = M_p(2,3);
M_6DOF(6,2) = M_p(2,3);
M_6DOF(6,6) = M_p(3,3);
nu_6DOF = [u;v;0;0;0;r];
C_6DOF = m2c(M_6DOF,nu_6DOF);

C_p = C_6DOF;
C_p(:,3:5) = [];
C_p(3:5,:) = [];

eta_dot = Rzyx(0,0,psi)*nu;
nu_dot = inv(M_p)*(B_p*f-C_p*nu-D_p*nu);
ship_out = [eta_dot;nu_dot];

end

