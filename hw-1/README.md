# Applied DSP - Homework 1
Aaron Lim - 29 September 2020

# Your DSP Experience

## On the project you are currently doing:

### What Signal Processing is being done?
**NOTE:** If there is no DSP on your project, go ask about a different project.

Lots of signal processing, filtering, rate conversion, modulation, demodulation, carrier recovery, correlation; you name it.

### What DSP hardware?  FPGA? DSP? PC? Etc.
I have seen projects use any and all of those options. FPGA's are popular because they are fast, but processing on a PC is also useful to decrease development time.

### Which ADC and DAC?  How many bits?  What is the sample rate?
There's a small software defined radio (SDR) that I often use, which contains two transceiver IC's. Each uses a 12-bit ADC and samples at 60MSps. In addition, there is an arbitrary waveform generator block in firmware that contains several optional upsampling filters, allowing you to take in data at a few other rates less than 60MSps.

# Sampling

## Using either Matlab, Simulink, or Python

### Create a signal composed of multiple sinusoids of different frequencies
The signal chosen is composed of three complex sinusoids at frequencies:
- f1 = 100 Hz
- f2 = 200 Hz
- f3 = 300 Hz

### Sample this signal at different sampling rates
##### Sampling at 450Sps (1.5x f<sub>max</sub>)
Note the 300Hz component has been aliased.

<p align="center">
    <img src="plots/comparing_sample_rates_450_Sps.png" alt="Sampled at 450Sps" width="500"/>
</p>

##### Sampling at 600Sps (2x f<sub>max</sub>)
Note the 300Hz component is at the very edge of the band, and due to the limited FFT resolution, it appears at -300Hz.

<p align="center">
    <img src="plots/comparing_sample_rates_600_Sps.png" alt="Sampled at 600Sps" width="500"/>
</p>

##### Sampling at 610Sps (2.03x f<sub>max</sub>)
Note that no aliasing occurs, but with very little margin for frequency error.

<p align="center">
    <img src="plots/comparing_sample_rates_610_Sps.png" alt="Sampled at 610Sps" width="500"/>
</p>

##### Sampling at 3000Sps (10x f<sub>max</sub>)
Note that aliasing does not occur, and there is a lot of margin for frequency error.

<p align="center">
    <img src="plots/comparing_sample_rates_3000_Sps.png" alt="Sampled at 3000Sps" width="500"/>
</p>

#### What is the minimum sampling rate allowed?
The data shows that to prevent aliasing, the sample rate of your system must be greater than twice the highest frequency of the received signal. This is known as the Nyquist Criterion.

<p align="center">
    Nyquist Criterion: f<sub>s</sub> > 2f<sub>max</sub>
</p>

Real systems must account for non-idealities in their hardware, which can lead to frequency errors. It is important to operate well above the Nyquist rate.

# Quantization

### Quantize the signal, using quantizing levels (i.e. different numbers of bits)
Signals were quantized using a mid-rise quantizer, with levels:

<p align="center">
    -A + D/2 + D .* (0, 1, 2, ..., q-1)
</p>

Where:

A = Full Scale Amplitude

q = number of levels = 2<sup>num_bits</sup>

D = The distance between levels = 2A / q

.* = point-wise multiplication operator

Because the signal under test is complex, the real and imaginary (I and Q) data streams were quantized separately.

#### Analyze the spectrum of the signal

<p align="center">
    <img src="plots/spectrum_2_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_4_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_6_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_8_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_10_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_12_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_14_bits.png" alt="SQNR with 2 bits" width="330"/>
    <img src="plots/spectrum_16_bits.png" alt="SQNR with 2 bits" width="330"/>
</p>

#### How does the quantizing level affect the noise floor of the spectrum?

It is clear from the plots that more bits leads to a lower noise floor.

#### For each new bit added, how much does the noise floor decrease?

Quantization noise was measured as:

<p align="center">
    Noise Signal = Pure Signal - Quantized Signal
</p>

Power for both the pure and noise signals was measured as:

<p align="center">
    P = sum( |x|<sup>2</sup> )
</p>

And Signal to Quantization Noise Ratio (SQNR) was measured as the ratio of the power of the pure signal to the power of the quantization noise.

<p align="center">
    SQNR = P<sub>s</sub> / P<sub>n</sub>
</p>
<p align="center">SQNR<sub>dB</sub> = 10Log<sub>10</sub>(SQNR)</p>

In DSP literature (for example [Analog Devices MT-229](https://www.analog.com/media/en/training-seminars/tutorials/MT-229.pdf)) it is common to estimate the SQNR of a quantized full-scale sine wave as:

<p align="center">SQNR<sub>dB</sub> = 1.76 + 6.02*b [dB]
</p>

Where b is the number of bits.

Both my data and the theoretical data are provided in the plot below. The magnitudes may not match because the theoretical estimate uses a sine wave, where as my signal is a superposition of sine waves. But as you will see, the trend lines will have matching slopes, because that depends only on the number of bits used.

<p align="center">
    <img src="plots/sqnr_vs_num_bits.png" alt="SQNR vs Number of Bits" width="750"/>
</p>

For each bit added, the quantization noise increases by approximately 6dB.
