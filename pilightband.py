from rpi_ws281x import PixelStrip, Color
import time
import random

# LED strip configuration:
LED_COUNT = 50        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal
LED_BRIGHTNESS = 64   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)

# Create PixelStrip object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()

# Define functions for animations such as colorWipe, theaterChase, etc.

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def sparkle(strip, color, wait_ms=50, iterations=500):
	"""Sparkle - randomly turn on a pixel."""
	for j in range(iterations):
		pixel = random.randint(0, strip.numPixels()-1)
		strip.setPixelColor(pixel, color)
		strip.show()
		time.sleep(.5)
		strip.setPixelColor(pixel, Color(0,0,0))
		strip.show()

def fire(strip, heat, steps=60):
    """Fire Animation."""
    for i in range(strip.numPixels()):
        t = (i * 255) // strip.numPixels()
        strip.setPixelColor(i, Color(t//heat, t//heat//2, 0))
        strip.show()
        time.sleep(25 / 1000.0)
    for i in reversed(range(strip.numPixels())):
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()
        time.sleep(25 / 1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, Color(0,0,0))

def ukraineFlagAnimation(strip, wait_ms=500, iterations=5):
    """Fades in the Ukraine flag colors yellow and blue."""
    # Define colors:
    yellow = Color(255, 255, 0)  # Yellow color
    blue = Color(0, 0, 255)      # Blue color

    # Calculate the number of pixels for each color (assuming two equal sections for the flag)
    half_n_pixels = strip.numPixels() // 2

    # Perform the animation
    for i in range(iterations):
        # Fade in yellow from the first half of the strip
        fadeColor(strip, yellow, 0, half_n_pixels, wait_ms)
        # Fade in blue from the second half of the strip
        fadeColor(strip, blue, half_n_pixels, strip.numPixels(), wait_ms)
        # Fade out
        fadeColor(strip, Color(0, 0, 0), 0, strip.numPixels(), wait_ms)

# Function to fade in a color
def fadeColor(strip, color, start_pixel, end_pixel, wait_ms):
	for i in range(256):
		for j in range(start_pixel, end_pixel):
			r = (color & 255) * i // 255
			g = (color >> 8 & 255) * i // 255
			b = (color >> 16 & 255) * i // 255
			strip.setPixelColor(j, Color(r, g, b))
		strip.show()
		time.sleep(wait_ms / 100)

# Main program logic follows:
if __name__ == '__main__':
	try:
		while True:
			cmd = input("Enter command (chase, sparkle, fire, wipe, rainbow, ukraine, light, song): ")

			if (cmd == "wipe"):
				# Color wipe animations.
				colorWipe(strip, Color(255, 0, 0))  # Red wipe
				colorWipe(strip, Color(0, 255, 0))  # Green wipe
				colorWipe(strip, Color(0, 0, 255))  # Blue wipe
			elif (cmd == "sparkle"):
				sparkle(strip, Color(255, 0, 255))  # White sparkle
			elif (cmd == "fire"):
				fire(strip, 150)  # Fire animation
			elif (cmd == "chase"): 
				theaterChase(strip, Color(127, 127, 127))  # White theater chase
			elif (cmd == "ukraine"):
				ukraineFlagAnimation(strip)	    
	except KeyboardInterrupt:
		# On a keyboard interrupt, turn off all the pixels.
		colorWipe(strip, Color(0,0,0), 10)
