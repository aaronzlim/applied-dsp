#!/usr/bin/env python

import timeit
import numpy as np
from numpy.fft import fft, ifft
from matplotlib import pyplot as plt

if __name__ == '__main__':

    N = 256
    x1 = np.concatenate([np.zeros(int(N/4)), np.ones(int(N/2)), np.zeros(int(N/4))])
    x2 = np.zeros(N)
    x2[int(N/8): int(N/8) + 16] = np.arange(16)

    rc = np.convolve(x1, x2)[:N]
    rf = ifft(fft(x1) * fft(x2))

    print('np.allclose(rc, rf):', np.allclose(rc, rf))

    fig, ax = plt.subplots(2, 2, figsize=(10, 6))

    ax[0][0].plot(x1)
    ax[0][0].set_title('Signal 1')
    ax[0][0].set_xlabel('Samples')
    ax[0][0].set_ylabel('Amplitude')

    ax[0][1].plot(rc)
    ax[0][1].set_title('Output of Convolution in the Time Domain')
    ax[0][1].set_xlabel('Samples')
    ax[0][1].set_ylabel('Amplitude')

    ax[1][0].plot(x2)
    ax[1][0].set_title('Signal 2')
    ax[1][0].set_xlabel('Samples')
    ax[1][0].set_ylabel('Amplitude')

    ax[1][1].plot(rf.real)
    ax[1][1].set_title('Output of Multiplication in the Frequency Domain')
    ax[1][1].set_xlabel('Samples')
    ax[1][1].set_ylabel('Amplitude')

    plt.tight_layout()
    plt.savefig('./hw-3/plots/conv_vs_mult.png')
    plt.close()

    # time convolution vs multiplication for different signal sizes

    M = (64, 84, 256, 732, 1024, 3096, 8192)
    conv_results = []
    mult_results = []

        # convolution in the time domain
    stmt_conv = """
rc = np.convolve(x1, x2)
        """

        # multiplication in the frequency domain
    stmt_mult = """
rf = ifft(fft(x1) * fft(x2))
        """

    for n in M:

        # Setup
        setup_str = f"""
import numpy as np
from numpy.fft import fft, ifft
N = {n}
x1 = np.concatenate([np.zeros(int(N/4)), np.ones(int(N/2)), np.zeros(int(N/4))])
x2 = np.zeros(N)
x2[int(N/8): int(N/8) + 16] = np.arange(16)
        """

        conv_results.append(timeit.timeit(stmt=stmt_conv, setup=setup_str, number=1000))
        mult_results.append(timeit.timeit(stmt=stmt_mult, setup=setup_str, number=1000))

    plt.plot(M, conv_results, '--o')
    plt.plot(M, mult_results, '--o')
    plt.title('Processing Time for Convolution Algorithms')
    plt.xlabel('Array Size')
    plt.ylabel('Processing Time (s)')
    plt.legend(['Convolution in TD', 'Multiplication in FD'])
    plt.grid()
    plt.savefig('./hw-3/plots/processing_time.png')



