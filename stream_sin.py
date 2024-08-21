import numpy as np
from pylsl import StreamInfo, StreamOutlet, local_clock
import time

# Parameters for the sine wave
fs = 10  # Sampling frequency (Hz)
f = 1    # Frequency of the sine wave (Hz)
duration = 100  # Duration of the signal in seconds

# Create LSL stream info and outlet
info = StreamInfo('SineWave', 'EEG', 1, fs, 'float32', 'myuid34234')
outlet = StreamOutlet(info)

print("Now sending data...")

# Generate sine wave data
t = np.arange(0, duration, 1/fs)
sine_wave = np.sin(2 * np.pi * f * t)

# Stream the data
start_time = local_clock()
for i in range(len(sine_wave)):
    # Get current time
    current_time = local_clock()
    # Calculate the sample delay
    sample_delay = start_time + (i / fs) - current_time
    # Send sample with timestamp
    outlet.push_sample([sine_wave[i]], timestamp=current_time + sample_delay)
    # Wait to simulate real-time sampling
    time.sleep(1/fs)

print("Done sending data.")
