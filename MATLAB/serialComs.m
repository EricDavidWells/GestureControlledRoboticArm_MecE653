try

    fclose('all');
    % s = serial ('/dev/cu.usbmodem14201');
    s = serial ('COM6');
    set(s,'BaudRate',115200);
    fopen(s);
    fprintf(s,'*IDN?');
%     load svm_Rico.mat;
    pause(3);
    tic
    
    window = 10;
    y = zeros(1, window);
    while toc < 60

        fprintf(s, "a");
        out = fscanf(s, '%40s\n');
        split = strsplit(out, ',');
        split = strrep(split, 'NaN', '0');
        force = str2double(split(1:end-1));
        
        for i=1:window-1
           y(i) = y(i+1); 
        end
        y(window) = grandFinal.predictFcn(force);
%         y = mode(y);
        
        fprintf(s, "s%i\n", mode(y));
        pause(0.01);
        disp(mode(y));
    end

    fclose(s);
    delete(s)
    clear s
catch ME
    disp(ME);
    fclose(s);
    delete(s)
    clear s
end
