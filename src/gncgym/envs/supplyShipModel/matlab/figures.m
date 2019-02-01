sec_interval = 50;

plot([0 0],[x.signals.values(1) x.signals.values(end)+100],'LineWidth',2,'Color','red');
hold on;
plot(y.signals.values,x.signals.values,'LineWidth',2,'Color','blue');
for i=1:length(x.time)
    if mod(x.time(i),sec_interval) == 0
        ship_corners = plot_ship([x.signals.values(i);y.signals.values(i);psi.signals.values(i)]);
        plot(ship_corners(2,:),ship_corners(1,:),'k','LineWidth',2);
    end
end
title('xy-trajectory');
xlabel('East [m]');
ylabel('North [m]');
legend('Desired straight line path','Actual path');
axis equal;

figure
plot(u_ref.time, u_ref.signals.values,'r');
hold on;
plot(u.time, u.signals.values,'b');
title('Forward speed reference and actual');
axis([0 u_ref.time(end) -2 6]);
xlabel('Time [s]');
ylabel('Velocity [m/s]');
legend('Reference surge velocity','Actual surge velocity');

figure
plot(psi_ref.time, (180/pi)*psi_ref.signals.values,'r');
hold on;
plot(psi.time, (180/pi)*psi.signals.values,'b');
title('Heading reference and actual');
xlabel('Time [s]');
ylabel('Heading [deg]');
legend('Reference','Actual');

figure
plot(T.time, T.signals.values,'r');
title('Thruster force in Newton');

figure
plot(delta_r.time, (180/pi)*delta_r.signals.values,'r');
title('Rudder angle in degrees');