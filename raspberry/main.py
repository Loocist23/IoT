from machine import Pin, UART
import time

# Broches moteur et LED
in1 = Pin(18, Pin.OUT)  # D18 = IN1
in2 = Pin(19, Pin.OUT)  # D19 = IN2
led = Pin(2, Pin.OUT)   # LED intégrée

# UART (D16=RX, D17=TX)
uart = UART(2, baudrate=230400, rx=16, tx=17)

CMD_IDLE = 0b0000
CMD_FORWARD = 0b0001
CMD_BACKWARD = 0b0010
CMD_LEFT = 0b0100
CMD_RIGHT = 0b0110
VALID_COMMANDS = (CMD_IDLE, CMD_FORWARD, CMD_BACKWARD, CMD_LEFT, CMD_RIGHT)

FAILSAFE_MS = 150

last_valid_rx_ms = time.ticks_ms()
last_applied_frame = -1
failsafe_active = False


def moteur_stop():
    in1.off()
    in2.off()
    led.off()


def appliquer_commande(commande):
    if commande == CMD_IDLE:
        moteur_stop()
    elif commande == CMD_FORWARD:
        in1.on()
        in2.off()
        led.on()
    elif commande == CMD_BACKWARD:
        in1.off()
        in2.on()
        led.on()
    elif commande == CMD_LEFT:
        in1.on()
        in2.off()
        led.on()
    elif commande == CMD_RIGHT:
        in1.off()
        in2.on()
        led.on()


def traiter_commande(raw_data):
    # Keep only the 5 useful bits from the protocol.
    data = raw_data & 0b11111
    mode = (data >> 4) & 0b1
    commande = data & 0b01111

    if commande not in VALID_COMMANDS:
        return False, data, mode

    appliquer_commande(commande)
    return True, data, mode


print("ESP32 recepteur pret (UART)")

while True:
    now = time.ticks_ms()

    # Read all pending bytes and keep only the newest one.
    if uart.any():
        raw = uart.read()
        if raw:
            ok, data, mode = traiter_commande(raw[-1])
            if ok:
                last_valid_rx_ms = now
                failsafe_active = False
                if data != last_applied_frame:
                    print("Recu: {:05b} (Mode {})".format(data, "auto" if mode else "manuel"))
                    last_applied_frame = data

    # Safety: stop motor if link is lost.
    if time.ticks_diff(now, last_valid_rx_ms) > FAILSAFE_MS and not failsafe_active:
        moteur_stop()
        failsafe_active = True
        print("Failsafe: aucune trame valide")

    time.sleep_ms(2)
