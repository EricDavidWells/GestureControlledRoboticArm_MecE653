clear all; close all; clc;
COMPORT = "/dev/cu.usbmodem14201"; %"COM6";

data = getTrainingData(200, 4, 2, COMPORT); 
fprintf("\nTraining Complete\n");
fprintf("Generating classifier...\n");
[model, accuracy] = generateSVM(data);
fprintf("Classifier Accuracy: %d\n", accuracy);
visualizeData(data);
t = input("Simulation time: ");
serialComs(model, t, COMPORT);