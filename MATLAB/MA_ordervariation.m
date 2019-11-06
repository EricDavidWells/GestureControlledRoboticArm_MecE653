%% Moving Average Filter
MAn = [10, 20, 30];
for i=1:3
    MAfilt_fc = (fp+fst);
    psi = 2*pi*MAfilt_fc/fs;
%     MAn = ceil(pi/psi); 
    b = (1/MAn(i))*ones(1,MAn(i));
    a = 1;
    MAfiltFSR1 = filter(b,a,FSR1+noise);
    tic

    figure(fnum)
    subplot(2,1,1)
    hold on
    freqz(b,a)
    [h, w] = freqz(b,a);
    title("Moving Average Filter")
    plot([wp, wst], interp1(w/pi, 20*log10(abs(h)), [wp,wst]), 'x')
    subplot(2,1,2)
    hold off
    phasedelay(b,a)
    hold on
    ytickformat('%.2f')
    [phi,w] = phasedelay(b,a);
    plot([wp, wst], interp1(w(2:end)/pi, phi(2:end), [wp,wst], 'linear','extrap'), 'x')
end
subplot(2,1,1)
legend("n=10", "n=20", "n=30")
subplot(2,1,2)
legend("n=10", "n=20", "n=30")