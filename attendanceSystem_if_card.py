## Toggle an LED when the GUI button is pressed ##
#todo code review - create a classes for every function
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
import sqlite3

CardValue = 0
CardValueBool = False
class Reader(rdm6300.BaseReader):
    def card_inserted(self, card):
        #print(f"card inserted {card}")
        #label_down.config(text=card)
        print(f"[{card.value}] ID přečtené karty")
        global CardValue
        CardValue = card.value
        ledToggle()

    def card_removed(self, card):
        print(f"card removed {card}")

    def invalid_card(self, card):
        print(f"invalid card {card}")


RPi.GPIO.setmode(RPi.GPIO.BCM)
coverFrame = None
### HARDWARE DEFINITIONS ###
led=LED(14)
#Set buzzer - pin 27 as output
buzz=27
RPi.GPIO.setup(buzz,RPi.GPIO.OUT)
win = Tk()
win.geometry("800x480")
win.title("Attendace System")

bg = StringVar()
bg.set("yellow")
var = StringVar()
type = 0
cardData = StringVar()
cardData.set(rdm6300.CardData.value)
myFont = tkinter.font.Font(family = 'Helvetica', size = 20, weight = "bold")

## Setting background
background_image=(Image.open("/home/pi/Downloads/neon_background.jpg"))
# Resize image
resized_background_image = background_image.resize((800,400), Image.ANTIALIAS)
new_background_image = ImageTk.PhotoImage(resized_background_image)
# Create a Label Widget to display the text or Image
background_label = Label(win, image = new_background_image)
background_label.place(x=0,y=0, relwidth=1, relheight=1)
# Create background label for top part
label_top = Label(win, bg='#2D708A')
label_top.place(height='60', width='800')

### Add image ###
# Create an object of tkinter ImageTk
img = (Image.open("/home/pi/Downloads/logo.png"))
# Resize image
resized_image = img.resize((210,60), Image.ANTIALIAS)
new_image = ImageTk.PhotoImage(resized_image)
# Create a Label Widget to display the text or Image
label = Label(win, image = new_image)
label.place(height='60', width='210', x='2', y='2')


## ICONS ##
#icon arrive
open_image = (Image.open("/home/pi/Downloads/in.png"))
resized_open_image = open_image.resize((100,60), Image.ANTIALIAS)
new_image_open = ImageTk.PhotoImage(resized_open_image)
open_label=Label(win, image = new_image_open)
open_label.place(height='120', width='180', relx=0.26, rely=0.2)

#icon leave
leave_image = (Image.open("/home/pi/Downloads/out.png"))
resized_leave_image = leave_image.resize((100,60), Image.ANTIALIAS)
new_image_leave = ImageTk.PhotoImage(resized_leave_image)
leave_label=Label(win, image = new_image_leave)
leave_label.place(height='120', width='180', relx=0.5, rely=0.2)

#icon doctor
doctor_image = (Image.open("/home/pi/Downloads/doctor.png"))  ## Add image to rasp!!!!
resized_doctor_image = doctor_image.resize((100,60), Image.ANTIALIAS)
new_image_doctor = ImageTk.PhotoImage(resized_doctor_image)
doctor_label=Label(win, image = new_image_doctor)
doctor_label.place(height='120', width='180', relx=0.74, rely=0.2)

#icon private session - coffee
coffee_image = (Image.open("/home/pi/Downloads/coffee.png"))  ## Add image to rasp!!!!
resized_coffee_image = coffee_image.resize((100,60), Image.ANTIALIAS)
new_image_coffee = ImageTk.PhotoImage(resized_coffee_image)
coffee_label=Label(win, image = new_image_coffee)
coffee_label.place(height='120', width='180', relx=0.02, rely=0.2)

### REAL TIME ###
def my_time():
    time_string = strftime('%H:%M:%S')  # time format
    #date_string = strftime('%x')  # date format
    #date_label.config(text=date_string)
    time_label.config(text=time_string)
    time_label.after(1000, my_time)  # time delay of 1000 milliseconds
    #date_label.after(1000, my_time)  # time delay of 1000 milliseconds
my_font = ('Helvetica', 30, 'bold')  # display size and style
#myDate = ('Helvetica', 20, 'bold')  # display size and style
#date_label=Label(win, font=myDate,bg='#2D708A')
#date_label.place(height='55', width='220',relx=0.72, rely=0.05)
time_label = Label(win, font=my_font, bg='#2D708A')
time_label.place(height='55', width='220',relx=0.72, rely=0.01)
my_time()

### Event Functions ###
def ledToggle():
    led.on()
    RPi.GPIO.output(buzz, RPi.GPIO.HIGH)
    sleep(0.3)
    led.off()
    RPi.GPIO.output(buzz, RPi.GPIO.LOW)
   ###
   # if led.is_lit:
   #     RPi.GPIO.output(buzz, RPi.GPIO.LOW)
   #     led.off()
   #     ledButton["text"]="LED on" # Change only the button text property
   # else:
    #     led.on()
    #    ledButton["text"] = "LED off"
    #    RPi.GPIO.output(buzz, RPi.GPIO.HIGH)

# function to blink red or green when arrival or leave
def blinkByState(val: bool):
    if val:
        RPi.GPIO.output(27, RPi.GPIO.HIGH) #blink red
        sleep(0.3)
        RPi.GPIO.output(27, RPi.GPIO.LOW)
    else:
        RPi.GPIO.output(28, RPi.GPIO.HIGH) #blink green
        sleep(0.3)
        RPi.GPIO.output(28, RPi.GPIO.LOW)

def arrivalToggle():
    var.set("Příchod")
    global type
    type=1
    bg.set("green")
    blinkByState(False)
    popup()
   # pop.config(bg='green')
    #label_middleTop["text"]="Příchod"

def leaveToggle():
    var.set("Odchod")
    type=2
    bg.set("red")
    #pop.config(bg='red')
    #label_middleTop["text"]="Odchod"
    blinkByState(True)
    popup()

def doctorToggle():
    var.set("Lékař")
    type=3
    bg.set("blue")
    popup()
    #pop.config(bg='blue')
    #label_middleTop["text"]="Lékař"

def popup():
    if CardValue:
            global pop
            global img_arrow
            pop =Toplevel()
            pop.geometry("800x420+0+60")
            print(bg.get())
            #pop['bg']=bg.get
            if bg=="blue":
                pop.configure(bg="blue")
                print("bg is blue ------")
            if bg=="red":
                pop.configure(bg="red")
                print("bg is red ------")
            if bg=="green":
                pop.configure(bg="green")
                print("bg is green ------")
            endFont = tkinter.font.Font(family='Helvetica', size=24, weight="bold")

            canvas = Canvas(pop,width=800, height=420)
            canvas.pack()



            #i = [1,2,3,4,5,6,7,8,9,10]
            #for num in i:
            #    print(num)
            #    offset = 20*num
            #    arrow_pic.place(height='400', width='100', x=offset, y='0')

            #img_arrow = (Image.open("/home/pi/Downloads/green_arrow_crop.png"))
            # Resize image
            #resized_image_arrow = arrow.resize((100, 300), Image.ANTIALIAS)
            #new_image_arrow = ImageTk.PhotoImage(resized_image_arrow)
            # Create a Label Widget to display the text or Image
            #label_a rrow = Label(pop, image=new_image_arrow)
            #label_arrow.place(height='300', width='100', x='150', y='150')


            label_act = Label(pop, bg='#2C708A', textvariable=var, font=endFont)
            label_act.place(height='80', width='300',relx=0.3, rely=0.15)
            ##todo get method from API
            #animation arrow
            label_user = Label(pop, bg='#2C708A', text='Jan Novák', font=endFont)
            label_user.place(height='80', width='300',relx=0.3, rely=0.4)
            label_card = Label(pop, bg='#2C708A', text=CardValue, font=endFont)
            label_card.place(height='80', width='300',relx=0.3, rely=0.65)

            #pop.attributes('-fullscreen', True)
            #pop.protocol("WM_DELETE_WINDOW", close)  # cleanup GPIO when user closes window
            print("popup start")
            #reset caedvalue to zero!!!!
            CardValue=0
            pop.after(3000, popDestroy)

def popDestroy():
    pop.destroy()
    print("popup destroyed")


def close():
    RPi.GPIO.cleanup()
    pop.destroy()
    win.destroy()

middleFont = tkinter.font.Font(family = 'Helvetica', size = 28, weight = "bold")

def update():
    label_down.config(text=CardValue)

## Submit data to the database
def submit():
    # connection to the db
    conn = sqlite3.connect('workersID.db')
    # create a cursor
    c = conn.cursor()
    print("ADDING VALUES TO DB")
    print(id)
    print(type)
    print(var)
    print("_______________")
    # Insert in to table
    c.execute("INSERT INTO addresses VALUES (:id, :type, :var)",
              {
                  'id': id,
                  'type': type,
                  'var': var.get()
              })
    # Commit changes
    conn.commit()
    conn.close()

## Active label down for inform user about state
label_down = Label(win, bg='#2D708A', text="Přiložte kartu a stiskněte tlačítko!", font=myFont)
label_down.place(height='80', width='800',relx=0.0, rely=0.85)

label_middleTop= Label(win, bg='#2D708A', textvariable=var, font=middleFont, fg='white')
label_middleTop.place(height='55', width='160',relx=0.4, rely=0.005)

### WIDGETS ###

# Button, triggers the connected command when it is pressed
ledButton = Button(win, text='Soukromě', font=myFont, command=ledToggle, fg='white', bg='#8f244b', height=5, width=24)
ledButton.place(height='120', width='180', relx=0.02, rely=0.2)

# Arrival button
arrivalButton = Button(win, image=new_image_open, font=myFont,    command =arrivalToggle,fg='white', bg='#8f244b', height=5, width=24)
arrivalButton.place(height='120', width='180', relx=0.26, rely=0.2)

# Leave button
leaveButton = Button(win, image=new_image_leave, font=myFont, command=leaveToggle, fg='white',bg='#14155c', height=5, width=24)
leaveButton.place(height='120', width='180', relx=0.5, rely=0.2)

# Doctor button
doctorButton = Button(win, text='Lékař', font=myFont, command=doctorToggle, fg='white',bg='#14155c', height=5, width=24)
doctorButton.place(height='120', width='180', relx=0.74, rely=0.2)

# Help button - ack for simulation rfid
#helpButton = Button(win, text='Potvrzení-tmp', font=myFont, command=popup, fg='white',bg='#333333', height=5, width=24)
#helpButton.place(height='120', width='220', relx=0.35, rely=0.5)

# Exit button
exitButton = Button(win, text='Exit', font=myFont, command=close, bg='red', height=2, width=6)
exitButton.place(height='40', width='80', relx=0.88, rely=0.9)

#submit = Button(win, text='submit', font=myFont, command=submit, bg='red', height=2, width=6)
#submit.place(height='40', width='80', relx=0.58, rely=0.9)


#Create a fullscreen window
win.attributes('-fullscreen', True)
win.protocol("WM_DELETE_WINDOW", close) # cleanup GPIO when user closes window

def rfidreader():
    r = Reader('/dev/ttyS0')
    r.start()


def gui():
    while True:
        sleep(0.1)

## CREATE DATABASE
#id = CardValue

# Create a table
# connection to the db
#conn = sqlite3.connect('workersID.db')
# create a cursor
#c = conn.cursor()
#c. execute("""CREATE TABLE addresses (
#        id integer,
#        type integer,
#        var text
#         )""")

t1 = threading.Thread(target=rfidreader)
#t2 = threading.Thread(target=gui)
t1.setDaemon(True)
t1.start()
#t2.start()
# t2.join(timeout=5)
#app.run(debug=True)