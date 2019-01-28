function [g] = visualizeData(fileName)
    close all
    fileNamePath = strcat('../data/',fileName);
    data = csvread(fileNamePath);
    pcacoeff = pca(data, 'NumComponents', 3);
    
    y0 = data(:,end) == 0;
    y1 = data(:,end) == 1;
    y2 = data(:,end) == 2;
    y3 = data(:,end) == 3;
    
    x0 = data(find(y0),:);
    x1 = data(find(y1),:);
    x2 = data(find(y2),:);
    x3 = data(find(y3),:);
    
    pcax0 = x0 * pcacoeff;
    pcax1 = x1 * pcacoeff;
    pcax2 = x2 * pcacoeff;
    pcax3 = x3 * pcacoeff;
    
    figure(1)
    
    scatter3(pcax0(:,1), pcax0(:,2), pcax0(:,3), 'o')
    hold on
    scatter3(pcax1(:,1), pcax1(:,2), pcax1(:,3), 'o')
    scatter3(pcax2(:,1), pcax2(:,2), pcax2(:,3), 'o')
    scatter3(pcax3(:,1), pcax3(:,2), pcax3(:,3), 'o')
    grid on
    legend(["Rest", "Up", "Down", "Squeeze"])

    
    figure(2)
    labels = {'FSR 1', 'FSR 2', 'FSR 3', 'FSR 4', 'FSR 5', 'FSR 6', 'FSR 7', 'FSR 8', 'mean'};

    for ii = 1:length(data(:,10))
        if (data(ii,10) == 0)
            name{ii,1} = 'Rest';
        elseif (data(ii,10) == 1)
            name{ii,1} = 'Up';
        elseif (data(ii,10) == 2)
            name{ii,1} = 'Down';
        else
            name{ii,1} = 'Squeeze';
        end
    end

    parallelcoords(data(:,1:9),'Group',name,'Labels',labels)

end