function [] = serialComs(model, t)
    try
        % Establish a connection to Arduino
        fclose('all');
        s = serial('COM6');
        set(s,'BaudRate',115200);
        fopen(s);
        pause(3);
        tic

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
            disp(mode(y));
        end

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
