function [] = serialComs(model, t)
    
    try
        % Establish a connection to Arduino
        fclose('all');
        s = serial('COM6');
        set(s,'BaudRate',115200);
        fopen(s);
        fprintf("Connection established\n")
        pause(3)
        tic
        
        % Turn on servo's
        fprintf(s, 'on')
        pause(1);
        
        % Set up windowing of data to smooth spikes
        window = 10;
        y = zeros(1, window);

        % Run for t seconds. Handshake with Arduino, process string, window,
        % classify, and return classification.
        while toc < t
            fprintf(s, 'a');
            out = fscanf(s, '%40s\n');
            split = strsplit(out, ',');
            split = strrep(split, 'NaN', '0');
            force = str2double(split(1:end-1));

            for i=1:window-1
               y(i) = y(i+1);
            end
            y(window) = model.predictFcn(force);

            fprintf(s, 's%i\n', mode(y));
            pause(0.01);
            fprintf("Time: %0.1f, Class: %0.0f\n",toc,mode(y))
            %disp(mode(y));
        end
        
        % Turn off servo's
        fprintf(s, "off");
        
        % Clear connection
        fclose(s);
        delete(s)
        clear s

    catch ME
        disp(ME);
        fclose(s);
        delete(s)
        clear s
    end
end
