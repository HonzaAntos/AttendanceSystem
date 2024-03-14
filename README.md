# Dochazkový terminál 


Webové stránky docházkového terminálu [zde](https://terminal.techcrowd.cz/)


## Popis
Vývoj a implementace docházkového terminálu pro systém evidence docházky. Projekt zahrnuje ověřování uživatelů pomocí RFID a kamery, vytvoření GUI, odesílání dat na server, vzdálenou správu a komunikace se zákazníkem

![](https://github.com/HonzaAntos/AttendanceSystem/assets/112206462/2f3110b5-fb58-4b11-afe8-03e63e9dbb1e)

## Stavový diagram

![state_machine_diagram_attendance_terminal](https://github.com/HonzaAntos/AttendanceSystem/assets/112206462/9e4932f6-370b-4675-951b-83e81b7a2eff)

Stavový automat se skládá celkově ze sedmi stavů, konkrétně se jedná o stavy:
•	Initial – zobrazení inicializační obrazovky
•	State_a – autorizace zaměstnance (POST api_terminal/authorization)
•	State_b – zobrazení hlavní obrazovky
•	State_c – provedení akce docházky (POST api/terminal/action)
•	State_d – zobrazení vyskakovací obrazovky
•	State_e – odhlášení zaměstnance (DELETE api/terminal/logout)
•	State_f – zobrazení chybové obrazovky

## Flow Diagram
![algorithm_communication_terminal_X_server](https://github.com/HonzaAntos/AttendanceSystem/assets/112206462/fbe94750-c79b-48b9-99f0-ecd0142d3d8f)

