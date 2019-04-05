M = csvread("C:\Users\Rico\OneDrive\Documents\School\MecE 653\Progress Report\data.csv");
figure(3)
plot(M(1:2400, :))
labels = {'FSR 1', 'FSR 2', 'FSR 3', 'FSR 4', 'FSR 5', 'FSR 6', 'FSR 7', 'FSR 8'};
legend(labels)
title("Raw FSR Values for Various Hand Gestres")