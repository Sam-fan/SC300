from rasp_libhackrf import *
from pylab import *
import matplotlib.pyplot as plt
import numpy as np

hackrf = HackRF()

target_freq=2412e6
hackrf.sample_rate = 200e6
shift=3e6

##CORRECT IQ
'''
hackrf.center_freq = target_freq-shift
sn = hackrf.get_serial_no()
samples = hackrf.read_samples()
powe1,freqs1=psd(samples, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)


hackrf.center_freq = target_freq+shift
sn = hackrf.get_serial_no()
samples = hackrf.read_samples()
powe2,freqs2=psd(samples, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)
plt.clf()
align=round(2*shift*1024/(hackrf.sample_rate))
powe=[]
for n in range (align,len(freqs1)):
    powe.append(min(round(10*np.log10(powe1[n]),2),round(10*np.log10(powe2[n-align]),2)))
freq=freqs1[align:]
plt.plot(freq,powe)
xlabel('Frequency (MHz)')
ylabel('Relative power (dB)')
plt.show()
print(max(powe[len(powe)//2],powe[len(powe)//2+1],powe[len(powe)//2-1]))
'''

#fetch target power
hackrf.center_freq = target_freq-shift
sn = hackrf.get_serial_no()
while True:
    samples = hackrf.read_samples()
    powe,freqs=psd(samples, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)
    target_power=powe[round((target_freq-(hackrf.center_freq-hackrf.sample_rate//2))*1024/(hackrf.sample_rate))]
    print(round(20*np.log10(target_power),2))
