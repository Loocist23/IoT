from pyb import Pin, Timer, LED
import pyb

# Configurer les broches Y3/Y4 en mode AF pour Timer 4
pin_in1 = Pin('Y3', mode=Pin.ALT, alt=2)  # AF2 pour Timer 4, Channel 3
pin_in2 = Pin('Y4', mode=Pin.ALT, alt=2)  # AF2 pour Timer 4, Channel 4

# Initialiser Timer 4 en mode PWM
tim = Timer(4, freq=1000)  # Timer 4, fréquence 1 kHz

# Configurer les canaux PWM
ch3 = tim.channel(3, Timer.PWM, pin=pin_in1)  # Canal 3 pour Y3
ch4 = tim.channel(4, Timer.PWM, pin=pin_in2)  # Canal 4 pour Y4

# Initialiser la LED intégrée (LED 1 = rouge)
led = LED(1)

# Vitesse maximale limitée à 70%
VITESSE_MAX = 70

def clignoter_led_confirme():
    led.off()
    pyb.delay(100)
    led.on()
    pyb.delay(100)
    led.off()

def moteur_avant(vitesse=VITESSE_MAX):
    ch3.pulse_width_percent(vitesse)
    ch4.pulse_width_percent(0)
    led.on()  # LED allumée pendant que le moteur tourne
    print("Moteur en avant à {}%".format(vitesse))

def moteur_arriere(vitesse=VITESSE_MAX):
    ch3.pulse_width_percent(0)
    ch4.pulse_width_percent(vitesse)
    led.on()  # LED allumée pendant que le moteur tourne
    print("Moteur en arrière à {}%".format(vitesse))

def moteur_arret():
    ch3.pulse_width_percent(0)
    ch4.pulse_width_percent(0)
    led.off()  # LED éteinte quand le moteur est arrêté
    print("Moteur arrêté")

print("Contrôle du moteur via console :")
print("'a' = avant ({}%), 'r' = arrière, 's' = stop, 'q' = quitter".format(VITESSE_MAX))

while True:
    cmd = input("Entrez une commande : ").strip().lower()

    if cmd == 'a':
        moteur_avant()
        clignoter_led_confirme()
    elif cmd == 'r':
        moteur_arriere()
        clignoter_led_confirme()
    elif cmd == 's':
        moteur_arret()
        clignoter_led_confirme()
    elif cmd == 'q':
        moteur_arret()
        print("Fin du programme")
        break
    else:
        print("Commande invalide. Utilisez 'a', 'r', 's' ou 'q'.")

