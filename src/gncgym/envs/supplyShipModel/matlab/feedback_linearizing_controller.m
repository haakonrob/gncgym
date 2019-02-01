function [ controller_out ] = feedback_linearizing_controller( controller_in )
%Feedback linearizing controller for surge and yaw

P_u = 0.1;
P_r = 0.04;
D_r = 0.9;

u = controller_in(1);
v = controller_in(2);
r = controller_in(3);
u_r = controller_in(4);
u_r_dot = controller_in(5);
psi_r = controller_in(6);
psi_r_dot = controller_in(7);
psi_r_dot_dot = controller_in(8);
psi = controller_in(11);

%CORRECT MODEL
M = [(7.22)*10^6  0               0;
    0           (1.21)*10^7       (-3.63)*10^7;
    0           (-3.63)*10^7      (4.75)*10^9];

D = [95070      0               0;
    0           (4.34)*10^6       (-2.27)*10^6;
    0           (-1.88)*10^7      (7.57)*10^8];

B = [1          0;
    0           (-1.13)*10^6;
    0           (9.63)*10^7];

eps = -(M(3,3)*B(2,2)-M(2,3)*B(3,2))/(M(2,2)*B(3,2)-M(2,3)*B(2,2));

H = eye(3);
H(2,3) = -eps;

M_p = H'*M*H;
D_p = H'*D*H;
B_p = H'*B;

F_u = (r/M_p(1,1))*(M_p(2,3)*r+M_p(2,2)*v);
F_r = (1/(M_p(2,2)*M_p(3,3)-M_p(2,3)*M_p(2,3)))*(v*(D_p(2,2)*M_p(2,3)-D_p(3,2)*M_p(2,2)+u*(M_p(1,1)*M_p(2,2)-M_p(2,2)*M_p(2,2)))+r*(D_p(2,3)*M_p(2,3)-D_p(3,3)*M_p(2,2)+u*(M_p(1,1)*M_p(2,3)-M_p(2,2)*M_p(2,3))));

tau_u = -F_u + u_r_dot + (D_p(1,1)/M_p(1,1))*u_r + P_u*(u_r-u);
tau_r = -F_r + psi_r_dot_dot + P_r*(psi_r-psi) + D_r*(psi_r_dot-r);

controller_out = [tau_u;tau_r];
end