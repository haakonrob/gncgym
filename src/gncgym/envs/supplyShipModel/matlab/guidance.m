function [ state_out ] = guidance( state_in )
%Desired u and ps
global Delta u_des

y = state_in(2);
%Standard LOS for straight line path following
psi_des = atan2(-y,Delta);

%Return correct state
state_out = [u_des;psi_des];

end

