# RommePi
RommePi hilft beim Kartenspiel Rommé. Anstatt zu Klopfen drückt man einen Buzzer. Der erste Buzzer wird per LED signaisiert.

[Video zum Betrieb des RommePi](https://www.spitzlberger.de/wp-content/uploads/RommePi.mp4)  

![RommePi](https://raw.githubusercontent.com/spitzlbergerj/RommePi/main/images/RommePi-1.jpg)

weitere Fotos zum Aufbau unter [images](images)  

Aufgebaut ist das System wie folgt:
- Raspberry Pi Zero
- einige günstige Buzzer, an die Kabel gelötet wurden
- Steckbuchsen zum Anschließen der Buzzer
- LEDs zum Anzeigen, welcher Buzzer gedrückt wurde
- Status LED als RGB-LED
- Reset Taster
- USB-C Breakout Board
- ein Gehäuse, in das alles eingebaut wird

Das Python Script wird über die crontab von Root beim Booten gestartet

Funktion:
- Gerät fährt hoch
- Python wird gestartet
- Status LED wird grün = Gerät bereit
- Buzzer wird gedrückt = zugehörige LED leuchtet, Status LED wird rot
- nach 3 Sekunden wird System resetet, Status LED wird grün, nächster Buzzer kann gedrückt werden
- manuelles Reseten über den Reset Taster möglich
- Langes Drücken des Reset Tasters fährt das System runter

Raspberry Pi Zero
- Stromzufuhr über Lötkontakte 

LEDs
- Ansteuerung über MCP23017 I2C Expander
- Nutzung der Adafruit Library für MCP23017

crontab root  
@reboot python3 -u /home/pi/RommePi/romme-klopfen.py

