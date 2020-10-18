#!/usr/bin/env python

import numpy as np
from numpy.random import default_rng
from numpy.fft import fft, ifft, fftshift, fftfreq
from scipy import signal
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

    lfm_pw = 10e-6 # pulse width in seconds
    lfm_bw = 8e6 # bandwidth in Hz

    snr = -20 # dB

    num_taps = 64 # number of filter taps

    ### Processing ###

    fc = fs/4 # carrier frequency (purposely chose fs/4)

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
    ax[1].set_ylim([-50, max(L) + 5])
    ax[1].grid()
    ax[1].set_title('LFM Power Spectrum')
    ax[1].set_xlabel('Frequency (MHz)')
    ax[1].set_ylabel('Power (dBFS)')

    plt.tight_layout()
    plt.savefig('./hw-4/plots/lfm_no_carrier.png')
    plt.close()

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
    plt.savefig('./hw-4/plots/lfm_with_carrier.png')
    plt.close()

    # randomly place the pulses in time and add to noise vector
    pulse_starts = np.argwhere(rng.integers(low=0,
                                            high=2,
                                            size=num_possible_pulses))
    pulse_starts = pulse_starts * n_pw

    for ps in pulse_starts:
        sig = np.zeros(N).astype(complex)
        sig[ps[0] : ps[0]+n_pw] = lfm
        x += sig

    # plot the received signal
    t = np.arange(N) / fs
    plt.plot(t * 1e6, 20 * np.log10(np.abs(x)))
    plt.title(f'Randomly Placed LFM Pulses; SNR={snr}dB')
    plt.xlabel('Time (us)')
    plt.ylabel('Power (dBFS)')
    plt.savefig('./hw-4/plots/received_signal.png')
    plt.close()

    # The next step is digital demodulation
    # Because fc = fs/4, we can apply a bandpass filter, then
    # decimate by 4 to alias our carrier down to baseband

    # because the oscillator frequency is fs/4, its output will
    # repeat the sequence 1, 1j, -1, -1j

    osc = np.array([1, 1j, -1, -1j])
    # repeat the oscillator for the length of the filter
    osc = np.tile(osc, np.ceil(num_taps/4).astype(int))[:num_taps]
    lpf = signal.firwin(num_taps,
                        cutoff=fs/8,
                        width=1e6,
                        fs=fs)
    bpf = lpf * osc # combine lpf with osc to get bpf

    # apply the filter and decimate
    xf = np.convolve(x, bpf, mode='same')[::4]
    fsd = fs/4 # sample rate after decimation

    # going from 1.25GSps to 10MSps
    # which is a decimation factor of 125
    # break this down into 3x decimate by 5 stages

    # Create a filter with cutoff fs/5
    lpf_dec5 = signal.firwin(num_taps, cutoff=1/5, width=1/20)

    # apply the filter and decimate in 3 stages
    for _ in range(3):
        xf = np.convolve(xf, lpf_dec5)[::5]
        fsd /= 5

    # perform pulse compression
    # create the lfm but at our new sample rate after decimation
    lfm_10 = chirp(fs=fsd, pw=lfm_pw, bw=lfm_bw)
    r = np.abs(np.correlate(xf, lfm_10, mode='same')) # pulse compression

    # plot received vs processed data vs pulse compresion

    fig, ax = plt.subplots(3, 1)
    t1 = np.arange(len(x)) / fs
    t2 = np.arange(len(xf)) / fsd
    ax[0].plot(t1*1e6, 20 * np.log10(np.abs(x)))
    ax[0].set_title(f'Signal received at {fs/1e9}GSps')
    ax[0].set_xlabel('Time (us)')
    ax[0].set_ylabel('Power (dB)')

    ax[1].plot(t2*1e6, 20 * np.log10(np.abs(xf)))
    ax[1].set_title(f'Signal after decimation to {fsd/1e6}MSps')
    ax[1].set_xlabel('Time (us)')
    ax[1].set_ylabel('Power (dB)')
    ax[1].set_ylim(ax[0].get_ylim())

    ax[2].plot(t2*1e6, r)
    ax[2].set_title('Pulse Compression')
    ax[2].set_xlabel('Time (us)')
    ax[2].set_ylabel('Corr Mag')

    plt.tight_layout()
    plt.savefig('./hw-4/plots/pulse_compression.png')
    plt.close()
