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

win = Tk()
win.geometry("800x480")
win.title("RFID test")
myFont = tkinter.font.Font(family='Helvetica', size=20, weight="bold")
CardValue = 10

#def showData():
endFont = tkinter.font.Font(family='Helvetica', size=20, weight="bold")
label_card = Label(win, bg='#2C708A', text=CardValue ,font=endFont)
label_card.place(height='60', width='700', relx=0.0, rely=0.65)

def close():
    win.destroy()
    #RPi.GPIO.cleanup()

# Exit button
exitButton = Button(win, text='Exit', font=myFont, command=close, bg='red', height=2, width=6)
exitButton.place(height='40', width='80', relx=0.88, rely=0.9)

#Create a fullscreen window
win.attributes('-fullscreen', True)
win.protocol("WM_DELETE_WINDOW", close) # cleanup GPIO when user closes window
#t1 = threading.Thread(target=rfidreader)
#t1.start()
#t1.join()
win.mainloop()

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

def rfidreader():
    while True:
        sleep(0.2)

r = Reader('/dev/ttyS0')
r.start()

