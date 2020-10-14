#!/usr/bin/env python

from pathlib import Path
import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from matplotlib import pyplot as plt

def sinusoid(sample_rate: float, frequency: float, duration: float, phase: float = 0) -> np.ndarray:
    """Create a sinusoid with some sample rate, center frequency, duration, and initial phase."""
    t = np.arange(np.round(sample_rate * duration)) / sample_rate # time vector
    return np.exp((2j * np.pi * frequency * t) + phase)

def get_quantization_levels(amplitude: float, num_bits: int):
    """Return quantization levels for a given amplitude and number of bits.

    Uses Mid-Rise algorithm: -A + delta/2 + delta*(0, 1, 2, ..., 2**num_bits - 1)
    """
    num_levels = 2**num_bits # number of quantization levels
    delta = 2*amplitude / num_levels # distance between levels
    return (-amplitude + delta/2) + (np.arange(num_levels) * delta)

def quantize(signal: np.ndarray, levels: np.ndarray) -> np.ndarray:
    X = signal.reshape((-1,1)) # column vector
    L = levels.reshape((1,-1)) # row vector
    distances = abs(X-L) # distances between each sample and each quantization level
    nearestIndex = distances.argmin(axis=1) # find closest quantization level for each sample
    return L.flat[nearestIndex].reshape(signal.shape) # quantized signal

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

    return X, f

if __name__ == '__main__':

    freq_list = [100, 200, 300] # Signal frequenies in Hz
    T = 300e-3 # signal duration in seconds
    fs_list = [450, 600, 610, 3000] # sample rates in Sps

    # Part 1 - Sampling

    for fs in fs_list:
        # create a signal composed of multiple sinusoids sampled at fs
        x = np.zeros(round(T * fs)).astype(complex)
        for freq in freq_list:
            x += sinusoid(fs, freq, T)
        x /= len(freq_list) # bount amplitude to [-1, +1]

        # plot time domain and frequency domain
        time_axis = plt.subplot(2, 1, 1)
        time_domain_plot(signal=x, sample_rate=fs, axis=time_axis)
        freq_axis = plt.subplot(2, 1, 2)
        frequency_domain_plot(signal=x, sample_rate=fs, axis=freq_axis)

        # save the figure
        plt.tight_layout()
        fig_name = Path('./hw-1/plots/comparing_sample_rates_{}_Sps.png'.format(fs)).resolve()
        plt.savefig(fig_name) # TODO: change figure size
        plt.close()

    # Part 2 - Quantization
    bits_list = [2, 4, 6, 8, 10, 12, 14, 16]

    # generate the signal
    x = np.zeros(round(T * fs_list[-1])).astype(complex)
    for freq in freq_list:
        x += sinusoid(fs_list[-1], freq, T)
    x = x / len(freq_list) # bound amplitude to [-1, +1]
    x_max = max(max(x.real), max(x.imag))

    Ps = np.sum(np.power(abs(x), 2)) # power of the pure signal

    sqnr_list = [] # list to store SNR results

    f = fftshift(fftfreq(len(x), d=1/fs_list[-1])) # frequency vector

    for num_bits in bits_list:
        quantization_levels = get_quantization_levels(x_max, num_bits)
        xq_I = quantize(x.real, quantization_levels) # quantized signal
        xq_Q = quantize(x.imag, quantization_levels)
        xq = xq_I + 1j*xq_Q
        nq = x - xq # quantization noise = pure signal - quantized signal
        Pn = np.sum(np.power(abs(nq), 2))
        sqnr_list.append(10 * np.log10(Ps/Pn))

        Xq = 20 * np.log10(abs(fftshift(fft(xq) / len(xq))))
        plt.plot(f, Xq)
        plt.title('Power Specturm ({} bits)'.format(num_bits))
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Log Mag (dB)')
        plt.ylim([-150, 0])
        plt.grid()
        fig_name = './hw-1/plots/spectrum_{}_bits.png'.format(num_bits)
        plt.savefig(fig_name)
        plt.close()

    snr_theory = [1.76 + 6.02*b for b in bits_list]
    db_per_bit = round(np.mean(np.diff(sqnr_list)/np.diff(bits_list)), 2)

    plt.plot(bits_list, sqnr_list, '--o')
    plt.plot(bits_list, snr_theory, '--o')
    plt.title('SQNR vs Number of Bits')
    plt.xlabel('Number of Bits')
    plt.ylabel('SQNR (dB)')
    plt.legend(['Measured SQNR', '1.76 + 6.02*b'])

    annotation_idx = round(len(bits_list)/2)
    plt.annotate('slope = {} dB/bit'.format(db_per_bit),
                 xy=(bits_list[annotation_idx], sqnr_list[annotation_idx]),
                 xytext=(bits_list[annotation_idx], sqnr_list[annotation_idx]-10),
                 arrowprops=dict(arrowstyle='simple', facecolor='black'))

    plt.savefig('./hw-1/plots/sqnr_vs_num_bits.png')
    plt.close()
