clear all; close all; clc;
data = getTrainingData(250, 4, 3); fprintf("\nTraining Complete\n");
fprintf("\Generating classifier...\n"); model = generateSVM(data);
visualizeData(data);
t = input("Simulation time: ");
serialComs(model, t);