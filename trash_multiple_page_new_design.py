## Toggle an LED when the GUI button is pressed ##
import json
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
import queue

#create a queue for shared memory between threads
queue=queue.Queue()

class Reader(rdm6300.BaseReader): # read card ID
    CardRemoved = False
    def card_inserted(self, card):
        print(f"[{card.value}] ID přečtené karty")
        global CardValue
        CardValue = card.value
        global CardInserted
        CardInserted = True
        Reader.CardRemoved = False
        if queue.qsize() >= 2:
            queue.put(card.value)
            queue.get()
            print("queue i greater that 2 in Reader")
        else:
            queue.put(card.value)
        buzzToggle()

    def card_removed(self, card):
        print(f"card removed {card}")
        Reader.CardRemoved = True

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
clickCountAuthButton = 0
clickCountButtonOpen = 0
clickCountButtonLeave = 0
clickCountButtonDoctor = 0
clickCountButtonCoffee = 0


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
                                    text="Přiložte prosím kartu",
                                    text_font=('Helvetica', 30, "bold"))
idle_label.place(height='60', width='800', relx=0.0, rely=0.45)
# todo -arrow pointing to place where they have to put the card

button_to_statuscodewindow = customtkinter.CTkButton(master=root, state='normal',command=lambda:standByButtonAuth(),
                                                     fg_color="#ff0000",
                                                     bg_color=("gray90", "gray16"), text_color="black",
                                                     text="auth", width=100, height=300,
                                                     corner_radius=10, border_width=3,
                                                     text_font=('Helvetica', 20))
button_to_statuscodewindow.place(height='320', width='80', relx=0.88, rely=0.2)

#functions to provide just one click on time and does not send multiple request
def clickCountAuthButtonReset():
    global clickCountAuthButton
    clickCountAuthButton=0

def standByButtonAuth():
    global clickCountAuthButton
    clickCountAuthButton =clickCountAuthButton+1
    button_to_statuscodewindow.after(300, clickCountAuthButtonReset)#after 10s clickCountAuthButtonReset is called
    if clickCountAuthButton == 1:
        authentication(CardValue)
#-------------------------------------------------------------------------------

# compare actual card number with number with logged user
#def newUser():
   # logout()
  #  erase()

#setting variables for following functions
global bg
bg = StringVar()
global statusCodeText
statusCodeText = StringVar()
global actionId
actionId = 0
global token
global CardAgain
CardAgain = True
global user_name
user_name=0
global CardNumber
CardNumber=0

# -------------------------authentication card number and id of device--------------------------------------------------
# -------------------------POST    API/TERMINAL/AUTHORIZATION ----------------------------------------------------------
def authentication(CardValue):
    global CardAgain
    global clickCountAuthButton

    if CardValue !=0 or (CardValue !=0 and CardAgain):
        CardValueString = str(CardValue)
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
            statusCodeText.set("Zařízení není rozpoznáno " + str(authorization.status_code))
            CardAgain = True
            statusCodeWindow()
            erase()

        if authorization.status_code == 401:
            print("you are not authenticated")
            statusCodeText.set("Karta není rozpoznána " + str(authorization.status_code))
            CardAgain = True
            statusCodeWindow()
            erase()

        if authorization.status_code == 200:
            request_dict = authorization.json()
            print(request_dict)
            print(request_dict['accessToken'])
            global token
            token = request_dict['accessToken']
            print("you are succesfully authenticated")
            getUser()
            statusCodeText.set("")
            CardAgain = True
            mainWindow()

        if authorization.status_code == 400:
            print("something is wrong")
            CardAgain = False
            statusCodeText.set("Karta nebo zařízení nebylo rozpoznáno ")
            statusCodeWindow()
            erase()
            print(".........VALUES FOR QUEUE.......")
            #print(queue.get())
            #print(queue.get())
            #print(queue.get())
            print(".........VALUES FOR QUEUE.......")

# -----------------------------------------getting information about user-----------------------------------------------
#----------------------------------------GET terminal/user with JWT token-----------------------------------------------
def getUser():
    print(token)
    getUser = requests.get(
        "https://api-dev-becvary.techcrowd.space/api/terminal/user",headers={'Authorization':'Bearer {}'.format(token)})
    print("---------------get data---------------")
    print(getUser.status_code)
    print(getUser.text)

    if getUser.status_code == 403:
        # show screen with this status code
        statusCodeText.set("403 api/terminal/user  ")
        statusCodeWindow()

    if getUser.status_code == 401:
        statusCodeText.set("401 api/terminal/user")
        statusCodeWindow()

    if getUser.status_code == 200:
        statusCodeText.set("")
        getCardId()

    if getUser.status_code == 400:
        statusCodeText.set("400 api/terminal/user")
        statusCodeWindow()

    request_dict_get = getUser.json()
    global user_name
    user_name = StringVar()
    user_firstname = request_dict_get['user']['firstname']
    user_lastname = request_dict_get['user']['lastname']
    print(user_firstname,user_lastname)
    user_name = user_firstname + " " +user_lastname
    print(user_name)

#-------------------------------------getting cardID from logged user---------------------------------------------------
#----------------------------------------GET API/AUTH/LOGGED-USER-------------------------------------------------------
def getCardId():
    getCardId = requests.get(
        "https://api-dev-becvary.techcrowd.space/api/auth/logged-user",headers={'Authorization':'Bearer {}'.format(token)})
    print("---------------get data---------------")
    print(getCardId.status_code)
    print(getCardId.text)
    request_dict_get_logged_user = getCardId.json()
    global CardId
    print("####################################################################")
    print(request_dict_get_logged_user)
    CardInfo = request_dict_get_logged_user ['cards']
    global CardIds
    global CardIdsString
    global CardIdString
    global CardNumber
    global CardNumbersString
    for CardNumber in CardInfo:
        CardNumbers = CardNumber['cardNumber']
        print(CardNumbers)
        CardNumbersString=str(CardNumbers)

    CardNumber =int(CardNumbersString)
    for CardId in CardInfo:
        CardIds=CardId['id']
        print(CardIds)
        CardIdsString = str(CardIds)
    CardIdString = CardIdsString[0]
    CardId=int(CardIdString)
    print("-----------CARD ID and NUMBER FROM LOGGED USER-----------")
    print(CardId)
    print(CardNumber)
    print("----------------------------------------------")

#-----------------------------------send action choosed by user---------------------------------------------------------
#------------------------------------POST API/TERMINAL/ACTION-----------------------------------------------------------
def action():
    deviceId = int(internalDeviceId)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(actionId,CardId,deviceId)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    payload = {'actionId':1 , 'cardId': 2,'deviceId':1}
    print("===========>", payload)
    postAction = requests.post(
        "https://api-dev-becvary.techcrowd.space/api/terminal/action",headers={'Authorization':'Bearer {}'.format(token)}, json=payload)
    print("---------------post data---------------")
    print(postAction.status_code)
    print(postAction.text)
    if postAction.status_code == 403:
        # show screen with this status code
        statusCodeText.set("403 api/terminal/action  ")
        statusCodeWindow()

    if postAction.status_code == 401:
        statusCodeText.set("401 api/terminal/action")
        statusCodeWindow()

    if postAction.status_code == 200:
        statusCodeText.set("")

    if postAction.status_code == 400:
        statusCodeText.set("api/terminal/action")
        statusCodeWindow()

    logout() #logout user

#-------------------------------------logout user, ready for next user--------------------------------------------------
#----------------------------------------DELETE API/TERMINAL/LOGOUT-----------------------------------------------------
def logout():
    logoutDelete = requests.delete(
        "https://api-dev-becvary.techcrowd.space/api/terminal/logout" ,headers={'Authorization':'Bearer {}'.format(token)})
    print("---------------delete data---------------")
    print(logoutDelete.status_code)
    print(logoutDelete.text)
    print(user_name)
    print(CardValue)
    print(actionId)

    if logoutDelete.status_code == 200:
        erase()
        print("------call in delete------")
        print(token)
        print("--------------------------")

#-----------------------------erase all local variable connected to temporary logged user-------------------------------
def erase():
    global token
    global CardValue
    global user_name
    CardValue = 0
    user_name = 0
    token = 0
    actionId=0
    queue.empty()
    print("######deleted?#####")
    x = user_name
    z = actionId
    print(x)
    print(CardValue)
    print(z)

# ----------------------------okno s nabidkou moznosti vyberu (prichod, lekar, soukrome,....)---------------------------
# nahrani obrazku
logoTC = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/logo.png").resize((185, 50), Image.ANTIALIAS))
coffee_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/coffee.png").resize((60, 60), Image.ANTIALIAS))
open_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((60, 60), Image.ANTIALIAS))
leave_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/out.png").resize((60, 60), Image.ANTIALIAS))
doctor_image = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/doctor.png").resize((60, 60), Image.ANTIALIAS))


#-------------------------------------------MAIN WINDOW-----------------------------------------------------------------
#--------------------------user choose one type of action by clicking on widget-----------------------------------------
#-----------------------------------types of widgets will shows by API -------------------------------------------------
def mainWindow():
    global mainwindow
    mainwindow = Toplevel()
    mainwindow.geometry("800x480")
    #mainwindow.overrideredirect(True)
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
    global button_in
    global button_out
    global button_doctor
    global button_coffee
    button_in = customtkinter.CTkButton(master=mainwindow, command=mainWindowButtonOpen, hover_color="#09bd6f",
                                        border_color="#0f0f0f", fg_color="#0dff96", image=open_image,
                                        text="Příchod", text_color="black", width=160, height=120,
                                        corner_radius=25, border_width=4, text_font=('Helvetica', 17, 'bold'),
                                        bg_color=("gray90", "gray16"), compound="bottom")
    button_in.place(height='120', width='160', x=220, rely=0.2)

    button_out = customtkinter.CTkButton(master=mainwindow, command=mainWindowButtonLeave, hover_color="#bf3d3d",
                                         border_color="#0f0f0f", fg_color="#ff5252", image=leave_image,
                                         text="Odchod", text_color="black", width=160, height=120,
                                         corner_radius=25, border_width=4, text_font=('Helvetica', 17, 'bold'),
                                         bg_color=("gray90", "gray16"), compound="bottom")
    button_out.place(height='120', width='160', x=420, rely=0.2)

    button_doctor = customtkinter.CTkButton(master=mainwindow, command=mainWindowButtonDoctor, hover_color="#2d56ad",
                                            border_color="#0f0f0f", fg_color="#427bf5", image=doctor_image,
                                            text="Lékař", text_color="black", width=160, height=120,
                                            corner_radius=25, border_width=4,
                                            text_font=('Helvetica', 17, 'bold'), bg_color=("gray90", "gray16"),
                                            compound="bottom")
    button_doctor.place(height='120', width='160', x=620, rely=0.2)

    button_coffee = customtkinter.CTkButton(master=mainwindow, command=mainWindowButtonCoffee, hover_color="#b37c30",
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
                                        text="Stiskněte tlačítko!",
                                        text_font=('Helvetica', 20, "bold"))
    label_down.place(height='60', width='800', relx=0.0, rely=0.9)

    label_down_line = customtkinter.CTkLabel(master=mainwindow, bg_color="#34b7eb", text="")
    label_down_line.place(x='0', y='430', height='3', width='800')

    button_exit = customtkinter.CTkButton(master=mainwindow, command=close, fg_color="#ff0000",
                                          bg_color=("gray90", "gray16"), text_color="black", text="x", width=20,
                                          height=20, corner_radius=10, border_width=3,
                                          text_font=('Helvetica', 20))
    button_exit.place(height='40', width='40', relx=0.94, rely=0.91)
    mainwindow.after(6000, mainwindowDestroy)

# -----------------functions to provide just one click on time and does not send multiple request----------------------
def clickCountOpenButtonReset():
    global clickCountButtonOpen
    clickCountButtonOpen = 0

def mainWindowButtonOpen():
    global clickCountButtonOpen
    clickCountButtonOpen = clickCountButtonOpen + 1
    button_in.after(3000,
                                     clickCountAuthButtonReset)  # after 10s clickCountAuthButtonReset is called
    if clickCountButtonOpen == 1:
        arrivalToggle()

def clickCountLeaveButtonReset():
    global clickCountButtonLeave
    clickCountButtonLeave = 0

def mainWindowButtonLeave():
    global clickCountButtonLeave
    clickCountButtonLeave = clickCountButtonLeave + 1
    button_out.after(3000,
                                     clickCountLeaveButtonReset)  # after 10s clickCountAuthButtonReset is called
    if clickCountButtonLeave == 1:
        leaveToggle()

def clickCountDoctorButtonReset():
    global clickCountButtonDoctor
    clickCountButtonDoctor = 0

def mainWindowButtonDoctor():
    global clickCountButtonDoctor
    clickCountButtonDoctor = clickCountButtonDoctor + 1
    button_doctor.after(3000,
                                     clickCountDoctorButtonReset)  # after 10s clickCountAuthButtonReset is called
    if clickCountButtonDoctor == 1:
        doctorToggle()

def clickCountCoffeeButtonReset():
    global clickCountButtonDoctor
    clickCountButtonDoctor = 0

def mainWindowButtonCoffee():
    global clickCountButtonCoffee
    clickCountButtonCoffee = clickCountButtonCoffee + 1
    button_coffee.after(3000,
                                     clickCountCoffeeButtonReset)  # after 10s clickCountAuthButtonReset is called
    if clickCountButtonCoffee == 1:
        coffeeToggle()
# -------------------------------okno zobrazujici stav propojeni s API (status code)------------------------------------
def statusCodeWindow():
    buzzToggle()
    buzzToggle()
    print(statusCodeText.get())
    if statusCodeText.get() != "":
        print("we are in status window condition")
        print(statusCodeText.get())
        global statuswindow
        statuswindow = Toplevel()
        statuswindow.geometry("800x480")
        statuswindow.overrideredirect(True)

        ## Setting background
        background_statuswindow = customtkinter.CTkFrame(master=statuswindow, fg_color="#ff5b4f")
        background_statuswindow.place(x=0, y=0, height='480', width='800')

        # create frame to hide background of the icons
        statuswindow_frame = customtkinter.CTkFrame(master=statuswindow, width=740, height=365,
                                                    bg_color="#ff5b4f",
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

        statuswindow.after(5000, statuswindowDestroy)


# ----------------------pop up okno s informacemi o zamestnanci a vybrane aktivite--------------------------------------
coffee_image_pop = ImageTk.PhotoImage(
    Image.open("/home/pi/Downloads/coffee.png").resize((200, 200), Image.ANTIALIAS))
open_image_pop = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/in.png").resize((200, 200), Image.ANTIALIAS))
leave_image_pop = ImageTk.PhotoImage(
    Image.open("/home/pi/Downloads/out.png").resize((200, 200), Image.ANTIALIAS))
doctor_image_pop = ImageTk.PhotoImage(
    Image.open("/home/pi/Downloads/doctor.png").resize((200, 200), Image.ANTIALIAS))

def popup():
    buzzToggle()
    global cardNumber
    if CardValue != 0:
        global pop
        global pop_frame
        global img_arrow
        pop = Toplevel()
        pop.geometry("800x480")
        #pop.overrideredirect(True)

        background_pop_frame = customtkinter.CTkFrame(master=pop, width=800, height=480, bg_color="gray16",
                                                      fg_color="gray40")
        background_pop_frame.place(x=0, y=0)

        pop_frame = customtkinter.CTkFrame(master=pop, width=720, height=380, bg_color="gray40", border_width=5,
                                           border_color="black")
        pop_frame.place(x=40, y=50)
        label_act = customtkinter.CTkLabel(master=pop, bg_color=("gray90", "gray16"), corner_radius=10,
                                           textvariable=var, text_color="black", text_font=('Helvetica', 30, "bold"))
        label_act.place(height='80', width='300', x='50',y='80')

        label_user = customtkinter.CTkLabel(master=pop, bg_color=("gray90", "gray16"), corner_radius=10,
                                            text=user_name, text_color="black", text_font=('Helvetica', 30, "bold"))
        label_user.place(height='80', width='450', x='50',y='190')

        label_card = customtkinter.CTkLabel(master=pop, bg_color=("gray90", "gray16"), corner_radius=10,
                                            text=CardNumber, text_color="black", text_font=('Helvetica', 30, "bold"))
        label_card.place(height='80', width='300', x='50',y='300')

        label_icon = customtkinter.CTkButton(master=pop, width=200, height=200, text="", fg_color="black",
                                             border_width=0)
        label_icon.place(x=500, y=120)

        if bg.get() == "blue":
            pop_frame.configure(fg_color="#427bf5")
            label_icon.configure(fg_color="#427bf5",bg_color="#427bf5")
            label_act.configure(bg_color="#427bf5")
            label_user.configure(bg_color="#427bf5")
            label_card.configure(bg_color="#427bf5")
            label_icon.configure(image=doctor_image_pop)
            print("bg is blue ------")
        if bg.get() == "red":
            pop_frame.configure(fg_color="#ff5252")
            label_icon.configure(fg_color="#ff5252",bg_color="#ff5252")
            label_act.configure(bg_color="#ff5252")
            label_user.configure(bg_color="#ff5252")
            label_card.configure(bg_color="#ff5252")
            label_icon.configure(image=leave_image_pop)
            print("bg is red ------")
        if bg.get() == "green":
            pop_frame.configure(fg_color="#0dff96")
            label_icon.configure(fg_color="#0dff96",bg_color="#0dff96")
            label_act.configure(bg_color="#0dff96")
            label_user.configure(bg_color="#0dff96")
            label_card.configure(bg_color="#0dff96")
            label_icon.configure(image=open_image_pop)
            print("bg is green ------")
        if bg.get() == "brown":
            pop_frame.configure(fg_color="#f5aa42")
            label_icon.configure(fg_color="#f5aa42",bg_color="#f5aa42")
            label_act.configure(bg_color="#f5aa42")
            label_user.configure(bg_color="#f5aa42")
            label_card.configure(bg_color="#f5aa42")
            label_icon.configure(image=coffee_image_pop)
            print("bg is brown ------")

        print("popup start")
        pop.after(5000, popDestroy)

    else:
        print("error: no card inserted!!!!!!!!")

### Event Functions ###
def buzzToggle():
    RPi.GPIO.output(buzz, RPi.GPIO.LOW)
    sleep(0.2)
    RPi.GPIO.output(buzz, RPi.GPIO.HIGH)
def arrivalToggle():
    global actionId
    var.set("Příchod")
    bg.set("green")
    actionId = 2
    popup()
    action()

def leaveToggle():
    global actionId
    var.set("Odchod")
    bg.set("red")
    actionId = 3
    popup()
    action()

def doctorToggle():
    global actionId
    var.set("Lékař")
    bg.set("blue")
    actionId=4
    popup()
    action()

def coffeeToggle():
    global actionId
    var.set("Soukromě")
    bg.set("brown")
    actionId=1
    popup()
    action()

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

#r = Reader('/dev/ttyS0')
#r.start()

def rfidreader():
    r = Reader('/dev/ttyS0')
    r.start()
   # if(CardValue!=0 and Reader.CardRemoved):
   #     r.stop()

def otherCard():
    print("in other card function")
    if queue.qsize() >= 2:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>...queue is equal or bigger than 2")
        firstCard=queue.get()
        secondCard = queue.get()
        print(firstCard,secondCard)

        if firstCard != secondCard:
            print("THEY ARE NOT EQUAL.....REFRESH USER BY NEW ONE IMMEIDATELLY")
            if user_name:
                logout()
                erase()
           # close()

    #if user_name != 0:
     #   print("in user name condition")

      #  if CardValue != CardNumber and (CardNumber != 0):
       #     print("given number: ", CardValue, " VS number from logged user: ", CardNumber)


def checker_thread():
    while True:
        time.sleep(1)
        otherCard()


t1 = threading.Thread(target=rfidreader)
t2 = threading.Thread(target=checker_thread)
t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
t2.start()
#t1.join()
#t2.join()
