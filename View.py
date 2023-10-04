#! python
# -*- coding: utf-8 -*-

# GUI fuer Thermosycler 

from tkinter import *
#from tkinter.tix import *
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import font
from PIL import Image, ImageTk
from Cycler_Hardware import *
from threading import *
import atexit
from time import sleep, time, strftime
import logging
import pickle
import sys

data = ""

class Gui():
    def __init__(self, root):
        """Do GUI stuff and attach to ObserverPattern"""
        self.root = root
        self.var_testende = StringVar(value="Entleeren")
   
        #print(standart_font.actual())
        #label_frame = Frame(root, height = 100, width=200, borderwidth=3, relief=RIDGE)
        #label_frame.place (x= 550, y = 300)
        #tip = Balloon(root)
        #tip.bind_widget(witghet, balloonmsg="The time of Medium-1")
        #self.label_com_status = Label(root, text="False", relief = GROOVE, fg = "red", width = 6)
        #self.canvas = Canvas(root, width=250, height=250)
        #img = ImageTk.PhotoImage(Image.open("WatersystemSmall.png").resize((250, 250), Image.ANTIALIAS))
        #self.canvas.background = img  # Keep a reference in case this code is put in a function.
        #bg = self.canvas.create_image(0, 0, anchor=NW, image=img)
        #self.canvas.place (x= 170, y = 400)
        #root.bind('<Motion>',self.mouse)

        #Root Window
        self.root.title ("Thermocycling")
        self.root.geometry("1100x600+0+0")
        #Change default Textfont
        standart_font = font.nametofont("TkDefaultFont")
        standart_font.configure(size=9, family="Segoe UI")
        root.option_add("*Font", standart_font)
        #Scrollbar
        self.scrollbar = Scrollbar(root)
        #Menu
        self.menu =     Menu(root)
        self.filemenu = Menu(self.menu)
        self.filemenu.add_command(label="Sichern", command = self.menu_stuff)
        self.filemenu.add_command(label="Laden", command = self.menu_stuff)
        self.filemenu.add_command(label="Beenden", command = self.menu_stuff)
        self.menu.add_cascade(label="Datei",menu = self.filemenu)
        self.root.config(menu=self.menu)
        
        #*************************  Left  ******************************
        self.label_kalt_warm =          Label(root, text="Kalt-Warm-Zyklen")
        self.label_reinigungszeit =     Label(root, text="Reinigungszeit")
        self.label_dauer =              Label(root, text="Dauer", relief=GROOVE)
        self.label_dauer_links =        Label(root, text="Links")
        self.label_dauer_rechts =       Label(root, text="Rechts")
        self.label_solltemp =           Label(root, text="Solltemperatur erfassen - für Auswertung", relief=GROOVE)
        self.label_solltemp_links =     Label(root, text="Links")
        self.label_solltemp_rechts =    Label(root, text="Rechts")
        self.label_medium_links =       Label(root, text="Medium Links")
        self.label_medium_rechts =      Label(root, text="Medium Rechts")
        self.label_testende =           Label(root, text="Nach Testende", relief=GROOVE)
        self.label_optional =           Label(root, text="Optional", relief=GROOVE)
        self.label_logfile =            Label(root, text="Logfile erstellen, Dateiname")
        self.label_bericht =            Label(root, text="Bericht per E-mail senden an")
        #Entries
        self.entry_zyklen =             Entry(root, width = 10)
        self.entry_reinigungszeit =     Entry(root, width = 10)
        self.entry_dauer_links =        Entry(root, width = 10)
        self.entry_dauer_rechts =       Entry(root, width = 10)
        self.entry_solltemp_links =     Entry(root, width = 10)
        self.entry_solltemp_rechts =    Entry(root, width = 10)
        self.entry_medium_links =       Entry(root, width = 10)
        self.entry_medium_rechts =      Entry(root, width = 10)
        self.entry_logfile =            Entry(root, width = 30)
        self.entry_email =              Entry(root, width = 30)
        #Radiobutton
        self.radiobutton_entleeren =    Radiobutton(root, text="Entleeren", variable = self.var_testende, value="Entleeren")
        self.radiobutton_fill_1 =       Radiobutton(root, text="Füllen mit Medium 1" , variable = self.var_testende, value="Füllen 1")
        self.radiobutton_fill_2 =       Radiobutton(root, text="Füllen mit Medium 2" , variable = self.var_testende, value="Füllen 2")
        #Units
        self.label_einheit_zyklen =     Label(root, text="1-1000")   
        self.label_einheit_reinigung =  Label(root, text="Sek.")
        self.label_einheit_dauer_L =    Label(root, text="Sek.")
        self.label_einheit_dauer_R =    Label(root, text="Sek.")
        self.label_einheit_temp_L =     Label(root, text="°C")
        self.label_einheit_temp_R =     Label(root, text="°C")
        self.label_einheit_dateiendung =Label(root, text=".log")
        #Buttons
        self.button_start =               Button(root, text="Start",     fg="blue",command=self.start_test, width = 20)
        self.button_abbrechen =           Button(root, text="Abbrechen", fg="red" ,command=self.stop_test, width = 20, state = DISABLED)

        #***  Place label Left  ***
        space = 40
        self.label_kalt_warm.place           (x= 10,  y = space*1)       
        self.label_reinigungszeit.place      (x= 10,  y = space*2)
        self.label_dauer.place               (x= 10,  y = space*3)
        self.label_dauer_links.place         (x= 10,  y = space*4)
        self.label_dauer_rechts.place        (x= 300, y = space*4)
        self.label_solltemp.place            (x= 10,  y = space*5)
        self.label_solltemp_links.place      (x= 10,  y = space*6)
        self.label_solltemp_rechts.place     (x= 300, y = space*6)
        self.label_medium_links.place        (x= 10,  y = space*7)
        self.label_medium_rechts.place       (x= 250, y = space*7)
        self.label_testende.place            (x= 10,  y = space*8)
        self.label_optional.place            (x= 10,  y = space*10)
        self.label_logfile.place             (x= 10,  y = space*11)
        self.label_bericht.place             (x= 10,  y = space*12)
        #Entries
        self.entry_zyklen.place              (x= 150, y = space*1, width= 50)
        self.entry_reinigungszeit.place      (x= 150, y = space*2, width= 50)
        self.entry_dauer_links.place         (x= 100, y = space*4, width= 50)
        self.entry_dauer_rechts.place        (x= 350, y = space*4, width= 50)
        self.entry_solltemp_links.place      (x= 100, y = space*6, width= 50)
        self.entry_solltemp_rechts.place     (x= 350, y = space*6, width= 50)
        self.entry_medium_links.place        (x= 100, y = space*7, width= 50)
        self.entry_medium_rechts.place       (x= 350, y = space*7, width= 50)
        self.entry_logfile.place             (x= 200, y = space*11, width= 200)
        self.entry_email.place               (x= 200, y = space*12, width= 200)
        #Radiobuttons
        self.radiobutton_entleeren.place     (x= 10,  y = space*9)
        self.radiobutton_fill_1.place        (x= 120, y = space*9)
        self.radiobutton_fill_2.place        (x= 300, y = space*9)
        #Units
        self.label_einheit_zyklen.place      (x= 220, y = space*1)
        self.label_einheit_reinigung.place   (x= 220, y = space*2)
        self.label_einheit_dauer_L.place     (x= 170, y = space*4)
        self.label_einheit_dauer_R.place     (x= 420, y = space*4)
        self.label_einheit_temp_L.place      (x= 170, y = space*6)
        self.label_einheit_temp_R.place      (x= 420, y = space*6)
        self.label_einheit_dateiendung.place (x= 420, y = space*11)
        #Buttons
        self.button_start.place              (x= 10, y = space*13) 
        self.button_abbrechen.place          (x= 250, y = space*13)
               
        #*************************  Right  ******************************   
        self.label_messwerte =          Label(root, text="Aktuelle Messwerte" , relief=GROOVE)
        self.label_temperatur =         Label(root, text="Temperatur", relief=GROOVE)        
        self.label_probenbehaelter =    Label(root, text="Probenbehälter")
        self.label_isttemp_L =          Label(root, text="Links")
        self.label_isttemp_R =          Label(root, text="Rechts")
        self.label_abg_zyklen =         Label(root, text="Abgeschlossene Zyklen")
        self.label_verlauf =            Label(root, text="Verlauf", relief=GROOVE)
        #Label measurements
        self.label_messwert_proben =    Label(root, text="24.1", relief = GROOVE, fg = "green")
        self.label_messwert_temp_L =    Label(root, text="25.2", relief = GROOVE, fg = "green")
        self.label_messwert_temp_R =    Label(root, text="26.3", relief = GROOVE, fg = "green")
        self.label_messwert_zyklen =    Label(root, text="0030", relief = GROOVE, fg = "green")
        #Textbox
        self.text_verlauf =             scrolledtext.ScrolledText(root, height=4)
        Font_tuple = ("Arial", 10)
        self.text_verlauf.configure(font=Font_tuple)
        #Units
        self.label_ein_mess_temp_proben =Label(root, text="°C")
        self.label_ein_mess_temp_L =     Label(root, text="°C")
        self.label_ein_mess_temp_R =     Label(root, text="°C")   

        #****  Place Right ***
        self.label_messwerte.place           (x= 600, y = space*1)
        self.label_temperatur.place          (x= 600, y = space*2)       
        self.label_probenbehaelter.place     (x= 600, y = space*3)
        self.label_isttemp_L.place           (x= 600, y = space*4)
        self.label_isttemp_R.place           (x= 900, y = space*4)
        self.label_abg_zyklen.place          (x= 600, y = space*5)
        self.label_verlauf.place             (x= 600, y = space*6)
        #Label measurements
        self.label_messwert_proben.place     (x= 700, y = space*3, width= 50)
        self.label_messwert_temp_L.place     (x= 700, y = space*4, width= 50)
        self.label_messwert_temp_R.place     (x= 950, y = space*4, width= 50)
        self.label_messwert_zyklen.place     (x= 950, y = space*5, width= 50)
        #Textbox
        self.text_verlauf.place              (x= 600, y = space*7, width=350)
        #Units
        self.label_ein_mess_temp_proben.place(x= 770, y = space*3)
        self.label_ein_mess_temp_L.place     (x= 770, y = space*4)
        self.label_ein_mess_temp_R.place     (x= 1020, y = space*4)  
        #Picture
        self.canvas = Canvas(root, width=450, height=250)
        img = ImageTk.PhotoImage(Image.open("WatersystemSmall.png").resize((450, 250), Image.ANTIALIAS))
        self.canvas.background = img  # Keep a reference in case this code is put in a function.
        bg = self.canvas.create_image(0, 0, anchor=NW, image=img)
        self.canvas.place (x= 600, y = 400)
        
        #Bind Event to Main Window
        root.bind("<<update_gui>>", self.meassage_from_cycler)
        #Attach cycler to get messages from Cycler
        self.cycler = Cycler()
        self.cycler.attach(self.cycler.EVT_CYCLER_STATUS, self.cycler_status)
        self.cycler.attach(self.cycler.EVT_TEMP,          self.new_temp_values)
  

    def cleanup(self):
        """Quit GUI, Stop cycler test and clean-up"""
        print("Clean-Up")
        self.cycler.stop_test()
        self.root.quit()

    def start_test(self):
        "Starts the cycling test, checks user input, Modifies Buttons"
        self.button_start.configure(state=DISABLED)
        self.button_abbrechen.configure(state=NORMAL)
        user_values = self.get_user_inputs()
        self.all_user_inputs_ok = TRUE          #FOR DEBUG COMMENT OUT
        print(self.var_testende.get())

        if self.all_user_inputs_ok == TRUE:
            self.cycler.user_inputs(user_values)
            self.cycler.start_test()
            print("View: Start Cycling")
        else:
            messagebox.showerror("Falsche Benutzereingabe",
                                 "Eingabe keine Zahl oder Wert ausser Limiten" +"\n"
                                +"Dateiname dar nur Alphanumerisch sein [1-9 / A-Z]" + "\n"
                                +"E-mail korrekt ?" +"\n")

    def stop_test(self):
        "Stops the cycler thread, Modifies Button"
        print("View: Stoping cycling")
        self.cycler.stop_test()
        self.button_abbrechen.configure(state=DISABLED)
        self.text_verlauf.insert(END,  strftime("%I:%M:%S ") + "Benutzer: Stop Test einleiten \n")
        self.text_verlauf.see(END)

    def check_user_input_digit(self, text):
        """Check if user entered a Number
           INPUT: str user_text"""
        if text.isdigit() == True:
            return()
        else:
            self.all_user_inputs_ok = False

    def check_user_input_text(self, text):
        """Check if user entered a alpanumerical input
           INPUT: str user_text"""
        if text.isalnum() == True:
            return()
        else:
            self.all_user_inputs_ok = False    

    def get_user_inputs(self):
        """Get the user_inputs from entry_witgets
           INPUT: -
           RETURN:  dict {"field-name": "user-text" ... }"""
        user_inputs = {}
        self.all_user_inputs_ok = True

        cycles = self.entry_zyklen.get()
        self.check_user_input_digit(cycles)

        reinigungszeit = self.entry_reinigungszeit.get()
        self.check_user_input_digit(reinigungszeit)

        dauer_links = self.entry_dauer_links.get()
        self.check_user_input_digit(dauer_links)

        dauer_rechts = self.entry_dauer_rechts.get()
        self.check_user_input_digit(dauer_rechts)

        solltemp_links = self.entry_solltemp_links.get()
        self.check_user_input_digit(solltemp_links)

        solltemp_rechts = self.entry_solltemp_rechts.get()
        self.check_user_input_digit(solltemp_rechts)

        medium_links = self.entry_medium_links.get()
        self.check_user_input_digit(solltemp_links)

        medium_rechts = self.entry_medium_rechts.get()
        self.check_user_input_digit(solltemp_rechts)

        logfile = self.entry_logfile.get()
        self.check_user_input_text(logfile)

        email = self.entry_email.get()
        self.check_user_input_text(email)

        user_inputs["cycles"]           = cycles
        user_inputs["reinigungszeit"]   = reinigungszeit
        user_inputs["dauer_links"]      = dauer_links
        user_inputs["dauer_rechts"]     = dauer_rechts
        user_inputs["solltemp_links"]   = solltemp_links
        user_inputs["solltemp_rechts"]  = solltemp_rechts
        user_inputs["medium_links"]     = medium_links
        user_inputs["medium_rechts"]    = medium_rechts        
        user_inputs["logfile"]          = logfile
        user_inputs["email"]            = email
        return(user_inputs)


    def meassage_from_cycler(self, event):
        """Root event, shows error-messages to the user"""
        messagebox.showerror("Cycler Error", "Die Pumpe benötigt zu viel zeit: " +"\n"
                             "Alle Ventile offen? NOT-AUS frei? Pegelstände ok?" +"\n"
                             "Pumpen zeit = "+ str(event.state))
        self.text_verlauf.insert(END, strftime("%I:%M:%S ") + "Hardware: Pumpen Error \n")


    def new_temp_values(self, dict_temp):
        print(dict_temp)
        self.label_messwert_temp_L.configure(text=dict_temp["TEMP-1"])
        

    def cycler_status(self, status):
        """Gets different messages from cycler thread, generates root. events
           INPUT: str cycler-status"""
        if status == "PUMP_ERROR":
            root.event_generate("<<update_gui>>", when="tail", state=123)
        if status == "TEST END":
            self.button_start.configure(state=NORMAL)
            self.text_verlauf.insert(END, strftime("%I:%M:%S ") + "Hardware: Test gestoppt \n")
            self.text_verlauf.see(END)
        if status == "TEST START":
            self.text_verlauf.insert(END, strftime("%I:%M:%S ") + "Hardware: Test gestartet \n")
            self.text_verlauf.see(END)

    def menu_stuff(self):
        print("menu_stuff")


if __name__ == "__main__":

    root=Tk()
    gui = Gui(root)
    atexit.register(gui.cleanup)
    root.mainloop()

