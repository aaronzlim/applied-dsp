#!/usr/bin/env python

import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from matplotlib import pyplot as plt


def kronecker_delta(n: int, m: int = 0):
    """Generate a Kronecker delta function of length n and time shift t

    Args:
        n (int): Signal length in samples
        m (int, optional): Time shift in samples. Defaults to 0.

    Returns:
        [np.ndarray]: Kronecker delta function
    """
    z = np.zeros(n)
    z[m] = 1
    return z

def rect(n: int, pw: int):
    """Returns a rectangle pulse of width pw and amplitude 1

    Args:
        n (int): Number of total samples to return
        pw (int): Length of rectangle in samples

    Returns:
        np.ndarray: Rectangle waveform
    """
    return np.concatenate([np.ones(pw), np.zeros(n - pw)])

def dirac_comb(n: int, k: int):
    """Return a dirac comb of length n with comb spacing k

    Args:
        n (int): Total number of samples to return
        k (int): Spacing of each Kronecker delta in samples

    Returns:
        np.ndarray: Dirac comb
    """
    z = np.zeros(n)
    z[::k] = 1
    return z

if __name__ == '__main__':

    # Part 1: Visualizing Fourier Transforms
    N = 256
    pw = 64
    T = 64

    # generate delta, rect, and comb waveforms
    d = kronecker_delta(N)
    r = rect(N, pw)
    c = dirac_comb(N, T)

    # take the fourier transform of each function
    D = fftshift(fft(d)/N)
    R = fftshift(fft(r)/N)
    C = fftshift(fft(c)/N)

    # plot
    f = fftshift(fftfreq(N, d=1/N))

    fig, ax = plt.subplots(3, 2, figsize=(8, 6))

    ax[0][0].plot(d)
    ax[0][0].set_title('Kronecker Delta')
    ax[0][0].set_xlabel('Time (samples)')
    ax[0][0].set_ylabel('Amplitude')

    ax[0][1].plot(f, D.real)
    ax[0][1].plot(f, D.imag)
    ax[0][1].set_title('Kronecker Delta Fourier Transform')
    ax[0][1].set_xlabel('Frequency (samples)')
    ax[0][1].set_ylabel('Amplitude')
    ax[0][1].legend(['real', 'imag'])

    ax[1][0].plot(r)
    ax[1][0].set_title('Rectangle')
    ax[1][0].set_xlabel('Time (samples)')
    ax[1][0].set_ylabel('Amplitude')

    ax[1][1].plot(f, R.real)
    ax[1][1].plot(f, R.imag)
    ax[1][1].set_title('Rectangle Fourier Transform')
    ax[1][1].set_xlabel('Frequency (samples)')
    ax[1][1].set_ylabel('Amplitude')
    ax[1][1].legend(['real', 'imag'])

    ax[2][0].plot(c)
    ax[2][0].set_title('Dirac Comb')
    ax[2][0].set_xlabel('Time (samples)')
    ax[2][0].set_ylabel('Amplitude')

    ax[2][1].plot(f, C.real)
    ax[2][1].plot(f, C.imag)
    ax[2][1].set_title('Dirac Comb Fourier Transform')
    ax[2][1].set_xlabel('Frequency (samples)')
    ax[2][1].set_ylabel('Amplitude')
    ax[2][1].legend(['real', 'imag'])

    plt.tight_layout()
    plt.savefig('./hw-3/plots/fourier_transforms.png')
