from tkinter import *
import tkinter.font
from gpiozero import LED
import RPi.GPIO
from time import strftime
from time import sleep
import time
from PIL import ImageTk, Image
import rdm6300
import threading


#t1 = threading.Thread(target=rfidreader)
#t1.start()
#t1.join()


class Reader(rdm6300.BaseReader):
    def card_inserted(self, card):
        #print(f"card inserted {card}")
        print(f"[{card.value}] ID přečtené karty")
        global CardValue
        CardValue = card.value

    def card_removed(self, card):
        print(f"card removed {card}")

    def invalid_card(self, card):
        print(f"invalid card {card}")

    def card_data(self):
        self.cardData=CardValue
        print(f"card data {CardValue}")

r = Reader('/dev/ttyS0')
r.start()

