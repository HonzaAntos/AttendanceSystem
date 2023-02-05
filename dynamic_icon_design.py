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

# Setting theme dark/light
customtkinter.set_appearance_mode("dark")
# customizable theme via json file
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

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
logo = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/logo.png").resize((210,60), Image.ANTIALIAS))

# Create background label for top part
label_top = customtkinter.CTkLabel(master=root,bg_color=("gray90","gray16"))
label_top.place(height='70', width='800')

label_top_line = customtkinter.CTkLabel(master=root,bg_color="#34b7eb", text="")
label_top_line.place(x='0', y='70',height='3', width='800')

label_down_line = customtkinter.CTkLabel(master=root,bg_color="#34b7eb",text="")
label_down_line.place(x='0', y='430',height='3', width='800')
# Create a Label Widget to display the text or Image
label_logo = customtkinter.CTkLabel(master=root, image = logo, bg_color=("gray90","gray16"))
label_logo.place(height='60', width='210', x='5', y='5')



def popup():
    if CardValue != 0:
        print(f"prijata data z karty jsou {CardValue}")
        global pop
        global pop_frame
        global img_arrow
        pop = Toplevel()
        pop.geometry("800x420+0+70")
        pop.overrideredirect(True)
        print("_______")
        print(bg.get())
        print("_______")

        coffee_image_pop = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/coffee.png").resize((200, 200), Image.ANTIALIAS))
        open_image_pop = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((200, 200), Image.ANTIALIAS))
        leave_image_pop = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/out.png").resize((200, 200), Image.ANTIALIAS))
        doctor_image_pop = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/doctor.png").resize((200, 200), Image.ANTIALIAS))

        pop_frame = customtkinter.CTkFrame(master=pop, width=800, height=420)
        pop_frame.place(x=0,y=0)
        label_act = customtkinter.CTkLabel(master=pop,bg_color=("gray90","gray16"), corner_radius=10, textvariable=var,text_font=('Helvetica',30,"bold"))
        label_act.place(height='80', width='300', relx=0.3, rely=0.15)
        label_user = customtkinter.CTkLabel(master=pop,bg_color=("gray90","gray16") , corner_radius=10, text='Jan Novák',text_font=('Helvetica',30,"bold"))
        label_user.place(height='80', width='300', relx=0.3, rely=0.4)
        label_card = customtkinter.CTkLabel(master=pop,bg_color=("gray90","gray16"), corner_radius=10, text=CardValue,text_font=('Helvetica',30,"bold"))
        label_card.place(height='80', width='300', relx=0.3, rely=0.65)
        label_icon = customtkinter.CTkButton(master=pop, width = 200, height = 200, text="", fg_color="black", border_width=0)
        label_icon.place(x=10, y=120)

        if bg.get() == "blue":
            pop_frame.configure(fg_color="#427bf5")
            label_icon.configure(fg_color="#427bf5")
            label_icon.configure(image=doctor_image_pop)
            print("bg is blue ------")
        if bg.get() == "red":
            pop_frame.configure(fg_color="#ff5252")
            label_icon.configure(fg_color="#ff5252")
            label_icon.configure(image=leave_image_pop)
            print("bg is red ------")
        if bg.get() == "green":
            pop_frame.configure(fg_color="#0dff96")
            label_icon.configure(fg_color="#0dff96")
            label_icon.configure(image=open_image_pop)
            print("bg is green ------")
        if bg.get() == "brown":
            pop_frame.configure(fg_color="#f5aa42")
            label_icon.configure(fg_color="#f5aa42")
            label_icon.configure(image=coffee_image_pop)
            print("bg is brown ------")
        card_info.set("Stiskněte tlačítko!")
        print("popup start")
        pop.after(5000, popDestroy)

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
    second_window.destroy()

def second_close():
    second_window.destroy()

def new_popup():
    print("new popup running....")
    global second_window
    second_window = Toplevel()
    second_window.geometry("800x480")
    second_window.overrideredirect(True)

    ###############
    pop_frame = customtkinter.CTkFrame(master=second_window, width=800, height=420)
    pop_frame.place(x=0, y=0)
    # shadows under buttons
    # create frame to hide background of the icons
    frame1_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame1_second.place(height='140', width='180', x=210, rely=0.18)
    frame2_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame2_second.place(height='140', width='180', x=10, rely=0.18)
    frame3_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame3_second.place(height='140', width='180', x=410, rely=0.18)
    frame4_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame4_second.place(height='140', width='180', x=610, rely=0.18)
    # frames for second row
    frame5_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame5_second.place(height='140', width='180', x=210, rely=0.52)
    frame6_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame6_second.place(height='140', width='180', x=10, rely=0.52)
    frame7_second = customtkinter.CTkFrame(master=second_window, corner_radius=25)
    frame7_second.place(height='140', width='180', x=410, rely=0.52)
    frame8_second = customtkinter.CTkFrame(master=second_window , corner_radius=25)
    frame8_second.place(height='140', width='180', x=610, rely=0.52)

    ## Setting background
    logo_second = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/logo.png").resize((210, 60), Image.ANTIALIAS))

    # Create background label for top part
    label_top_second = customtkinter.CTkLabel(master=second_window, bg_color=("gray90", "gray16"))
    label_top_second.place(height='70', width='800')
    label_top_line_second = customtkinter.CTkLabel(master=second_window, bg_color="#34b7eb", text="")
    label_top_line_second.place(x='0', y='70', height='3', width='800')
    label_down_line_second = customtkinter.CTkLabel(master=second_window, bg_color="#34b7eb", text="")
    label_down_line_second.place(x='0', y='430', height='3', width='800')
    # Create a Label Widget to display the text or Image
    label_logo_second = customtkinter.CTkLabel(master=second_window, image=logo_second, bg_color=("gray90", "gray16"))
    label_logo_second.place(height='60', width='210', x='5', y='5')


    button_doctor_second = customtkinter.CTkButton(master=second_window, command=doctorToggle,hover_color="#2d56ad",border_color="#0f0f0f",fg_color="#427bf5",image=doctor_image, text="Lékař", text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_doctor_second.place(height='120', width='160', x=620, rely=0.2)
    button_coffee_second = customtkinter.CTkButton(master=second_window, command=coffeeToggle,hover_color="#b37c30", border_color="#0f0f0f",fg_color="#f5aa42", image=coffee_image, text="Soukromě",text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_coffee_second.place(height='120', width='160', x=20, rely=0.2)

    # down labels
    ## Active label down for inform user about state
    label_down_second = customtkinter.CTkLabel(master=second_window, bg_color=("gray90", "gray16"),text="Přiložte kartu a stiskněte tlačítko!", text_color="black",text_font=('Helvetica', 20, "bold"))
    label_down_second.place(height='60', width='800', relx=0.0, rely=0.9)

    label_middleTop_second = customtkinter.CTkLabel(master=second_window, bg_color=("gray90", "gray16"), textvariable=var,text_font=('Helvetica', 30, "bold"))
    label_middleTop_second.place(height='55', width='200', relx=0.35, rely=0.005)

    second_window.after(5000, second_close())

coffee_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/coffee.png").resize((60,60), Image.ANTIALIAS))
open_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((60,60), Image.ANTIALIAS))
leave_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/out.png").resize((60,60), Image.ANTIALIAS))
doctor_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/doctor.png").resize((60,60), Image.ANTIALIAS))
#dovolena
#nahradni volno
#nemoc
#sluzebne

mode_select = StringVar()
# options bigAL, six, three,
mode_select.set("bigAL")

if mode_select.get() == "six":
    # create frame to hide background of the icons
    frame1 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame1.place(height='140', width='180', x=210, rely=0.18)
    frame2 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame2.place(height='140', width='180', x=10, rely=0.18)
    frame3 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame3.place(height='140', width='180', x=410, rely=0.18)
    frame4 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame4.place(height='140', width='180', x=610, rely=0.18)
    # frames for second row
    frame5 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame5.place(height='140', width='180', x=210, rely=0.52)
    frame6 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame6.place(height='140', width='180', x=10, rely=0.52)
    frame7 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame7.place(height='140', width='180', x=410, rely=0.52)
    frame8 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame8.place(height='140', width='180', x=610, rely=0.52)

    button_in = customtkinter.CTkButton(master=root, command=arrivalToggle,hover_color="#09bd6f",border_color="#0f0f0f", fg_color="#0dff96", image=open_image, text="Příchod", text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_in.place(height='120', width='160', x=220, rely=0.2)
    button_out = customtkinter.CTkButton(master=root, command=leaveToggle, hover_color="#bf3d3d", border_color="#0f0f0f",fg_color="#ff5252", image=leave_image, text="Odchod", text_color="black",width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_out.place(height='120', width='160', x=420, rely=0.2)
    button_doctor = customtkinter.CTkButton(master=root, command=doctorToggle,hover_color="#2d56ad",border_color="#0f0f0f",fg_color="#427bf5",image=doctor_image, text="Lékař", text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_doctor.place(height='120', width='160', x=620, rely=0.2)
    button_coffee = customtkinter.CTkButton(master=root, command=coffeeToggle,hover_color="#b37c30", border_color="#0f0f0f",fg_color="#f5aa42", image=coffee_image, text="Soukromě",text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_coffee.place(height='120', width='160', x=20, rely=0.2)
    print(mode_select.get())

if mode_select.get() == "bigAL":
    open_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((160, 160), Image.ANTIALIAS))
    leave_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/out.png").resize((160, 160), Image.ANTIALIAS))
    frame1 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame1.place(height='260', width='340', x=430, rely=0.18)
    frame2 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame2.place(height='260', width='340', x=30, rely=0.18)
    frame3 = customtkinter.CTkFrame(master=root, corner_radius=25)
    frame3.place(height='60', width='740', x=30, rely=0.75)

    button_in = customtkinter.CTkButton(master=root, command=arrivalToggle,hover_color="#09bd6f",border_color="#0f0f0f", fg_color="#0dff96", image=open_image, text="Příchod", text_color="black", width=320, height=240, corner_radius=25,border_width=4,text_font=('Helvetica',25,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_in.place(height='240', width='320', x=40, rely=0.2)
    button_out = customtkinter.CTkButton(master=root, command=leaveToggle, hover_color="#bf3d3d", border_color="#0f0f0f",fg_color="#ff5252", image=leave_image, text="Odchod", text_color="black",width=320, height=240, corner_radius=25,border_width=4,text_font=('Helvetica',25,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_out.place(height='240', width='320', x=440, rely=0.2)
    #button_doctor = customtkinter.CTkButton(master=root, command=doctorToggle,hover_color="#2d56ad",border_color="#0f0f0f",fg_color="#427bf5",image=doctor_image, text="Lékař", text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    #button_doctor.place(height='120', width='160', x=620, rely=0.2)
    #button_coffee = customtkinter.CTkButton(master=root, command=coffeeToggle,hover_color="#b37c30", border_color="#0f0f0f",fg_color="#f5aa42", image=coffee_image, text="Soukromě",text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    #button_coffee.place(height='120', width='160', x=20, rely=0.2)
    button_other = customtkinter.CTkButton(master=root, command=new_popup,hover_color="#09bd6f",border_color="#0f0f0f", fg_color="#dede50", text="Další možnosti", text_color="black", width=720, height=40, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_other.place(x=40, rely=0.77)
    print(mode_select.get())

if mode_select.get() == "three":
    button_in = customtkinter.CTkButton(master=root, command=arrivalToggle,hover_color="#09bd6f",border_color="#0f0f0f", fg_color="#0dff96", image=open_image, text="Příchod", text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_in.place(height='120', width='160', x=220, rely=0.2)
    button_out = customtkinter.CTkButton(master=root, command=leaveToggle, hover_color="#bf3d3d", border_color="#0f0f0f",fg_color="#ff5252", image=leave_image, text="Odchod", text_color="black",width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_out.place(height='120', width='160', x=420, rely=0.2)
    button_doctor = customtkinter.CTkButton(master=root, command=doctorToggle,hover_color="#2d56ad",border_color="#0f0f0f",fg_color="#427bf5",image=doctor_image, text="Lékař", text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_doctor.place(height='120', width='160', x=620, rely=0.2)
    button_coffee = customtkinter.CTkButton(master=root, command=coffeeToggle,hover_color="#b37c30", border_color="#0f0f0f",fg_color="#f5aa42", image=coffee_image, text="Soukromě",text_color="black", width=160, height=120, corner_radius=25,border_width=4,text_font=('Helvetica',17,'bold'),bg_color=("gray90","gray16"), compound="bottom")
    button_coffee.place(height='120', width='160', x=20, rely=0.2)
    print(mode_select.get())

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
    time_label.configure(text=time_string)
    time_label.after(1000, my_time)  # time delay of 1000 milliseconds
    #date_label.after(1000, my_time)  # time delay of 1000 milliseconds
my_font = ('Helvetica', 30, 'bold')  # display size and style
#myDate = ('Helvetica', 20, 'bold')  # display size and style
#date_label=Label(win, font=myDate,bg='#2D708A')
#date_label.place(height='55', width='220',relx=0.72, rely=0.05)
time_label = customtkinter.CTkLabel(master=root,text_font=('Helvetica',34,"bold"),bg_color=("gray90","gray16"))
time_label.place(height='55', width='220',relx=0.72, rely=0.01)
my_time()

middleFont = tkinter.font.Font(family = 'Helvetica', size = 34, weight = "bold")

def update():
    label_down.configure(text=CardValue)
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
label_down = customtkinter.CTkLabel(master=root,bg_color=("gray90","gray16"), text="Přiložte kartu a stiskněte tlačítko!",text_color="black", text_font=('Helvetica',20,"bold"))
label_down.place(height='60', width='800',relx=0.0, rely=0.9)

label_middleTop= customtkinter.CTkLabel(master=root,bg_color=("gray90","gray16"), textvariable=var, text_font=('Helvetica',30,"bold"))
label_middleTop.place(height='55', width='200',relx=0.35, rely=0.005)

button_exit = customtkinter.CTkButton(master=root, command=close,fg_color="#ff0000",bg_color=("gray90","gray16"),text_color="black", text="x", width=20, height=20, corner_radius=10,border_width=3,text_font=('Helvetica',20))
button_exit.place(height='40', width='40', relx=0.94, rely=0.91)

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