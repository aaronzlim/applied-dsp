#!/usr/bin/env python

import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from matplotlib import pyplot as plt

def sinusoid(frequency: float, fs: float, duration: float, phase: float = 0) -> np.array:
    t = np.arange(round(fs * duration)) / fs
    return np.exp((2j * np.pi * frequency * t) + phase)

if __name__ == '__main__':

    # user setup
    fs = 50e3 # original signal sample rate in Hz
    T = 16/fs # signal duration in seconds
    upsample_rate = 10

    # derived parameters
    N = round(fs * T)
    freqs = np.array((1/16, 4/16, 7/16)) * fs
    fs_adc = fs * upsample_rate # sample rate of the interpolating ADC

    # create the DAC output
    x = np.zeros(N, dtype=np.dtype(complex))
    for f in freqs:
        x += sinusoid(f, fs, T)
    # apply zero-order hold
    x_zoh = np.repeat(x, upsample_rate)

    eps = np.finfo(x_zoh.dtype).eps # machine epsilon
    # add eps before log to avoid infinity (log(0) = -inf)

    # compute the power spectrum of x
    X = 20 * np.log10(np.abs(fftshift(fft(x)/len(x))) + eps) # pure spectrum
    fx = fftshift(fftfreq(len(X), d=1/fs)) # frequency vector with original sample rate fs in Hz

    # compute the power spectrum of x after the DAC
    X_zoh = fftshift(fft(x_zoh)/len(x_zoh)) + eps
    X_zoh_mag = 20 * np.log10(np.abs(X_zoh)) # power spectrum in dBm
    f = fftshift(fftfreq(len(X_zoh_mag), d=1/fs_adc)) # frequency vector for ADC sample rate in Hz

    # calculate the samples of our tones so we can mark them in a plot
    tone_samples = [np.argmin(np.abs(f - freq)) for freq in freqs]

    # calculate the DAC frequency response
    z = (f * np.pi / fs) + eps
    H = np.abs(np.sin(z)/z)
    H_mag = 20 * np.log10(H)

    # create a lowpass filter with the inverse of the DAC frequency response
    Ndc = round(len(H)/2)
    Nbw_half = round(fs * len(H) / (2*fs_adc)) # half passband bandwidth in samples
    G = 1/H
    G[:Ndc - Nbw_half] = 0 # make the stopband zero
    G[Ndc + Nbw_half:] = 0
    G_mag = 20 * np.log10(np.abs(G) + eps)

    # apply the pre-equalizing filter in the frequency domain
    Xr = X_zoh * G
    Xr_mag = 20 * np.log10(np.abs(Xr) + eps)

    ### PLOTS ###

    # plot the pure spectrum
    plt.figure()
    plt.plot(fx/1000, X)
    plt.title('Pure Power Spectrum')
    plt.xlabel('Frequency (kHz)')
    plt.ylabel('Power (dBm)')
    plt.xlim([-fs_adc/2000, fs_adc/2000])
    plt.ylim([-50, 10])
    plt.grid()

    plt.savefig('./hw-2/plots/pure_spectrum.png')
    plt.close()

    # plot the spectrum after the DAC/ADC
    plt.figure()
    plt.plot(f/1000, X_zoh_mag, label='ADC Output')
    plt.plot(f[tone_samples]/1000, X_zoh_mag[tone_samples], 'bv', label='Markers')
    plt.plot(f/1000, H_mag, '--', label=r'sinc($\frac{\pi f}{fs}$)')
    plt.title('Power Spectrum After ZOH DAC and Interpolating ADC')
    plt.xlabel('Frequency (kHz)')
    plt.ylabel('Power (dBm)')
    plt.ylim([-50, 10])
    plt.grid()
    plt.legend(loc='upper right', fancybox=True)

    annotation_x_offsets = [-60, 10, 10]
    annotation_y_offsets = [1, 0, -1]
    for samp, xoffset, yoffset in zip(tone_samples,
                                      annotation_x_offsets,
                                      annotation_y_offsets):
        plt.annotate('{} dBm'.format(round(X_zoh_mag[samp], 2)),
                     xy=(f[samp]/1000 + xoffset, X_zoh_mag[samp] + yoffset))

    plt.savefig('./hw-2/plots/adc_spectrum.png')
    plt.close()

    # plot the spectrum of the pre-equalizing filter
    plt.figure()
    plt.plot(f/1000, G_mag)
    plt.title('Ideal Inverse Sinc LPF')
    plt.xlabel('Frequency (kHz)')
    plt.ylabel('Gain (dB)')
    plt.grid()
    plt.xlim([-fs_adc/2000, fs_adc/2000])
    plt.ylim([-100, 10])

    plt.savefig('./hw-2/plots/pre_equalization_filter.png')
    plt.close()

    # plot the spectrum of the equalized signal
    plt.figure()
    plt.plot(f/1000, Xr_mag)
    plt.title('Equalized Signal')
    plt.xlabel('Frequency (kHz)')
    plt.ylabel('Power (dBm)')
    plt.xlim([-fs_adc/2000, fs_adc/2000])
    plt.ylim([-50, 10])
    plt.grid()

    plt.savefig('./hw-2/plots/equalized signal')
    plt.close()
