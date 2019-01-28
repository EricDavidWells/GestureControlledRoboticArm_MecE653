data = getTrainingData(100, 4, 1);
model = generateSVM(data);
visualizeData(data);
t = input("foo");
serialComs(model, t);