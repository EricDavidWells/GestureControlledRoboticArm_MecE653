function [] = serialComs(model, t, COMPORT)

    try
        % Establish a connection to Arduino
        fclose('all');
        s = serial(COMPORT);
        set(s,'BaudRate',115200);
        fopen(s);
        fprintf("Connection established\n")
        pause(3)
        yPrev = 0;
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

            if (yPrev ~= mode(y))
              stateVisualizer(mode(y));
            end
            
            yPrev = mode(y);
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



function [] = stateVisualizer(state)
    % Figure setup
    figure(1)
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0, 1, 1, 0.7]);
    pos = [0 0 2 2];

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Shoulder Counter Clockwise
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(2,2,1);

    if state == 1
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.4660, 0.6740, 0.1880])
    else
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.25, 0.25, 0.25])
    end

    title('Shoulder State: Counter Clockwise','FontSize',24)
    axis equal
    set(gca,'xtick',[],'ytick',[],'color','none','XColor','none','Ycolor','none')

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Shoulder Clockwise
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(2,2,3);

    if state == 2
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.4660, 0.6740, 0.1880])
    else
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.25, 0.25, 0.25])
    end

    title('Shoulder State: Clockwise','FontSize',24)
    axis equal
    set(gca,'xtick',[],'ytick',[],'color','none','XColor','none','Ycolor','none')

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Gripper On
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(2,2,2);

    if state == 3
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.4660, 0.6740, 0.1880])
    else
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.25, 0.25, 0.25])

    end

    title('Gripper State: Closed','FontSize',24)
    axis equal
    set(gca,'xtick',[],'ytick',[],'color','none','XColor','none','Ycolor','none')

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Gripper Off
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(2,2,4);

    if state == 0
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.4660, 0.6740, 0.1880])
    else
        rectangle('Position',pos,'Curvature',[1 1],'FaceColor',[0.25, 0.25, 0.25])
    end

    title('Gripper State: Open','FontSize',24)
    axis equal
    set(gca,'xtick',[],'ytick',[],'color','none','XColor','none','Ycolor','none')

end
