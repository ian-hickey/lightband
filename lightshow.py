import serial
import time
import numpy as np
import simpleaudio as sa
import threading
import os
import sounddevice as sd
import colorsys
from rpi_ws281x import PixelStrip, Color
import time


# Play your audio file
wave_obj = sa.WaveObject.from_wave_file('alliwantforchristmasisyou.wav')
play_obj = wave_obj.play()
play_obj.wait_done()

CHANNELS = 1
RATE = 44100
CHUNK = 1024  # Number of audio samples per frame

# LED strip configuration
NUM_LEDS = 50       # We have 1000, but one strip for testing 
NUM_BANDS = 3       # Number of bands (e.g., bass, mids, highs)
LEDS_PER_BAND = 16  # Closest to 50 evenly.

# Path to the audio file
AUDIO_FILE = 'alliwantforchristmasisyou.wav'


def frequency_to_color(frequency_index, num_frequencies, brightness):
    # Map the frequency index to a hue between 0 and 270 degrees (you can adjust this range as needed)
    hue = (frequency_index / num_frequencies) * 270
    # Set saturation to 100% and value according to the brightness
    saturation = 1.0
    value = brightness / 255.0
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation, value)
    # Convert RGB from 0-1 range to 0-255 range and return as hex
    return '{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

# Function to play audio using simpleaudio
def play_audio(audio_path):
    wave_obj = sa.WaveObject.from_wave_file(audio_path)
    play_obj = wave_obj.play()

def audio_callback(indata, frames, time, status):
    # This function will be called by sounddevice for each audio block

    # Convert the input audio data to an numpy array for FFT
    audio_data = np.frombuffer(indata, dtype=np.float32)
    
    # Perform FFT on the audio data
    fft_result = np.fft.fft(audio_data)
    
    # Process the FFT result to control the LED strip
    # For example, you might want to take the magnitude of the FFT result
    # to determine how to light the LEDs
    light_leds(fft_result)
    
def main():
    while True:
        # Example commands to control the lights.
        # To set a light manually, use `light <index> <color> <duration> <brightness>`
        # To light many lights at once, send `light <index> <color> <duration> <brightness>;<index> <color> <duration> <brightness>;...;<index> <color> <duration> <brightness>`

        cmd = input("Enter command (chase, sparkle, fire, wipe, rainbow, ukraine, light, song, off): ")

        if cmd == "song":
             play_song()
        else:      
            send_command(cmd)
        if cmd == "off":
            break

def light_leds(frequency_data):
    print(f"Lighting LEDS")
    # Calculate the magnitudes from the complex numbers
    magnitudes = np.abs(frequency_data)

    # Normalize the magnitudes
    normalized_magnitudes = magnitudes / np.max(magnitudes)

    # Number of frequency bins per LED
    bins_per_led = len(frequency_data) // LED_COUNT

    # Average the bins for each LED
    led_brightness = np.array([np.mean(normalized_magnitudes[i*bins_per_led:(i+1)*bins_per_led]) for i in range(LED_COUNT)])

    # Map to brightness
    brightness_values = (led_brightness * 255).astype(int)

    # Generate a color for each LED
    colors = [colorsys.hsv_to_rgb(i / LED_COUNT, 1, led_brightness[i]) for i in range(LED_COUNT)]

    # Format the colors as hexadecimal
    hex_colors = ['{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in colors]
   
    # Construct the command strings
    led_commands = [f'light {i} {color} {brightness_values[i]};' for i, color in enumerate(hex_colors)]
        
    # Send to Arduino
    print(''.join(led_commands))
    send_command(''.join(led_commands))
    
def send_command(command):
    print(f"Command: {command}")

def play_song():
     print("Playing song")
     # Thread to play audio
     audio_thread = threading.Thread(target=play_audio, args=(AUDIO_FILE,))
     audio_thread.start()
     #with sd.InputStream(callback=audio_callback):
        # Just keep the main thread alive while audio processing is done in the callback
     #   while True:
     #       time.sleep(0.1)

def analyze_stream():
    print("Starting audio analysis")
    try:
        while True:
            # Read new audio stream data
            data = stream.read(CHUNK, exception_on_overflow=False)
            # Process the new data
            audio_data = np.frombuffer(data, dtype=np.int16)
            fft_data = np.fft.rfft(audio_data)
            # Ensure fft_data is changing
            print(fft_data)
            # Call the function to light LEDs
            light_leds(fft_data)
            # Adjust sleep time as needed
            time.sleep(.5)
    except KeyboardInterrupt:
        print("Stopping audio analysis")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PyAudio object
    p.terminate()
 


def get_frequency_magnitude(fft_data, freq_range, sample_rate, chunk_size):
    # Calculate the frequency of each FFT bin
    freq_bin = sample_rate / chunk_size
    start_bin = int(freq_range[0] / freq_bin)
    end_bin = int(freq_range[1] / freq_bin)
    
    # Sum the magnitudes of the FFT data in our frequency range
    magnitude = np.sum(np.abs(fft_data[start_bin:end_bin]))
    
    return magnitude

def normalize_magnitude(magnitude, num_leds, max_magnitude):
    # Scale magnitude to the range of 0 to the number of LEDs
    normalized_magnitude = np.clip((magnitude / max_magnitude), 0, 1)
    scaled_magnitude = int(normalized_magnitude * num_leds)
    
    return scaled_magnitude

def display_band_on_led(strip, led_start, led_end, magnitude):
    # Turn off all LEDs in the strip section
    for i in range(led_start, led_end):
        strip.setPixelColor(i, Color(0, 0, 0))

    # Turn on LEDs up to the calculated magnitude
    for i in range(led_start, led_start + magnitude):
        strip.setPixelColor(i, Color(0, 255, 0))  # Example: Green color

    strip.show()


if __name__ == "__main__":
    main()



