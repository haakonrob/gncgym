function [ ship_corners ] = plot_ship( eta )
%Returns points to plot the ship

w = 25;
l = 45;

x = eta(1);
y = eta(2);
psi = eta(3);

p = [x;y];

R = Rzyx(0,0,psi);
R = R(1:2,1:2);

p1 = [1.4*l;0];
p2 = [l;w];
p3 = [-l;w];
p4 = [-l;-w];
p5 = [l;-w];

p1 = R*p1 + p;
p2 = R*p2 + p;
p3 = R*p3 + p;
p4 = R*p4 + p;
p5 = R*p5 + p;

ship_corners = [p1,p2,p3,p4,p5,p1];


end

