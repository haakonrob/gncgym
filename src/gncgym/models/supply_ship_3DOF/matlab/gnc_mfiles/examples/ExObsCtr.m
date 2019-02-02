% ExObsCtr   Observability and Controllability of Ships (see supply.m)
% Author:    Thor I. Fossen
% Date:      11 July 2002
% Revisions: 
% ________________________________________________________________
%
% MSS GNC is a Matlab toolbox for guidance, navigation and control.
% The toolbox is part of the Marine Systems Simulator (MSS).
%
% Copyright (C) 2008 Thor I. Fossen and Tristan Perez
% 
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% This program is distributed in the hope that it will be useful, but
% WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <http://www.gnu.org/licenses/>.
% 
% E-mail: contact@marinecontrol.org
% URL:    <http://www.marinecontrol.org>

format compact
disp('Controllabilty and observability of offShore supply vessel length 76 m')

% Normalization variables

L   =  76.2;           % length of ship (m)
g   =  9.8;            % acceleration of gravity (m/s^2)

T    = diag([1 1 L]);
Tinv = diag([1 1 1/L]);

% Model matricses
Mbis = [1.1274         0          0
             0    1.8902    -0.0744
             0   -0.0744     0.1278];

Dbis = [0.0358        0        0
             0        0.1183  -0.0124
             0       -0.0041   0.0308];

   
M = T*Mbis*Tinv
D = sqrt(g/L)*T*Dbis*Tinv          

% state space model
A = [ zeros(3,3) eye(3)
      zeros(3,3) -inv(M)*D ]

B = [zeros(3,3); inv(M) ]

C = [ eye(3) zeros(3,3) ]

n=rank(obsv(A,C))
n=rank(ctrb(A,B))
         
