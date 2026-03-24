# IoT - Robot

Ce projet utilise un ESP32 pour lire les donnees d'une manette PS5 (DualSense) via Bluetooth, puis les exposer sur la liaison serie.

## Structure du projet

```text
IoT/
├── esp32ps5/
│   └── Controller/
│       └── Controller.ino   # Firmware ESP32 (Bluepad32 + lecture manette)
├── pyboard/
│   └── main.py              # Script MicroPython de controle moteur (prototype)
└── raspberry/               # A venir: code Raspberry Pi qui recevra/traitera la data ESP32
```

Note: le dossier `raspberry/` n'est pas encore present dans ce depot. Il sera ajoute a la racine pour la partie reception et traitement des donnees envoyees par l'ESP32.

## Partie ESP32 (`esp32ps5`)

PlatformIO a ete retire de ce projet. Le firmware est maintenant maintenu comme sketch Arduino (`Controller.ino`).

### Prerequis

- Arduino IDE 2.x ou `arduino-cli`
- Carte ESP32 (package cartes ESP32 installe)
- Bibliotheque `Bluepad32`
- ESP32 connecte en USB
- Manette PS5 (DualSense)

### Flash du firmware (Arduino IDE)

1. Ouvrir `esp32ps5/Controller/Controller.ino`
2. Aller dans **Arduino IDE -> Preferences** puis ajouter dans **Additional Boards Manager URLs**:

```text
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
https://raw.githubusercontent.com/ricardoquesada/esp32-arduino-lib-builder/master/bluepad32_files/package_esp32_bluepad32_index.json
```

3. Ouvrir **Tools -> Board** et selectionner **DOIT ESP32 DEVKIT V1** depuis **esp32_bluepad32**
4. Selectionner le bon port dans **Tools -> Port**
5. Regler:
   - **Flash Frequency**: `40MHz`
   - **Upload Speed**: `115200`
6. Cliquer sur Upload

### Flash du firmware (arduino-cli)

```bash
cd esp32ps5/Controller
arduino-cli board list
arduino-cli compile --fqbn <votre_fqbn_esp32> .
arduino-cli upload -p <votre_port_serie> --fqbn <votre_fqbn_esp32> .
```

### Monitor serie

```bash
arduino-cli monitor -p <votre_port_serie> -c baudrate=115200
```

## Comportement du firmware ESP32

Le code dans `Controller.ino`:
- Initialise Bluepad32 et attend une manette
- Detecte la connexion/deconnexion de la DualSense
- Lit le joystick gauche (`axisX`, `axisY`)
- Change le mode robot avec le bouton Triangle (`y()` dans Bluepad32)
- Change la LED de la manette selon le mode
- Envoie des traces serie a 115200 bauds

Exemples de traces:

```text
Controller connected: DualSense Wireless Controller
Mode changed to 1
Joystick - X:  12  Y: -45  Mode:1
```

## Appairage de la manette PS5

1. Maintenir **PS + Share** pendant environ 3 secondes
2. La LED de la manette clignote rapidement
3. L'ESP32 la detecte automatiquement via Bluepad32

## Cablage UART (ESP32 -> carte receptrice)

Utiliser UART2 de l'ESP32 DevKit V1:
- `D17 (TX2)` ESP32 -> `RX` carte receptrice
- `D16 (RX2)` ESP32 <- `TX` carte receptrice
- `GND` ESP32 <-> `GND` carte receptrice (**masse commune obligatoire**)

Le firmware emet la trame de commande sur `Serial2` a `115200` bauds.

### Protocole de communication (5 bits)

- `Bit 4`: Mode (`0` = normal, `1` = alternatif)
- `Bits 0-3`: Direction

| Bit4 | Bit3 | Bit2 | Bit1 | Bit0 | Signification |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | Idle (moteur arrete) |
| 0 | 0 | 0 | 0 | 1 | Avant |
| 0 | 0 | 0 | 1 | 0 | Arriere |
| 0 | 0 | 1 | 0 | 0 | Gauche |
| 0 | 0 | 1 | 1 | 0 | Droite |
| 1 | x | x | x | x | Mode alternatif (ex: vitesse reduite) |

Exemples:
- `00001` = Avant en mode normal
- `10001` = Avant en mode alternatif

## Anciennes commandes PlatformIO

Les commandes suivantes ne sont plus applicables dans ce projet:

```bash
pio run -t upload
pio run -t upload && pio device monitor
pio init
```
