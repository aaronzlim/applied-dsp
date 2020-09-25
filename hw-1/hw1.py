#!/usr/bin/env python

from pathlib import Path
import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from matplotlib import pyplot as plt

def sinusoid(sample_rate: float, frequency: float, duration: float, phase: float = 0):
    """Create a sinusoid with some sample rate, center frequency, duration, and initial phase."""
    t = np.arange(np.round(sample_rate * duration)) / sample_rate # time vector
    return np.exp((2j * np.pi * frequency * t) + phase)

def make_signal(sample_rate: float, frequency_list: list, duration: float, phase_list: list = []):
    """Generate a complex signal containing multiple frequencies."""

    if not phase_list:
        phase_list = np.zeros(len(frequency_list))

    if len(frequency_list) != len(phase_list):
        raise ValueError('List of frequencies and phases must be the same length')

    N = np.round(sample_rate * duration).astype(int) # number of samples
    x = np.zeros(N).astype(np.complex)
    for freq, phase in zip(frequency_list, phase_list):
        x += sinusoid(sample_rate, freq, duration, phase)

    return x

def time_domain_plot(signal: np.ndarray, sample_rate: float, axis=None):
    if axis is None:
        axis = plt.gca()

    t = np.arange(len(signal)) / sample_rate
    axis.plot(t, signal.real, '-o')
    axis.plot(t, signal.imag, '-o')
    axis.set_title('Time Domain')
    axis.set_xlabel('Time (s)')
    axis.set_ylabel('Amplitude')
    axis.grid()
    axis.legend(['real', 'imag'])

def frequency_domain_plot(signal: np.ndarray, sample_rate: float,
                          axis=None, normalize: bool = False):
    if axis is None:
        axis = plt.gca()

    f = fftshift(fftfreq(len(signal), d=1/sample_rate))
    eps = np.finfo(np.complex).eps
    X = 20 * np.log10(np.abs(fftshift(fft(signal)/len(signal))) + eps)
    if normalize:
        X -= max(X)
    axis.plot(f, X)
    axis.set_title('Frequency Domain')
    axis.set_xlabel('Frequency (Hz)')
    axis.set_ylabel('Log Mag (dB)')
    axis.grid()

if __name__ == '__main__':

    freq_list = [100, 200, 300] # Signal frequenies in Hz
    T = 300e-3 # signal duration in seconds
    fs_list = [450, 600, 610, 3000] # sample rates in Sps

    # Part 1 - Sampling

    for fs in fs_list:
    # create a signal composed of multiple sinusoids sampled at fs
        x = make_signal(fs, freq_list, T)

        time_axis = plt.subplot(2, 1, 1)
        time_domain_plot(signal=x, sample_rate=fs, axis=time_axis)

        freq_axis = plt.subplot(2, 1, 2)
        frequency_domain_plot(signal=x, sample_rate=fs, axis=freq_axis)

        plt.tight_layout()
        fig_name = Path('./hw-1/plots/comparing_sample_rates_{}_Sps.png'.format(fs)).resolve()
        plt.savefig(fig_name)
        plt.close()

    # Part 2 - Quantization
    bits_list = [2, 4, 6, 8, 12, 14, 16]
    x = make_signal(max(fs_list), freq_list, T)
    x_max = max(max(x.real), max(x.imag))
    for num_bits in bits_list:
        ampl = 2**(num_bits-1) - 1
        xq = x * ampl / x_max
        xq = np.round(xq)
        frequency_domain_plot(signal=xq, sample_rate=fs_list[-1], normalize=True)
        plt.ylim([-150, 5])
        fig_name = './hw-1/plots/quant_noise_{}_bits.png'.format(num_bits)
        plt.savefig(fig_name)
        plt.close()
