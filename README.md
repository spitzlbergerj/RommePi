# RommePi
RommePi hilft beim Spiel Romme. Anstatt zu Klopfen drückt man einen Buzzer. der erste Buzzer wird per LED signaisiert.

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
- Statsu LED wird grün = Gerät bereit
- Buzzer wird gedrückt = zugehörige LED leuchtet, Status LED wird rot
- nach 3 Sekunden wird System resetet, Status LED wird grün, nächster Buzzer kann gedrückt werden
- manuelles Reseten über den Reset Taster möglich
- Langes Drücken des Reset Tasters fährt das System runter
