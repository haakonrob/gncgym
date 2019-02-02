function [ point_rotated ] = rotate_point_psi( psi )
%Function to illustrate direction of LOS
R = Rzyx(0,0,psi);
R = R(1:2,1:2);
p = [150;0];
point_rotated = R*p;

end

