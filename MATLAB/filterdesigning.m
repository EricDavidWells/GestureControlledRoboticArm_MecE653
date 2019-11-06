close all
% read data
filename = 'C:\Users\Rico5678\OneDrive\Documents\School\MecE 653\GestureControlledRoboticArm_MecE653\data\data.csv';
delimiter = ',';
startRow = 2;
formatSpec = '%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%[^\n\r]';
fileID = fopen(filename,'r');
dataArray = textscan(fileID, formatSpec, 'Delimiter', delimiter, 'TextType', 'string', 'EmptyValue', NaN, 'HeaderLines' ,startRow-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
fclose(fileID);
data = [dataArray{1:end-1}];
clearvars filename delimiter startRow formatSpec fileID dataArray ans;

%% Raw values and FFT Plotting

% get data for filtering
fs = 200;
N = length(data);
t = (0:N-1)/fs;
T = N/fs;
data(:,2) = [];
FSRnum = 10;
FSR1 = data(:,1)';
noise = 15*rand(size(t)).*sin(2*pi*50*t);

%% Raw Plots
% plot all FSRs
fnum = 1;
figure(fnum)
set(0,'DefaultLineLineWidth',1.5)
plot(t, data(:,1:FSRnum))
xlabel('Time (s)')
ylabel('Force (grams)')
fnum = fnum+1;

% plot single FSR with and without noise
figure(fnum)
hold on
grid on
plot(t, FSR1 + noise)
plot(t, FSR1)
xlabel('Time (s)')
ylabel('Force (grams)')
legend("50 Hz Artificial Noise", "Original Signal")
fnum = fnum+1;

% plot FFT of all FSRS without noise
Y = fft(data);
Ymag = abs(Y);
Yscaled = Ymag(1:N/2+1,1:FSRnum)*2/N;
f = (0:1/T:fs/2);

figure(fnum)
grid on
plot(f, Yscaled)
xlabel('Frequency (Hz)')
ylabel('Magnitude (grams)')
xlim([0,100])
ylim([0,50])
fnum = fnum+1;

% plot FFT of all FSRS with noise
Y = fft(data + noise');
Ymag = abs(Y);
Yscaled = Ymag(1:N/2+1,1:FSRnum)*2/N;
f = (0:1/T:fs/2);

figure(fnum)
grid on
plot(f, Yscaled)
xlabel('Frequency (Hz)')
ylabel('Magnitude (grams)')
xlim([0,100])
ylim([0,50])
fnum = fnum+1;


%% Filter Design
fp = 5;
wp = fp/(fs/2);
fst = 15;
wst = fst/(fs/2);
%% Moving Average Filter

MAfilt_fc = (fp+fst);
psi = 2*pi*MAfilt_fc/fs;
MAn = ceil(pi/psi); 
MAn = 30;
b = (1/MAn)*ones(1,MAn);
a = 1;
MAfiltFSR1 = filter(b,a,FSR1+noise);
tic

MAfiltdelay = 0;
tic
for i=1:100000
temp = filter(b,a,FSR1(1:MAn));
end
MAfiltdelay = toc/100000;
MAfiltphasedelay = phasedelay(b,a);

figure(fnum)
fnum = fnum+1;
subplot(2,1,1)
hold on
freqz(b,a)
[h, w] = freqz(b,a);
title("Moving Average Filter")
plot([wp, wst], interp1(w/pi, 20*log10(abs(h)), [wp,wst]), 'rx')
subplot(2,1,2)
hold off
phasedelay(b,a)
hold on
ytickformat('%.2f')
[phi,w] = phasedelay(b,a);
plot([wp, wst], interp1(w(2:end)/pi, phi(2:end), [wp,wst], 'linear','extrap'), 'rx')


%% Hanning Window
Hannwindowsize = ceil(3.32*fs/(fst-fp));
Hannwindow = hann((Hannwindowsize-1)/2, 'symmetric');
b = fir1(floor(Hannwindowsize/2-1), (fst-fp)/2/(fs/2), Hannwindow);
a = 1;
HannfiltFSR1 = filter(b,a,FSR1+noise);
tic

Hannfiltdelay = 0;
tic
for i=1:100000
temp = filter(b,a,FSR1(1:Hannwindowsize));
end
Hannfiltdelay = toc/100000;
Hannfiltphasedelay = phasedelay(b,a);

figure(fnum)
fnum = fnum+1;
subplot(2,1,1)
hold on
freqz(b,a)
[h, w] = freqz(b,a);
title("Hanning Window")
plot([wp,wst], interp1(w/pi, 20*log10(abs(h)), [wp,wst]), 'rx')
subplot(2,1,2)
ytickformat('%.2f')
hold off
phasedelay(b,a)
hold on
ytickformat('%.2f')
[phi,w] = phasedelay(b,a);
plot([wp,wst], interp1(w(2:end)/pi, phi(2:end), [wp,wst], 'linear','extrap'), 'rx')

%% Butterworth Filter

butterwp = 2*(fst-fp)/2/fs;
butterws = 2*fst/fs;
butterattenp = 1;
butterdp = 1 - 10^(-butterattenp/20);
butterattens = 44;
butterds = 10^(-butterattens/20);
butterN = ceil(log10(1/butterds^2-1)/(2*log10(butterws/butterwp)));

[b,a] = butter(butterN, butterwp);

butterfiltFSR1 = filter(b,a,FSR1+noise);

butterfiltdelay = 0;
tic
for i=1:100000
temp = filter(b,a,FSR1(1:butterN));
end
butterfiltdelay = toc/100000;
butterfiltphasedelay = phasedelay(b,a);

figure(fnum)
fnum = fnum+1;
subplot(2,1,1)
hold on
freqz(b,a)
[h, w] = freqz(b,a);
title("Butterworth")
plot([wp,wst], interp1(w/pi, 20*log10(abs(h)), [wp,wst]), 'rx')
subplot(2,1,2)
ytickformat('%.2f')
hold off
phasedelay(b,a)
hold on
[phi,w] = phasedelay(b,a);
plot([wp,wst], interp1(w(2:end)/pi, phi(2:end), [wp,wst], 'linear','extrap'), 'rx')

%% Chebyshev type 2 filter
cheby2wp = fp/(fs/2);   
cheby2ws = fst/(fs/2);
cheby2attenp = 1;
cheby2dp = 1 - 10^(-cheby2attenp/20);
cheby2attens = 44;
cheby2ds = 10^(-cheby2attens/20);
epsilon = sqrt(1/(1-cheby2dp)^2-1);
d = sqrt(1/cheby2ds^2-1);
cheby2N = ceil(acosh(d/epsilon)/acosh(cheby2ws/cheby2wp));

[b,a] = cheby2(cheby2N,cheby2attens,cheby2ws);

cheby2filtFSR1 = filter(b,a,FSR1+noise);

cheby2filtFSRS = zeros(size(data(:,1:10)));
for i=1:10
cheby2filtFSRS(:,i) = filter(b,a,data(:,i)+noise');
end
cheby2filtdelay = 0;
tic
for i=1:100000
temp = filter(b,a,FSR1(1:cheby2N));
end
cheby2filtdelay = toc/100000;
cheby2phasedelay = phasedelay(b,a);

figure(fnum)
fnum = fnum+1;
subplot(2,1,1)
hold on
freqz(b,a)
[h, w] = freqz(b,a);
title("Chebyshev Type II")
plot([wp,wst], interp1(w/pi, 20*log10(abs(h)), [wp,wst]), 'rx')
subplot(2,1,2)
ytickformat('%.2f')
hold off
phasedelay(b,a)
hold on
[phi,w] = phasedelay(b,a);
plot([wp,wst], interp1(w(1:end)/pi, phi(1:end), [wp,wst], 'linear','extrap'), 'rx')

%% filter comparison
figure(fnum)
fnum = fnum+1;
hold on;
plot(t, FSR1)
plot(t, FSR1+noise)
plot(t,MAfiltFSR1)
plot(t,HannfiltFSR1)
plot(t,butterfiltFSR1)
plot(t,cheby2filtFSR1)
legend("Original Data", "Noisy Data", "Moving Average", "Hanning Window", "Butterworth", "Chebyshev II")
xlabel('Time (s)')
ylabel('Force (grams)')


figure(fnum)
set(gca,'DefaultLineLineWidth',2)
fnum = fnum+1;
hold on;
plot(t, FSR1+noise, 'c-', 'LineWidth', 0.5)
plot(t,MAfiltFSR1)
plot(t,HannfiltFSR1)
plot(t,butterfiltFSR1)
plot(t,cheby2filtFSR1)
legend("Noisy Data", "Moving Average", "Hanning Window", "Butterworth", "Chebyshev II")
xlabel('Time (s)')
ylabel('Force (grams)')
xlim([9,11]);
ylim([70,120]);

figure(fnum)
fnum = fnum+1;
Y = fft(cheby2filtFSRS);
Ymag = abs(Y);
Yscaled = Ymag(1:N/2+1,1:FSRnum)*2/N;
f = (0:1/T:fs/2);

grid on
plot(f, Yscaled)
xlabel('Frequency (Hz)')
ylabel('Magnitude (grams)')
xlim([0,100])
ylim([0,50])

