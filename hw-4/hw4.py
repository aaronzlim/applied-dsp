#!/usr/bin/env python

import numpy as np
from numpy.random import default_rng
from numpy.fft import fft, fftshift, fftfreq
from matplotlib import pyplot as plt

def chirp(fs: float, pw: float, bw: float):
    """Generate a complex linearly frequency modulated signal at baseband.

    Args:
        fs (float): Sample rate in Sps
        pw (float): Pulse width in seconds
        bw (float): Bandwidth in Hz

    Returns:
        np.ndarray: LFM as a complex signal at baseband.
    """
    t = np.arange(start=-pw/2, stop=pw/2, step=1/fs)
    return np.exp((1j * np.pi * bw / pw) *  np.power(t, 2))

if __name__ == '__main__':

    ### Setup ###

    rng_seed = 123 # seed for random number generator

    T = 1e-3 # analysis time in seconds
    fs = 5e9 # sample rate in Sps
    fc = 1250e6 # carrier frequency (purposely chose fs/4)

    lfm_pw = 10e-6 # pulse width in seconds
    lfm_bw = 8e6 # bandwidth in Hz

    snr = -5 # dB

    ### Processing ###

    rng = default_rng(rng_seed) # random number generator

    N = round(fs*T) # number of samples to process
    n_pw = round(fs * lfm_pw) # pulse width in samples
    num_possible_pulses = round(T / lfm_pw)

    # start by generating noise
    x = (1/np.sqrt(2)) * (rng.normal(size=N) + 1j*rng.normal(size=N))
    p_noise = np.var(x)

    # generate LFM at required SNR
    p_sig = (10**(snr/10)) * p_noise
    lfm = chirp(fs=fs, pw=lfm_pw, bw=lfm_bw)
    lfm *= np.sqrt(p_sig) / np.std(lfm)

    # plot the lfm
    fig, ax = plt.subplots(2, 1)

    t = np.arange(n_pw) / fs
    ax[0].plot(t*1e6, lfm.real)
    ax[0].plot(t*1e6, lfm.imag)
    ax[0].grid()
    ax[0].set_title('LFM Time Domain')
    ax[0].set_xlabel('Time (us)')
    ax[0].set_ylabel('Amplitude')
    ax[0].legend(['Real', 'Imag'], loc='upper right')

    f = fftshift(fftfreq(n_pw, d=1/fs))
    L = 20 * np.log10(np.abs(fftshift(fft(lfm)/n_pw)))
    ax[1].plot(f/1e6, L)
    ax[1].set_xlim([-lfm_bw*1e-6, lfm_bw*1e-6])
    ax[1].set_ylim([-50, 0])
    ax[1].grid()
    ax[1].set_title('LFM Power Spectrum')
    ax[1].set_xlabel('Frequency (MHz)')
    ax[1].set_ylabel('Power (dBFS)')

    plt.tight_layout()
    plt.show()

    # modulate onto a carrier
    lfm *= np.exp(2j * np.pi * fc * np.arange(n_pw) / fs)

    # plot the modulated LFM

    fig, ax = plt.subplots(2, 1)

    t = np.arange(n_pw) / fs
    ax[0].plot(t*1e6, lfm.real)
    ax[0].plot(t*1e6, lfm.imag)
    ax[0].grid()
    ax[0].set_title('LFM with Carrier Time Domain')
    ax[0].set_xlabel('Time (us)')
    ax[0].set_ylabel('Amplitude')
    ax[0].legend(['Real', 'Imag'], loc='upper right')

    f = fftshift(fftfreq(n_pw, d=1/fs))
    L = 20 * np.log10(np.abs(fftshift(fft(lfm)/n_pw)))
    ax[1].plot(f/1e6, L)
    ax[1].grid()
    ax[1].set_title('LFM with Carrier Power Spectrum')
    ax[1].set_xlabel('Frequency (MHz)')
    ax[1].set_ylabel('Power (dBFS)')

    plt.tight_layout()
    plt.show()

    # randomly place the pulses in time and add to noise vector
    pulse_starts = np.argwhere(rng.integers(low=0,
                                            high=2,
                                            size=num_possible_pulses))
    pulse_starts = pulse_starts * n_pw

    for ps in pulse_starts:
        sig = np.zeros(N).astype(complex)
        sig[ps[0] : ps[0]+n_pw] = lfm
        x += sig

    # plot the signal plus noise
    t = np.arange(N) / fs
    plt.plot(t * 1e6, 20 * np.log10(np.abs(x)))
    plt.title(f'Randomly Placed LFM Pulses; SNR={snr}dB')
    plt.xlabel('Time (us)')
    plt.ylabel('Power (dBFS)')
    plt.show()

    # TODO: Demodulate x (step 10)
    # use the fs/4 trick as the first decimation stage
    # then decimate again to 10MSps
