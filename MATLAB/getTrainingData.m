function [data] = getTrainingData(n, classnum, trainnum, COMPORT)
    try
        fclose('all');
        s = serial (COMPORT);
        set(s,'BaudRate',115200);
        fopen(s);
        pause(3);
        count = 1;

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
                    if (count > 50)
                        fprintf(". ");
                        count = 1;
                    end
                    count = count + 1;
                end
                fprintf("\n")
                count = 1;
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
