## Toggle an LED when the GUI button is pressed ##
from tkinter import *
import tkinter.font
import customtkinter
import RPi.GPIO
from time import strftime
from time import sleep
import time
from PIL import ImageTk, Image
import rdm6300
import threading
import requests
import API_auth as API

data = API.payload
print(data)
print("######################################")


class Reader(rdm6300.BaseReader): # read card ID
    def card_inserted(self, card):
        #print(f"card inserted {card}")
        #label_down.config(text=card)
        print(f"[{card.value}] ID přečtené karty")
        global CardValue
        CardValue = card.value
        #label_down.config(text="Stiskněte tlačítko!")
        global CardInserted
        CardInserted = True

    def card_removed(self, card):
        print(f"card removed {card}")
        #authentication(CardValue)
        #global CardRemoved
        #self.CardRemoved = True

    def invalid_card(self, card):
        print(f"invalid card {card}")


# Setting theme dark/light
customtkinter.set_appearance_mode("dark")
# customizable theme via json file
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

### HARDWARE DEFINITIONS ###
RPi.GPIO.setmode(RPi.GPIO.BCM)
#Set buzzer - pin 27 as output
buzz=27
RPi.GPIO.setup(buzz,RPi.GPIO.OUT)
# Identification number of this terminal to validate communication with API
internalDeviceId = "0001"
CardValue = 0

root = customtkinter.CTk()
root.geometry("800x480")
root.title("Attendace System")

# set background color and dimension
background_root = customtkinter.CTkFrame(master=root, fg_color=("gray90", "gray16"), height=480, width=800)
background_root.place(x=0, y=0)

# first window(idle window) - insert card label
logo = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/logo.png").resize((210, 60), Image.ANTIALIAS))
label_logo = customtkinter.CTkLabel(master=root, image=logo, bg_color=("gray90", "gray16"))
label_logo.place(height='60', width='210', x='5', y='5')

idle_label = customtkinter.CTkLabel(master=root, bg_color=("gray90", "gray16"),
                                    text="Přiložte prosím kartu", text_color="white",
                                    text_font=('Helvetica', 30, "bold"))
idle_label.place(height='60', width='800', relx=0.0, rely=0.45)
# todo -arrow pointing to place where they have to put the card

# if (CardValue !=0 and HW_id ==1234):
# POST /terminal/autorization

# response ???
# if response from api = 403 error code
#   something wrong
button_to_mainwindow = customtkinter.CTkButton(master=root, command=lambda: mainWindow(), fg_color="#ff0000",
                                               bg_color=("gray90", "gray16"), text_color="black", text="MW",
                                               width=20, height=20,
                                               corner_radius=10, border_width=3, text_font=('Helvetica', 20))
button_to_mainwindow.place(height='40', width='80', relx=0.9, rely=0.91)

button_to_statuscodewindow = customtkinter.CTkButton(master=root, command=lambda: authentication(CardValue),
                                                     fg_color="#ff0000",
                                                     bg_color=("gray90", "gray16"), text_color="black",
                                                     text="S", width=20, height=20,
                                                     corner_radius=10, border_width=3,
                                                     text_font=('Helvetica', 20))
button_to_statuscodewindow.place(height='40', width='80', relx=0.8, rely=0.91)

global bg
bg = StringVar()
global statusCodeText
statusCodeText = StringVar()

# ------------------------------------------------------------------------------

def authentication(CardValue):
    # API first call - card ID + HW device ID send
    # todo
    #intDeviceIDINT = int(internalDeviceId)
    CardValueString = str(CardValue)
    payload = dict(key1=internalDeviceId, key2=CardValueString)
    payload={'internalDeviceId':internalDeviceId, 'cardNumber':CardValueString}
    print("===========>",payload)
    authorization = requests.post(
        "https://api-dev-becvary.techcrowd.space/api/terminal/authorization", data=payload)
    print("---------------post data---------------")
    print(authorization.status_code)
    print(authorization.text)
    print(authorization.content)
    print(authorization.request)
    print("---------------------------------------")
    buzzToggle()
    if authorization.status_code == 403:
        # show screen with this status code
        print("device is not authenticated")
        statusCodeText.set("Zařízení není rozpoznáno")
        statusCodeWindow()

    if authorization.status_code == 401:
        print("you are not authenticated")
        statusCodeText.set("Karta není rozpoznána")
        statusCodeWindow()

    if authorization.status_code == 200:
        print("you are succesfully authenticated")
        statusCodeText.set("")
        mainWindow()

    if authorization.status_code == 400:
        print("something is wrong")
        statusCodeText.set("Karta nebo zařízení nebylo rozpoznáno")
        statusCodeWindow()

# ------------------------------------------------------------------------------------------------------

#object = Reader()
#cardRem = object.CardRemoved
#if cardRem == True:
 #   print("jsem v /////////////////////////////")
    #  authentication(CardValue)
# ------------------------okno s nabidkou moznosti vyberu (prichod, lekar, soukrome,....)--------------
# nahrani obrazku
logoTC = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/logo.png").resize((185, 50), Image.ANTIALIAS))
coffee_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/coffee.png").resize((60, 60), Image.ANTIALIAS))
open_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((60, 60), Image.ANTIALIAS))
leave_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/out.png").resize((60, 60), Image.ANTIALIAS))
doctor_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/doctor.png").resize((60, 60), Image.ANTIALIAS))

def mainWindow():
    global mainwindow
    mainwindow = Toplevel()
    mainwindow.geometry("800x480")
    mainwindow.overrideredirect(True)
    ## Setting background
    global var
    var = StringVar()

    background_mainWindow = customtkinter.CTkFrame(master=mainwindow, fg_color=("gray20", "gray50"))
    background_mainWindow.place(x=0, y=0, height='480', width='800')
    # Create background label for top part
    label_top = customtkinter.CTkLabel(master=mainwindow, bg_color=("gray90", "gray16"))
    label_top.place(height='60', width='800')

    # Create a Label Widget to display the text or Image
    label_logo = customtkinter.CTkLabel(master=mainwindow, image=logoTC, bg_color=("gray90", "gray16"))
    label_logo.place(height='50', width='185', x='5', y='5')

    label_middleTop = customtkinter.CTkLabel(master=mainwindow, bg_color=("gray90", "gray16"), textvariable=var,
                                             text_font=('Helvetica', 30, "bold"))
    label_middleTop.place(height='55', width='200', relx=0.35, rely=0.01)

    label_top_line = customtkinter.CTkLabel(master=mainwindow, bg_color="#34b7eb", text="")
    label_top_line.place(x='0', y='60', height='3', width='800')

    # create frame to hide background of the icons
    frame1 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame1.place(height='140', width='180', x=210, rely=0.18)
    frame2 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame2.place(height='140', width='180', x=10, rely=0.18)
    frame3 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame3.place(height='140', width='180', x=410, rely=0.18)
    frame4 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame4.place(height='140', width='180', x=610, rely=0.18)

    # frames for second row
    frame5 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame5.place(height='140', width='180', x=210, rely=0.52)
    frame6 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame6.place(height='140', width='180', x=10, rely=0.52)
    frame7 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame7.place(height='140', width='180', x=410, rely=0.52)
    frame8 = customtkinter.CTkFrame(master=mainwindow, corner_radius=25, bg_color=("gray20", "gray50"))
    frame8.place(height='140', width='180', x=610, rely=0.52)

    button_in = customtkinter.CTkButton(master=mainwindow, command=arrivalToggle, hover_color="#09bd6f",
                                        border_color="#0f0f0f", fg_color="#0dff96", image=open_image,
                                        text="Příchod", text_color="black", width=160, height=120,
                                        corner_radius=25, border_width=4, text_font=('Helvetica', 17, 'bold'),
                                        bg_color=("gray90", "gray16"), compound="bottom")
    button_in.place(height='120', width='160', x=220, rely=0.2)

    button_out = customtkinter.CTkButton(master=mainwindow, command=leaveToggle, hover_color="#bf3d3d",
                                         border_color="#0f0f0f", fg_color="#ff5252", image=leave_image,
                                         text="Odchod", text_color="black", width=160, height=120,
                                         corner_radius=25, border_width=4, text_font=('Helvetica', 17, 'bold'),
                                         bg_color=("gray90", "gray16"), compound="bottom")
    button_out.place(height='120', width='160', x=420, rely=0.2)

    button_doctor = customtkinter.CTkButton(master=mainwindow, command=doctorToggle, hover_color="#2d56ad",
                                            border_color="#0f0f0f", fg_color="#427bf5", image=doctor_image,
                                            text="Lékař", text_color="black", width=160, height=120,
                                            corner_radius=25, border_width=4,
                                            text_font=('Helvetica', 17, 'bold'), bg_color=("gray90", "gray16"),
                                            compound="bottom")
    button_doctor.place(height='120', width='160', x=620, rely=0.2)

    button_coffee = customtkinter.CTkButton(master=mainwindow, command=coffeeToggle, hover_color="#b37c30",
                                            border_color="#0f0f0f", fg_color="#f5aa42", image=coffee_image,
                                            text="Soukromě", text_color="black", width=160, height=120,
                                            corner_radius=25, border_width=4,
                                            text_font=('Helvetica', 17, 'bold'), bg_color=("gray90", "gray16"),
                                            compound="bottom")
    button_coffee.place(height='120', width='160', x=20, rely=0.2)

    cardData = StringVar()
    cardData.set(rdm6300.CardData.value)

    ## Active label down for inform user about state
    label_down = customtkinter.CTkLabel(master=mainwindow, bg_color=("gray90", "gray16"),
                                        text="Stiskněte tlačítko!", text_color="white",
                                        text_font=('Helvetica', 20, "bold"))
    label_down.place(height='60', width='800', relx=0.0, rely=0.9)

    label_down_line = customtkinter.CTkLabel(master=mainwindow, bg_color="#34b7eb", text="")
    label_down_line.place(x='0', y='430', height='3', width='800')

    button_exit = customtkinter.CTkButton(master=mainwindow, command=close, fg_color="#ff0000",
                                          bg_color=("gray90", "gray16"), text_color="black", text="x", width=20,
                                          height=20, corner_radius=10, border_width=3,
                                          text_font=('Helvetica', 20))
    button_exit.place(height='40', width='40', relx=0.94, rely=0.91)
    mainwindow.after(8000, mainwindowDestroy)

# ----------------------------------okno zobrazujici stav propojeni s API (status code)------------------------------------------
def statusCodeWindow():
    print(statusCodeText.get())
    if statusCodeText.get() != "":
        global statuswindow
        statuswindow = Toplevel()
        statuswindow.geometry("800x480")
        statuswindow.overrideredirect(True)

        ## Setting background
        background_statuswindow = customtkinter.CTkFrame(master=statuswindow, fg_color="#ff5b4f")
        background_statuswindow.place(x=0, y=0, height='480', width='800')

        # create frame to hide background of the icons
        statuswindow_frame = customtkinter.CTkFrame(master=statuswindow, width=740, height=365,
                                                    bg_color="gray40",
                                                    border_width=3,
                                                    border_color="black")
        statuswindow_frame.place(x=30, y=90)

        # Create background label for top part
        label_top = customtkinter.CTkLabel(master=statuswindow, text="", bg_color=("gray90", "gray16"))
        label_top.place(height='60', width='800')

        # Create a Label Widget to display the text or Image
        label_logo = customtkinter.CTkLabel(master=statuswindow, image=logoTC, bg_color=("gray90", "gray16"))
        label_logo.place(height='50', width='185', x='5', y='5')

        label_middle_statusmess = customtkinter.CTkLabel(master=statuswindow, bg_color=("gray90", "gray16"),
                                                         textvariable=statusCodeText,
                                                         text_font=('Helvetica', 24, "bold"))
        label_middle_statusmess.place(height='55', width='660', relx=0.1, rely=0.5)

        label_top_line = customtkinter.CTkLabel(master=statuswindow, bg_color="#34b7eb", text="")
        label_top_line.place(x='0', y='60', height='5', width='800')

        statuswindow.after(8000, statuswindowDestroy)

# ----------------------pop up okno s informacemi o yamestnanci a vzbrane aktivite
coffee_image_pop = ImageTk.PhotoImage(
    Image.open("/home/pi/Downloads/coffee.png").resize((200, 200), Image.ANTIALIAS))
open_image_pop = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((200, 200), Image.ANTIALIAS))
leave_image_pop = ImageTk.PhotoImage(
    Image.open("/home/pi/Downloads/out.png").resize((200, 200), Image.ANTIALIAS))
doctor_image_pop = ImageTk.PhotoImage(
    Image.open("/home/pi/Downloads/doctor.png").resize((200, 200), Image.ANTIALIAS))

def popup():
    if CardValue != 0:
        print(f"prijata data z karty jsou {CardValue}")
        global pop
        global pop_frame
        global img_arrow
        pop = Toplevel()
        pop.geometry("800x480")
        pop.overrideredirect(True)
        print("_______")
        print(bg.get())
        print("_______")

        background_pop_frame = customtkinter.CTkFrame(master=pop, width=800, height=480, bg_color="red",
                                                      fg_color="gray40")
        background_pop_frame.place(x=0, y=0)

        pop_frame = customtkinter.CTkFrame(master=pop, width=720, height=380, bg_color="gray40", border_width=5,
                                           border_color="black")
        pop_frame.place(x=40, y=50)
        label_act = customtkinter.CTkLabel(master=pop, bg_color=("gray90", "gray16"), corner_radius=10,
                                           textvariable=var, text_font=('Helvetica', 30, "bold"))
        label_act.place(height='80', width='300', relx=0.4, rely=0.15)
        label_user = customtkinter.CTkLabel(master=pop, bg_color=("gray90", "gray16"), corner_radius=10,
                                            text='Jan Novák', text_font=('Helvetica', 30, "bold"))
        label_user.place(height='80', width='300', relx=0.4, rely=0.4)
        label_card = customtkinter.CTkLabel(master=pop, bg_color=("gray90", "gray16"), corner_radius=10,
                                            text=CardValue, text_font=('Helvetica', 30, "bold"))
        label_card.place(height='80', width='300', relx=0.4, rely=0.65)
        label_icon = customtkinter.CTkButton(master=pop, width=200, height=200, text="", fg_color="black",
                                             border_width=0)
        label_icon.place(x=60, y=120)

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

        print("popup start")
        pop.after(5000, popDestroy)

    else:
        print("error: no card inserted!!!!!!!!")

### Event Functions ###
def buzzToggle():
    RPi.GPIO.output(buzz, RPi.GPIO.HIGH)
    sleep(0.3)
    RPi.GPIO.output(buzz, RPi.GPIO.LOW)

def arrivalToggle():
    var.set("Příchod")
    bg.set("green")
    popup()

def leaveToggle():
    var.set("Odchod")
    bg.set("red")
    popup()

def doctorToggle():
    var.set("Lékař")
    bg.set("blue")
    popup()

def coffeeToggle():
    var.set("Soukromě")
    bg.set("brown")
    popup()

def popDestroy():
    pop.destroy()
    print("popup destroyed")

def mainwindowDestroy():
    mainwindow.destroy()
    print("mainwindow destroyed")

def statuswindowDestroy():
    statuswindow.destroy()
    print("statuscodewindow destroyed")

def close():
    RPi.GPIO.cleanup()
    pop.destroy()
    mainwindow.destroy()
    statuswindow.destroy()
    root.destroy()

### REAL TIME ###
def my_time():
    time_string = strftime('%H:%M:%S')  # time format
    time_label.configure(text=time_string)
    time_label.after(1000, my_time)  # time delay of 1000 milliseconds

my_font = ('Helvetica', 30, 'bold')  # display size and style
time_label = customtkinter.CTkLabel(master=root, text_font=('Helvetica', 34, "bold"),
                                    bg_color=("gray90", "gray16"))
time_label.place(height='55', width='220', relx=0.72, rely=0.01)
my_time()

#Create a fullscreen window
#root.attributes('-fullscreen', True)
root.protocol("WM_DELETE_WINDOW", close) # cleanup GPIO when user closes window

def rfidreader():
    r = Reader('/dev/ttyS0')
    r.start()


t1 = threading.Thread(target=rfidreader)
t1.setDaemon(True)
t1.start()
