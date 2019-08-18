import os
import slack
import requests
import neopixel
import board

import os
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import time
from papirus import Papirus

import RPi.GPIO as GPIO

# Check EPD_SIZE is defined
EPD_SIZE=2.0

WHITE = 1
BLACK = 0

CLOCK_FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
DATE_FONT_FILE  = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'

pixels = neopixel.NeoPixel(board.D18, 32, brightness=0.1)

SW1 = 21
SW2 = 16
SW3 = 20
SW4 = 19
SW5 = 26


def main(argv):

    """main program - draw and display time and date"""

    setup_gpio()

    papirus = Papirus(rotation = int(argv[0]) if len(sys.argv) > 1 else 0)

    # print('panel = {p:s} {w:d} x {h:d}  version={v:s} COG={g:d} FILM={f:d}'.format(p=papirus.panel, w=papirus.width, h=papirus.height, v=papirus.version, g=papirus.cog, f=papirus.film))

    papirus.clear()

    while True:
        if GPIO.input(SW1) == False:
            timer(papirus, 10)
        if GPIO.input(SW2) == False:
            timer(papirus, 64)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SW1, GPIO.IN)
    GPIO.setup(SW2, GPIO.IN)
    GPIO.setup(SW3, GPIO.IN)
    GPIO.setup(SW4, GPIO.IN)
    GPIO.setup(SW5, GPIO.IN)


def timer(papirus, seconds):
    """ start timer of x minutes """
    image = Image.new('1', papirus.size, WHITE)

    draw = ImageDraw.Draw(image)
    width, height = image.size

    timer_font_size = int((width - 4)/(5*0.65))
    timer_font = ImageFont.truetype(CLOCK_FONT_FILE, timer_font_size)

    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)
    previous_remaining = 0

    start = time.time()
    remaining = seconds # seconds

    light_on((100,100,0))
    while remaining > 0:
        while remaining > 0:
            now = time.time()
            remaining = seconds - (now - start)
            if int(remaining) == previous_remaining:
                break
            if remaining < 0:
                break
            time.sleep(0.1)

            draw.rectangle((5, 10, width - 5, 10 + timer_font_size), fill=WHITE, outline=WHITE)
            draw.text((5, 10), '{m:02d}:{s:02d}'.format(m=int(remaining // 60), s=int(remaining % 60)), fill=BLACK, font=timer_font)

            # display image on the panel
            papirus.display(image)
            if int(remaining % 60) == 0:
                papirus.update()    # full update every minute
            else:
                papirus.partial_update()
            previous_remaining = int(remaining)
    light_off()
    papirus.clear()



class SlackDND:
	client = slack.WebClient(token= os.environ['SLACK_API_TOKEN'])
			
	def start(self, time):
		try:
			response = self.client.dnd_setSnooze(num_minutes=time)
			self.set_status("trabajando",":male-technologist::skin-tone-3:")
			return response["ok"]
		except:
			return False
			
	def stop(self):
		try:
			response = self.client.dnd_endSnooze()
			self.set_status("","")
			return response["ok"]
		except:
			return False
		
	def set_status(self,status, emoji):
		try:
			response = self.client.users_profile_set(profile= {"status_text":status, "status_emoji": emoji })
			return response["ok"]
		except:
			return False



class RescueTimeDND:
	key = os.environ['RESCUETIME_API_KEY']
	
	def start(self, time):
		try:
			payload = {"key": self.key, "duration": time}
			r = requests.post("https://www.rescuetime.com/anapi/start_focustime",data= payload )
			return r.status_code == 200
		except:
			return False
			
	def stop(self):
		payload = {"key": self.key}
		try:
			r = requests.post("https://www.rescuetime.com/anapi/end_focustime",data= payload )
			return r.status_code == 200		
		except:
			return False


class LightDND:
	GREEN = (0,255,0)
	BLACK = (0,0,0)
	pixels = neopixel.NeoPixel(board.D18, 32)
	def start(self, time):
		try:
			self.pixels.fill(self.GREEN)
			return True
		except:
			return False
	def stop(self):
		try:
			pixels.fill(self.BLACK)
			return True
		except:
			return False

def light_on(color=(0,255,0)):
	pixels.fill(color)

def light_off():
	pixels.fill((0,0,0))



sl = SlackDND()
rt = RescueTimeDND()
l = LightDND()

services = [l]

main([])

# sl.set_status("","")
# https://github.com/sindresorhus/do-not-disturb

