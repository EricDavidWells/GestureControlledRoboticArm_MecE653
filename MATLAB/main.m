clear all; close all; clc;
COMPORT = "/dev/cu.usbmodem14201"; %"COM6";

data = getTrainingData(250, 4, 1, COMPORT); 
fprintf("\nTraining Complete\n");
fprintf("Generating classifier...\n");
[model, accuracy] = generateSVM(data);
fprintf("\Classifier Accuracy: %d\n", accuracy);
visualizeData(data);
t = input("Simulation time: ");
serialComs(model, t, COMPORT);