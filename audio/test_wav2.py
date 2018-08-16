import matplotlib.pyplot as plt
from scipy.io import wavfile # get the api
from scipy.fftpack import fft
from pylab import *

class MyClass():
    def __init__(self, a):
        self.a = a

    def a_squared(self):
        return self.a*self.a

def wav_fft(filename):
    fs, data = wavfile.read(filename) # load the data
    a = data # this is a two channel soundtrack, I get the first track
    b=[(ele/2**8.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
    c = fft(b) # create a list of complex number
    d = len(c)/2  # you only need half of the fft list
    plt.plot(abs(c[:,(d-1)]),'r')
    savefig(filename+'.png',bbox_inches='tight')


if __name__ == "__main__":
    wav_fft("test.wav")