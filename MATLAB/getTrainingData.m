function [data] = getTrainingData(n, classnum, trainnum)
    try
        fclose('all');
        % s = serial ('/dev/cu.usbmodem14201');
        s = serial ('COM6');
        set(s,'BaudRate',115200);
        fopen(s);
        pause(3);
        
        data = zeros(n*classnum*trainnum, 10);
        for k=1:trainnum
            input("training iteration: " + num2str(k))
            for i=1:classnum
                input("class number: " + num2str(i))
                fprintf(s, num2str(i-1));
                pause(1);
                for j=1:n
                    fprintf(s, "a");
                    out = fscanf(s, '%40s\n');
                    split = strsplit(out, ',');
                    split = strrep(split, 'NaN', '0');
                    data(n *(i-1) + n*classnum*(k-1) + j, :) = str2double(split);
                    disp(str2double(split))
                end
            end
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
end