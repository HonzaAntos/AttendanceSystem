## Toggle an LED when the GUI button is pressed ##

from tkinter import *
import tkinter.font
import customtkinter
from gpiozero import LED
import RPi.GPIO
from time import strftime
from time import sleep
import time
from PIL import ImageTk, Image
import rdm6300
import threading
import sqlite3

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

CardValue = 0
CardValueBool = False
class Reader(rdm6300.BaseReader):
    def card_inserted(self, card):
        #print(f"card inserted {card}")
        #label_down.config(text=card)
        print(f"[{card.value}] ID přečtené karty")
        global CardValue
        CardValue = card.value
        #label_down.config(text="Stiskněte tlačítko!")
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
root=customtkinter.CTk()
root.geometry("800x480")
root.title("Attendace System")

myFont = tkinter.font.Font(family = 'Helvetica', size = 20, weight = "bold")

###############

## Setting background
background_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/neon_background.jpg").resize((800,400), Image.ANTIALIAS))
logo = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/logo.png").resize((210,60), Image.ANTIALIAS))


# Create a Label Widget to display the text or Image
#background_label = customtkinter.CTkLabel(master=root, fg_color=("black","gray75"))
#background_label.place(x=0,y=0, relwidth=1, relheight=1)

# Create background label for top part
label_top = customtkinter.CTkLabel(master=root, bg_color='#2D708A')
label_top.place(height='60', width='800')

# Create a Label Widget to display the text or Image
label_logo = customtkinter.CTkLabel(master=root, image = logo)
label_logo.place(height='60', width='210', x='2', y='2')

#create frame to hide background of the icons
frame1=customtkinter.CTkFrame(master=root, corner_radius=25)
frame1.place(height='140', width='180', x=210, rely=0.18)
frame2=customtkinter.CTkFrame(master=root, corner_radius=25)
frame2.place(height='140', width='180', x=10, rely=0.18)
frame3=customtkinter.CTkFrame(master=root, corner_radius=25)
frame3.place(height='140', width='180', x=410, rely=0.18)
frame4=customtkinter.CTkFrame(master=root, corner_radius=25)
frame4.place(height='140', width='180', x=610, rely=0.18)
"""
## ICONS ##
#icon private session - coffee
coffee_image = (Image.open("/home/pi/Downloads/coffee.png"))  ## Add image to rasp!!!!
resized_coffee_image = coffee_image.resize((100,60), Image.ANTIALIAS)
new_image_coffee = ImageTk.PhotoImage(resized_coffee_image)
coffee_label=Label(root, image = new_image_coffee)
coffee_label.place(height='120', width='180', relx=0.02, rely=0.2)

#icon arrive
open_image = (Image.open("/home/pi/Downloads/in.png"))
resized_open_image = open_image.resize((100,60), Image.ANTIALIAS)
new_image_open = ImageTk.PhotoImage(resized_open_image)
open_label=Label(root, image = new_image_open)
open_label.place(height='120', width='180', relx=0.26, rely=0.2)

#icon leave
leave_image = (Image.open("/home/pi/Downloads/out.png"))
resized_leave_image = leave_image.resize((100,60), Image.ANTIALIAS)
new_image_leave = ImageTk.PhotoImage(resized_leave_image)
leave_label=Label(root, image = new_image_leave)
leave_label.place(height='120', width='180', relx=0.5, rely=0.2)

#icon doctor
doctor_image = (Image.open("/home/pi/Downloads/doctor.png"))  ## Add image to rasp!!!!
resized_doctor_image = doctor_image.resize((100,60), Image.ANTIALIAS)
new_image_doctor = ImageTk.PhotoImage(resized_doctor_image)
doctor_label=Label(root, image = new_image_doctor)
doctor_label.place(height='120', width='180', relx=0.74, rely=0.2)
"""

def popup():
    if CardValue != 0:
        print(f"prijata data z karty jsou {CardValue}")
        global pop
        global pop_frame
        global img_arrow
        pop = Toplevel()
        pop.geometry("800x420+0+60")
        pop.overrideredirect(True)
        print("_______")
        print(bg.get())
        print("_______")
        endFont = tkinter.font.Font(family='Helvetica', size=24, weight="bold")


        pop_frame = customtkinter.CTkFrame(master=pop, width=800, height=420)
        pop_frame.place(x=0,y=0)
        label_act = customtkinter.CTkLabel(master=pop, bg_color='#2C708A', fg_color="gray15", corner_radius=10, textvariable=var,text_font=('Helvetica',30,"bold"))
        label_act.place(height='80', width='300', relx=0.3, rely=0.15)
        label_user = customtkinter.CTkLabel(master=pop, bg_color='#2C708A', fg_color="gray15" , corner_radius=10, text='Jan Novák',text_font=('Helvetica',30,"bold"))
        label_user.place(height='80', width='300', relx=0.3, rely=0.4)
        label_card = customtkinter.CTkLabel(master=pop, bg_color='#2C708A', fg_color="gray15", corner_radius=10, text=CardValue,text_font=('Helvetica',30,"bold"))
        label_card.place(height='80', width='300', relx=0.3, rely=0.65)

        if bg.get() == "blue":
            pop_frame.configure(fg_color="blue")
            print("bg is blue ------")
        if bg.get() == "red":
            pop_frame.configure(fg_color="red")
            print("bg is red ------")
        if bg.get() == "green":
            pop_frame.configure(fg_color="green")
            print("bg is green ------")
        if bg.get() == "brown":
            pop_frame.configure(fg_color="brown")
            print("bg is brown ------")
        card_info.set("Stiskněte tlačítko!")
        print("popup start")
        pop.after(3000, popDestroy)

    else:
        print("error: no card inserted!!!!!!!!")


### Event Functions ###
def ledToggle():
    led.on()
    RPi.GPIO.output(buzz, RPi.GPIO.HIGH)
    sleep(0.3)
    led.off()
    RPi.GPIO.output(buzz, RPi.GPIO.LOW)

def arrivalToggle():
    var.set("Příchod")
    global type
    type=1
    bg.set("green")
    popup()

def leaveToggle():
    var.set("Odchod")
    type=2
    bg.set("red")
    popup()

def doctorToggle():
    var.set("Lékař")
    type=3
    bg.set("blue")
    popup()

def coffeeToggle():
    var.set("Soukromě")
    type=4
    bg.set("brown")
    popup()

def send_to_db():
    global CardValue
    CardValue = 0
    print("data initialized to zero")
    print(f"data: {var}")
    # sending accuirated data to db

def popDestroy():
    send_to_db()
    pop.destroy()
    print("popup destroyed")


def close():
    RPi.GPIO.cleanup()
    pop.destroy()
    root.destroy()

coffee_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/coffee.png").resize((100,60), Image.ANTIALIAS))
open_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((100,60), Image.ANTIALIAS))
leave_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/out.png").resize((100,60), Image.ANTIALIAS))
doctor_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/doctor.png").resize((100,60), Image.ANTIALIAS))

button_in = customtkinter.CTkButton(master=root, command=arrivalToggle, image=open_image, text="Příchod", width=160, height=120, corner_radius=25,border_width=3,text_font=('Helvetica',17),bg_color="gray16", compound="top")
button_in.place(height='120', width='160', x=220, rely=0.2)
#button_in.grid(row=0,column=0,padx=20)
button_out = customtkinter.CTkButton(master=root, command=leaveToggle, image=leave_image, text="Odchod", width=160, height=120, corner_radius=25,border_width=3,text_font=('Helvetica',17),bg_color="gray16", compound="top")
button_out.place(height='120', width='160', x=420, rely=0.2)
#button_out.grid(row=0,column=1, padx=20)
button_doctor = customtkinter.CTkButton(master=root, command=doctorToggle,  image=doctor_image, text="Lékař", width=160, height=120, corner_radius=25,border_width=3,text_font=('Helvetica',17),bg_color="gray16", compound="top")
button_doctor.place(height='120', width='160', x=620, rely=0.2)
#button_doctor.grid(row=0,column=2, padx=20)
button_coffee = customtkinter.CTkButton(master=root, command=coffeeToggle ,image=coffee_image, text="Soukromě", width=160, height=120, corner_radius=25,border_width=3,text_font=('Helvetica',17),bg_color="gray16", compound="top")
button_coffee.place(height='120', width='160', x=20, rely=0.2)
#button_coffee.grid(row=0,column=3, padx=20)

bg = StringVar()
bg.set("yellow")
var = StringVar()
type = 0
cardData = StringVar()
cardData.set(rdm6300.CardData.value)


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
time_label = Label(root, font=my_font, bg='#2D708A')
time_label.place(height='55', width='220',relx=0.72, rely=0.01)
my_time()

middleFont = tkinter.font.Font(family = 'Helvetica', size = 28, weight = "bold")

def update():
    label_down.config(text=CardValue)
    card_info.set("Stiskněte tlačítko!")

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

card_info = StringVar()


## Active label down for inform user about state
label_down = customtkinter.CTkLabel(master=root, bg_color='#2D708A', text="Přiložte kartu a stiskněte tlačítko!", text_font=('Helvetica',20,"bold"))
label_down.place(height='80', width='800',relx=0.0, rely=0.85)

label_middleTop= Label(root, bg='#2D708A', textvariable=var, font=middleFont, fg='red')
label_middleTop.place(height='55', width='200',relx=0.35, rely=0.005)

button_exit = customtkinter.CTkButton(master=root, command=close,text_color="red", text="x", width=20, height=20, corner_radius=10,border_width=3,text_font=('Helvetica',20))
button_exit.place(height='40', width='40', relx=0.88, rely=0.9)

#submit = Button(win, text='submit', font=myFont, command=submit, bg='red', height=2, width=6)
#submit.place(height='40', width='80', relx=0.58, rely=0.9)


#Create a fullscreen window
root.attributes('-fullscreen', True)
root.protocol("WM_DELETE_WINDOW", close) # cleanup GPIO when user closes window

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