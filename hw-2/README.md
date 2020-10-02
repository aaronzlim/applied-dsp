# Applied DSP - Homework 2
Aaron Lim - 6 October 2020

## Background
In the real world, we have to deal with the limitations of practical devices. Practical DACs do not generate Dirac pulse train outputs. Instead, they generate analog signals using a Zero-Order Hold approach. With a Zero-Order Hold, each sample is held for the duration of the sample period. This causes what is known as sinc-rolloff to occur in the generated signal. In this homework assignment, you will investigate this phenomenon.

## Setup
Use your choice of software to generate a test signal consisting of the sum of three real sinusoids of the same amplitude. All three sinusoids should be of the same length.

The first sinusoid should have a frequency of $\frac{1}{16}f_s$. The second should have a frequency of $\frac{1}{4}f_s$. The third should have a frequency of $\frac{7}{16}f_s$.

Simulate the Zero-Order Hold of a DAC by repeating each sample 10 times. This is roughly equivalent to generating an analog signal using a DAC, and then sampling that signal with an ADC running at 10x the sample rate.

Use an FFT to examine the signal in the frequency domain.

## Questions
#### What happens to the relative amplitudes of the three sinusoids within the Nyquist region of the DAC?

#### How many times are the three sinusoids repeated in the frequency domain? Why is that? What must follow the DAC?

#### What techniques might we use to generate a higher- fidelity signal out of the DAC?