clear all;
close all;

% Define the FFT size that you used (1024, 2048, etc)
Params.FFT_SIZE = 2048;

% Define sampling rate
Params.FS = 1e6;

%%%%% Tunable parameters %%%%%

% How many vectors do you want to use for the running average
Params.NUM_AVG_WINDOW = 5;

% What power threshold do you want to use to trigger an event detection
Params.THRESHOLD = 12;

% How many samples to average for the baseline 
Params.AVG_N = 100;

%%% Read File %%%
fileName = 'fft_mac_laptop.bin';
fileID = fopen(fileName, 'r');
x = fread(fileID, 'float');

% Note that the GNURadio scrip performs a log power FFT 
% before saving data to a file. We will perform an FFT shift here. 
x = fftshift(x);

% Reshape the data 
T = length(x)/Params.FFT_SIZE;
spectra = reshape(x,[Params.FFT_SIZE,T]);

% Compute Avreaged frames, every NUM_AVG_WINDOW samples of FFT vectors
spectra_avg = zeros(Params.FFT_SIZE, floor(size(spectra,2)/Params.NUM_AVG_WINDOW) );
count = 1;
for i = 1:Params.NUM_AVG_WINDOW:size(spectra,2) - Params.NUM_AVG_WINDOW
    spectra_avg(:,count) = mean(spectra(:, i:i + Params.NUM_AVG_WINDOW -1), 2);
    count = count + 1;
end

% Compute frequency rang
N=length(spectra_avg);
if mod(N,2)==0
    k=-N/2:N/2-1; % N even
else
    k=-(N-1)/2:(N-1)/2; % N odd
end
T=N/Params.FS;
freq=k/T;

% Generate Baseline
baseline = sum(spectra_avg(:,(1:Params.AVG_N)),2)/Params.AVG_N;

% Subtract baseline
yn = spectra_avg-baseline;



% Perform event detection 
[rows,columns] = size(yn);
events = [];
i = 1;
while i < columns
    if max(yn(:,i)) >= Params.THRESHOLD
        e_start = i;  
        j = i+1;
        k = columns;
        
        while j ~= k
            if max(yn(:,j)) >= Params.THRESHOLD && max(yn(:,j+1)) < Params.THRESHOLD
                new = [e_start,j];
                events = [events;new];
                i = j+1;
                j = k;
            elseif j+1 == k
                new = [e_start,j];
                events = [events;new];
                i = j + 1;
                j = k;
            else
                j = j+1;
            end
        end    
    else
        i = i +1;
    end
end

%%%%%%%%%%%% Plot Results %%%%%%%%%%%%

% Plot the original recording 
figure(1);
imagesc((spectra_avg)); axis off; title('Original')
hold on; box off;
a1 = axes('YAxisLocation', 'Left');
set(a1, 'color', 'none')
set(a1, 'YLim', [freq(1) freq(2048)]);
set(a1, 'XLim', [0 376]);    
%ax = gca;
%ax.YRuler.Exponent = 0;
xlabel('Time');
ylabel('Frequency (Hz)');
%colorbar('eastoutside'); 

% Plot the filtered spectra (baseline subtracted)
figure(2);
imagesc((yn)); axis off; title('Filtered')
hold on; box off;
a1 = axes('YAxisLocation', 'Left');
set(a1, 'color', 'none')
set(a1, 'YLim', [freq(1) freq(2048)]);
set(a1, 'XLim', [0 376]);   
%ax = gca;
%ax.YRuler.Exponent = 0;
%colorbar('eastoutside');  
 

% Plot the filtered spectra with events marked
figure(3);
imagesc((yn)); axis off; title('Events Marked')
format long g;
for l=1:length(events)
     x1 = [events(l,1),events(l,1)];
     x2 = [events(l,2), events(l,2)];
     y = [0,2000];
     line(x1,y, 'Color', 'red','LineWidth',1);
     line(x2,y, 'Color', 'blue', 'LineWidth', 1);
end

hold on; box off;
a1 = axes('YAxisLocation', 'Left');
set(a1, 'color', 'none')
set(a1, 'YLim', [freq(1) freq(2048)]);
set(a1, 'XLim', [0 376]);    
%ax = gca;
%ax.YRuler.Exponent = 0;
%colorbar('eastoutside');  

