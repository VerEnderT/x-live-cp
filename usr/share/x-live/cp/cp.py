#!/usr/bin/python3

import sys
import os
import subprocess
import time
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QDesktopWidget, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from PyQt5.QtGui import QCursor, QIcon, QFont
from datetime import datetime

# Pfad zum gewünschten Arbeitsverzeichnis # Das Arbeitsverzeichnis festlegen
arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/cp')

os.chdir(arbeitsverzeichnis)

class Tray(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        screen = QDesktopWidget().screenGeometry()
        self.bg = QLabel(self)
        self.bg.setFixedSize(screen.width(),screen.height())
        self.bg.move(0,0)
        self.settings_cmds =  self.check_com(["command -v xfce4-settings-manager","command -v lxde-control-center","command -v gnome-control-center","command -v systemsettings"]).split("\n")
        self.term_cmds = self.check_com(["command -v gnome-terminal","command -v konsole","command -v xfce4-terminal","command -v lxterminal"]).split("\n")
        self.taskm_cmds = self.check_com(["command -v gnome-system-monitor","command -v ksysguard","command -v xfce4-taskmanager","command -v lxtask","command -v stacer"]).split("\n")

        # Befehlsdefinition
        self.tmcommand = self.taskm_cmds[0]
        self.termcommand = self.term_cmds[0]
        self.settingscommand = self.settings_cmds[0]
        self.rebootcommand = "xfce4-session-logout --reboot --fast"
        self.logoutcommand = "xfce4-session-logout --logout --fast"
        self.poweroffcommand = "xfce4-session-logout --halt --fast"


        #  skalierungsberechnung
        faktor = app.desktop().height()/780
        self.faktor = faktor
        self.bts=int(16 * faktor)
        self.sts=int(15 * faktor)
          
        # diverse variablen
        self.menu_open = False

        # cpu_usage initial daten holen

        self.prev_idle = 0
        self.prev_total = 0
        self.initialize_cpu_stats()
        

        #Buttons definieren
        
        self.btn1 = QPushButton("Einstellungen")
        self.btn1.setFixedWidth(int(180*self.faktor))
        self.btn1.clicked.connect(self.settings)

        self.btn2 = QPushButton(" Terminal ")
        self.btn2.setFixedWidth(int(180*self.faktor))
        self.btn2.clicked.connect(self.terminal)
        self.btn3 = QPushButton("TaskManager")
        self.btn3.setFixedWidth(int(180*self.faktor))
        self.btn3.clicked.connect(self.taskmanager)

        self.btn5 = QPushButton("zurück")
        self.btn5.setFixedWidth(int(180*self.faktor))
        self.btn5.clicked.connect(app.exit)



        # Powerbuttons
        
        self.btn6 = QPushButton(self)
        icon = QIcon("./icons/logout")
        self.btn6.setIcon(icon)
        self.btn6.setIconSize(QSize(36,36))
        self.btn6.setFixedWidth(36)
        self.btn6.clicked.connect(self.logout)

        self.btn7 = QPushButton(self)
        icon = QIcon("./icons/reboot")
        self.btn7.setIcon(icon)
        self.btn7.setIconSize(QSize(36,36))
        self.btn7.setFixedWidth(36)
        self.btn7.clicked.connect(self.reboot)

        self.btn8 = QPushButton(self)
        icon = QIcon("./icons/poweroff")
        self.btn8.setIcon(icon)
        self.btn8.setIconSize(QSize(36,36))
        self.btn8.setFixedWidth(36)
        self.btn8.clicked.connect(self.poweroff)

        self.cal_label = QLabel(self)

        # Aktuelles Datum
        current_date = datetime.now()

        # Nur den Tag extrahieren
        day = current_date.day
        kalender = self.com("ncal -M -b -w ")#.decode("UTF-8")
        while kalender and not kalender[-1].isdigit():
            kalender = kalender[:-1]
        kalender += "  \n"
        test = kalender.replace("  \n","<br>").replace(" ", "&nbsp;").split("_\x08")
        self.cal_label.setTextFormat(Qt.RichText)
        today = str("  "+str(day))[-2:]        
        cal_text = f'{test[0]}<span style="background-color:white;">{today}</span>{test[1]}'
        self.cal_label.setText(cal_text)
        self.cal_label.setTextFormat(Qt.RichText)
        font = QFont("Noto Mono", 32)
        self.cal_label.setFont(font)
        
        self.label_left = QLabel(self)
        self.label_date = QPushButton(self)
        self.label_date.setFixedSize(int(screen.width()*0.4),int(screen.height()*0.1))
        self.label_time = QPushButton(self)
        self.label_time.setFixedSize(int(screen.width()*0.4),int(screen.height()*0.2))
        self.label_usage = QLabel(self)
        
        # menu button
        self.btn_menu = QPushButton(self)
        icon = QIcon("./icons/menu")
        self.btn_menu.setIcon(icon)
        self.btn_menu.setIconSize(QSize(36,36))
        self.btn_menu.setFixedWidth(36)
        self.btn_menu.clicked.connect(self.menu)

        self.menu_widget = QWidget()
        self.menu_label1 = QLabel("Einstellungen für \nX-Live-cp bald verfügbar")
        self.menu_widget.hide()
        calwidth = self.cal_label.width()
        self.menu_widget.setFixedWidth(calwidth)



        # Layouts
        layout = QVBoxLayout()
        menubtnlayout = QHBoxLayout()
        menubtnlayout.addStretch(0)
        menubtnlayout.addWidget(self.btn_menu)

        menulayout = QVBoxLayout()
        menulayout.addWidget(self.menu_label1)
        self.menu_widget.setLayout(menulayout)

        rightlayout = QVBoxLayout()
        rightlayout.addLayout(menubtnlayout)
        rightlayout.addStretch(2)
        rightlayout.addWidget(self.menu_widget)
        rightlayout.addWidget(self.cal_label)
        rightlayout.addStretch(5)


        leftlayout = QVBoxLayout()
        leftlayout.addStretch(4)
        leftlayout.addWidget(self.label_usage)
        leftlayout.addWidget(self.label_left)
        leftlayout.addStretch(1)


        mainlayout = QHBoxLayout()
        mainlayout.addStretch(1)
        mainlayout.addLayout(leftlayout)
        mainlayout.addStretch(2)
        mainlayout.addLayout(layout)
        mainlayout.addStretch(2)
        mainlayout.addLayout(rightlayout)
        mainlayout.addStretch(1)

        layout.addWidget(self.label_time, alignment=Qt.AlignHCenter)
        layout.addWidget(self.label_date, alignment=Qt.AlignHCenter)
        layout.addStretch(3)
        layout.addWidget(self.btn1, alignment=Qt.AlignHCenter)
        layout.addWidget(self.btn2, alignment=Qt.AlignHCenter)
        layout.addWidget(self.btn3, alignment=Qt.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(self.btn5, alignment=Qt.AlignHCenter)
        layout.addStretch(5)

        powerlayout = QHBoxLayout()
        powerlayout.addStretch(80)
        powerlayout.addWidget(self.btn6)
        powerlayout.addStretch(1)
        powerlayout.addWidget(self.btn7)
        powerlayout.addStretch(1)
        powerlayout.addWidget(self.btn8)
        powerlayout.addStretch(1)

        main1layout = QVBoxLayout()
        main1layout.addLayout(mainlayout)
        main1layout.addLayout(powerlayout)
        self.setLayout(main1layout)
        
        # CSS-Styling
        self.setStyleSheet( "QPushButton {" +
                            "font-size: " + str(self.sts) + "px;" +
                            "color: black;" +
                            "background-color: rgba(255, 255, 255, 255);" +
                            "border: 0px solid black;border-radius: 5px;}"+
                            
                            "QPushButton:hover {"+
                            "color: black;" +
                            "background-color: rgba(25, 25, 25, 25);" +
                            "border: 0px solid black;border-radius: 5px;}")

        self.bg.setStyleSheet(  "padding: 0px; margin: 0px;" +
                                "background-color: rgba(155, 155, 155, 195);")        

        self.btn6.setStyleSheet(    "QPushButton {background-color: rgba(255, 255, 255, 0);}" +
                                    "QPushButton:hover {background-color: rgba(25, 25, 25, 45);}")
        self.btn7.setStyleSheet(    "QPushButton {background-color: rgba(255, 255, 255, 0);}" +
                                    "QPushButton:hover {background-color: rgba(25, 25, 25, 45);}")
        self.btn8.setStyleSheet(    "QPushButton {background-color: rgba(255, 255, 255, 0);}" +
                                    "QPushButton:hover {background-color: rgba(25, 25, 25, 45);}")
        self.btn_menu.setStyleSheet(    "QPushButton {background-color: rgba(255, 255, 255, 0);}" +
                                    "QPushButton:hover {background-color: rgba(25, 25, 25, 45);}")

        self.label_left.setStyleSheet(   "QLabel {" +
                                        "color: black;" +
                                        "font-size: " + str(int(self.sts*1.2)) + "px;" +
                                        "padding-top: 5px;" +
                                        "padding-left: 5px;" +
                                        "padding-right: 5px;" +
                                        "padding-bottom: 5px;" +
                                        "background-color: rgba(255, 255, 255, 155);" +
                                        "border: 2px ;border-radius: 5px;}")
        #self.label_left.setFixedSize(int(screen.width()*0.2),int(screen.height()*0.7))


        self.label_usage.setStyleSheet(   "QLabel {" +
                                        "color: black;" +
                                        "font-size: " + str(self.sts) + "px;" +
                                        "padding-top: 5px;" +
                                        "padding-left: 5px;" +
                                        "padding-right: 5px;" +
                                        "padding-bottom: 5px;" +
                                        "background-color: rgba(255, 255, 255, 155);" +
                                        "border: 2px ;border-radius: 5px;}")


        self.label_time.setStyleSheet(   "QPushButton {" +
                                        "color: white;" +
                                        "font-size: " + str(int(self.sts*10)) + "px;" + 
                                        "text-align: centre;"+      
                                        "padding-top: 5px;" +
                                        "padding-left: 5px;" +
                                        "padding-right: 5px;" +
                                        "padding-bottom: 5px;" +
                                        "background-color: rgba(255, 255, 255, 2);" +
                                        "border: 2px ;border-radius: 5px;}")

        self.label_date.setStyleSheet(   "QPushButton {" +
                                        "color: black;" +
                                        "font-size: " + str(int(self.sts*3)) + "px;" + 
                                        "text-align: centre;"+      
                                        "padding-top: 5px;" +
                                        "padding-left: 5px;" +
                                        "padding-right: 5px;" +
                                        "padding-bottom: 5px;" +
                                        "background-color: rgba(255, 255, 255, 0);" +
                                        "border: 2px ;border-radius: 5px;}")

        self.cal_label.setStyleSheet(   "QLabel {" +
                                        "color: black;" +
                                        "font-size: " + str(int(self.bts*1.4)) + "px;" +
                                        "padding-top: 15px;" +
                                        "padding-left: 15px;" +
                                        "padding-right: 5px;" +
                                        "padding-bottom: 5px;" +
                                        "background-color: rgba(255, 255, 255, 155);" +
                                        "border: 2px ;border-radius: 5px;}")


        self.menu_widget.setStyleSheet( "QWidget {" +
                                        "color: black;" +
                                        "font-size: " + str(int(self.sts)) + "px;" +
                                        "padding-top: 15px;" +
                                        "padding-left: 15px;" +
                                        "padding-right: 5px;" +
                                        "padding-bottom: 5px;" +
                                        "background-color: rgba(255, 255, 255, 155);" +
                                        "border: 2px ;border-radius: 5px;}" +
                                        "QLabel {" +
                                        "background-color: rgba(255, 255, 255, 0);}")

        # Background transparenz                    
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("cp")
        self.update_ps()

        self.timer = QTimer()
        self.timer.setInterval(5000)  # 1 Sekunde Intervall
        self.timer.timeout.connect(self.update_ps)
        self.showFullScreen()   
        #self.show()
        
        self.installEventFilter(self)
        self.timer.start()      

    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            # Blockiere das WindowDeactivate-Ereignis, um zu verhindern, dass das Fenster den Fokus verliert
            os.system("wmctrl -a cp")
            return True
        return super().eventFilter(obj, event)


    def com(self, command):
        try:
            # Führe den übergebenen Befehl aus und erfasse die Ausgabe
            result = subprocess.check_output(command, shell=True).decode("UTF-8")

            return result
        except subprocess.CalledProcessError as e:
            #print(f"Befehl: {str(command)}\nFehler: {e} \n")
            return " "
    def check_com(self, cmds):
        ergebnis = ""
        for cmd in cmds:
            t=self.com(cmd)
            if t != " ":
                ergebnis = ergebnis + t
        return ergebnis



    def update_ps(self):
        cmd =  "ps -o pid,user,%cpu,%mem,comm -U $USER | sort -n -r -k3 | awk '{if " + '($2 != "root" && $5 != "ps" && $5 != "awk" && $5 != "x-mint-fullcont" && $1 != "PID" ) print $3,$4,$5' + "}' | head -n25"   
        #print(cmd)
        xs = str(self.com(cmd)).replace("b'","").replace("'","").replace(" ","\t").replace("\\n","\n")
        #print(xs)
        self.label_left.setText("CPU\tRAM\tProzess\n---------------------------------------------------------------\n"+xs)
        # update time
        xt = datetime.now().strftime("%H:%M\n%d/%m/%Y")
        self.label_time.setText(xt)
        self.label_time.adjustSize() 
        # update date
        xd = datetime.now().strftime("%d/%m/%Y")
        self.label_date.setText(xd)
        self.label_time.adjustSize() 

        max_ram = self.com("free -h | sed -n '2p' | awk '{print $2}'").replace("\n","")
        used_ram = self.com("free -h | sed -n '2p' | awk '{print $3}'").replace("\n","")
        cpu_used = int(self.update_cpu_usage()*10)/10
        self.label_usage.setText(f"CPU:\t\t{cpu_used}%\nSpeicher:\t{used_ram}B von {max_ram}B")
        
    def cpu_usage(self):
        self.cpu_prev_idle = self.cpu_idle
        self.cpu_prev_total= self.cpu_total
        self.cpu_idle = int(self.com("awk '/^cpu / {print $5}' /proc/stat"))
        self.cpu_total = int(self.com("awk '/^cpu / {print $2+$3+$4+$5+$6+$7+$8}' /proc/stat"))
        self.cpu_diff_idle = self.cpu_idle - self.cpu_prev_idle
        self.cpu_diff_total = self.cpu_total - self.cpu_total
        cpu_used = 100 * (self.cpu_diff_total - self.cpu_diff_idle) #/ self.cpu_diff_total 
        if self.cpu_diff_total > 0:
            cpu_used = 100 * (self.cpu_diff_total - self.cpu_diff_idle) / self.cpu_diff_total
        return cpu_used


    def read_cpu_stats(self):
        """Liest die CPU-Zeiten aus der Datei /proc/stat."""
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        parts = line.split()
        total_time = sum(int(part) for part in parts[1:8])
        idle_time = int(parts[4])
        return idle_time, total_time

    def initialize_cpu_stats(self):
        """Holt die initialen CPU-Werte und speichert sie in den Instanzvariablen."""
        self.prev_idle, self.prev_total = self.read_cpu_stats()

    def update_cpu_usage(self):
        """Aktualisiert die CPU-Werte, berechnet die CPU-Auslastung und speichert die neuen Werte."""
        curr_idle, curr_total = self.read_cpu_stats()
        
        diff_idle = curr_idle - self.prev_idle
        diff_total = curr_total - self.prev_total
        diff_usage = 100 * (diff_total - diff_idle) / diff_total
        
        # Aktualisiere die Instanzvariablen mit den aktuellen Werten
        self.prev_idle = curr_idle
        self.prev_total = curr_total
        
        return diff_usage
    def menu(self):
        if self.menu_open == False:
            calwidth = self.cal_label.width()
            self.menu_widget.setFixedWidth(calwidth)
            self.menu_widget.show()
            self.cal_label.hide()
            self.menu_open = True
        else:
            self.menu_widget.hide()
            self.cal_label.show()
            self.menu_open = False




    def taskmanager(self):
        self.hide()
        subprocess.Popen(self.tmcommand)
        app.exit()

    def terminal(self):
        self.hide()
        subprocess.Popen(self.termcommand)
        app.exit()
    def settings(self):
        self.hide()
        subprocess.Popen(self.settingscommand)
        app.exit()
    def reboot(self):
        self.hide()
        os.system(self.rebootcommand)
        app.exit()
    def logout(self):
        self.hide()
        os.system(self.logoutcommand)
        app.exit()
    def poweroff(self):
        self.hide()
        os.system(self.poweroffcommand)
        app.exit()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Tray()
    sys.exit(app.exec_())
