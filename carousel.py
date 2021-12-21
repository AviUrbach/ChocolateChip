from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QSlider, QGridLayout, QButtonGroup, QRadioButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QColor
import fileinput
import RPi.GPIO as g
import threading
import time

butid = 0

#updates signal to motor
#called every time the slider or buttons are modified
def update():
    global butid
    #print(butid, speed.value())
    if butid == 0:
        clockpwm.ChangeDutyCycle(0)
        counterpwm.ChangeDutyCycle(0)
    elif butid == 2:
        clockpwm.ChangeDutyCycle(0)
        counterpwm.ChangeDutyCycle(speed.value())
    else:
        clockpwm.ChangeDutyCycle(speed.value())
        counterpwm.ChangeDutyCycle(0)
    #print(speed.value())

#MOTOR PINS
clockpin = 24
counterpin = 22

#LED PINS
colorpins = [9,10,11]

g.setmode(g.BCM)
g.setup(clockpin, g.OUT)
g.setup(counterpin, g.OUT)

for pin in colorpins:
    g.setup(pin, g.OUT)

clockpwm = g.PWM(clockpin, 50)
counterpwm = g.PWM(counterpin, 50)
clockpwm.start(0)
counterpwm.start(0)

#Set up GUI
app = QApplication([])
window = QWidget()
layout = QGridLayout()
#app.setStyle('fusion')
app.setStyleSheet('\n'.join(fileinput.input('chipstyle.qss')))
app.setApplicationName("Chocolate Chip Carousel")
app.setWindowIcon(QIcon('cookie.png'))

labelfont = QFont('Courier New', 12)

#TITLE
title = QLabel('Welcome Aboard the ')
title.setFont(QFont('Courier New', 24))
layout.addWidget(title, 0, 0, 1, 2)

title2 = QLabel('<font color=\'red\'>Red Baron</font>')
font = QFont('times', 24)
font.setStyle(QFont.StyleItalic)
#font.setColor(QColor(255, 0, 0))
title2.setFont(font)
layout.addWidget(title2, 0, 2)

#DIRECTION (BUTTONS)
label = QLabel('\t\tLand:')
#label.setFont(labelfont)
layout.addWidget(label, 1, 0)

label = QLabel('\t\tTake Off!:')
#label.setFont(labelfont)
layout.addWidget(label, 2, 0)

direction = QButtonGroup()
def onClick(button):
    global butid
    butid = direction.id(button)
    #print(butid)
    update()
direction.buttonClicked.connect(onClick)

buttonFont = QFont('Courier New', 12)
stop = QRadioButton('Stop')
#stop.setFont(buttonFont)
stop.setChecked(True)
button = stop
clock = QRadioButton('Clockwise')
#clock.setFont(buttonFont)
counter = QRadioButton('Counterclockwise')
#counter.setFont(buttonFont)
direction.addButton(stop, id=0)
direction.addButton(clock, id=1)
direction.addButton(counter, id=2)
layout.addWidget(stop, 1, 1)
layout.addWidget(clock, 2, 1)
layout.addWidget(counter, 3, 1)

#SPEED (SLIDER)
label = QLabel('\t\tSet speed:')
#label.setFont(labelfont)
layout.addWidget(label, 4, 0)

speed = QSlider(Qt.Horizontal)
def onChange():
    update()
speed.valueChanged.connect(onChange)

speed.setMinimum(0)
speed.setMaximum(50) #Even this speed is a bit much for the planes
layout.addWidget(speed, 4, 1)
#layout.addWidget(QLabel('\t\t\t\t\t\t\t\t'), 4, 2)

#RUN THE LIGHTS
running = True

curlight = 0
def runlights():
    global curlight
    global running
    while running:
        curlight = (curlight + 1) % 3
        for i, pin in enumerate(colorpins):
            if i == curlight:
                g.output(pin, g.HIGH)
                #print("setting high", pin)
            else:
                g.output(pin, g.LOW)
        time.sleep(20 / (speed.value() + 10))

#Run lights on separate thread
thread = threading.Thread(target=runlights)
thread.start()

window.setLayout(layout)
window.show()
app.exec()

running = False
thread.join()

g.cleanup()
