from typing import List

import numpy as np
from scipy.io.wavfile import read as read_wavfile
from tqdm import trange


def generate_sine_wave(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sine_wave = np.sin(2 * np.pi * freq * t)
    return sine_wave


def detect_tone_start_time_convolution(
    wav_file,
    target_freq=16_000,
    duration=0.1,
    threshold=50,
    chunk_size=1_000_000,
    downsample=1,
):

    # Load audio file
    sample_rate, audio_data = read_wavfile(wav_file)
    audio_data.astype("float")

    # Generate a sine wave at the target frequency
    sine_wave = generate_sine_wave(target_freq, duration, sample_rate)

    # Normalize both the audio data and the sine wave
    audio_data_normalized = audio_data / np.max(np.abs(audio_data))
    sine_wave_normalized = sine_wave / np.max(np.abs(sine_wave))

    # Calculate the number of chunks
    num_chunks = (len(audio_data) - len(sine_wave)) // chunk_size

    # Iterate over the chunks
    for i in trange(num_chunks + 1):
        start = i * chunk_size
        end = start + chunk_size + len(sine_wave) - 1
        if end > len(audio_data):
            end = len(audio_data)
        audio_chunk = audio_data_normalized[start:end]

        # Convolve the sine wave with the audio chunk
        convolved_signal = np.convolve(
            audio_chunk[::downsample],
            sine_wave_normalized[::downsample],
            mode='valid',
        )

        # Find the index of the highest peak in the convolved signal
        peak_index = np.argmax(np.abs(convolved_signal))

        # Check if the peak value is above the threshold
        if np.abs(convolved_signal[peak_index]) > threshold:
            # Convert the peak index to time in seconds and return it
            return (start + peak_index * downsample) / sample_rate

    # If the target frequency is not detected, return None
    return None


def find_all_tones(wav_files: List[str]) -> list:
    out = []
    start = 0
    for wav_file in wav_files:
        fs, memmap = read_wavfile(wav_file, memmap=True)
        tone_time = detect_tone_start_time_convolution(wav_file)
        if tone_time is not None:
            out.append(start + tone_time)
        start += len(memmap) / fs
    return out
