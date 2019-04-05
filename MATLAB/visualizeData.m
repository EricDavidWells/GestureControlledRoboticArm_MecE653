function [g] = visualizeData(data, numclass)
    close all
    
%     fileNamePath = strcat('../data/',"1450_fake8classes.csv");
%     data = csvread(fileNamePath);
    pcacoeff = pca(data(:,1:end-1), 'NumComponents', 3);
    
    Y = [];
    X = {};
    PCAX = {};
    for i=1:numclass
        Y(:,i) = data(:,end) == i-1;
        X{i} = data(find(Y(:,i)),1:end-1);
        PCAX{i} = X{i}*pcacoeff;
    end
    
    outputlabels = {'Rest', 'Extension', 'Flexion', 'Fist', 'Left', 'Right', 'Supination', 'Pronation'};
    figure(1)
    scatter3(PCAX{1}(:,1), PCAX{1}(:,2), PCAX{1}(:,3), 'o')
    hold on
    for i=2:numclass
        scatter3(PCAX{i}(:,1), PCAX{i}(:,2), PCAX{i}(:,3), 'o')  
    end
    grid on
    legend(outputlabels)
    xlabel("PCA 1")
    ylabel("PCA 2")
    zlabel("PCA 3")
    title("3 Dimensional PCA Analysis of FSR Data")
    
    labels = {'FSR 1', 'FSR 2', 'FSR 3', 'FSR 4', 'FSR 5', 'FSR 6', 'FSR 7', 'FSR 8'};
    figure(2)

    for ii = 1:length(data(:,9))
        name{ii,1} = outputlabels{data(ii,9)+1};
    end

    parallelcoords(data(:,1:8),'Group',name,'Labels',labels)
    title("Parallel Coordinate Plot of FSR Data")
    
end