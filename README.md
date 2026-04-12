# IoT - Robot

Ce projet utilise un ESP32 pour lire les donnees d'une manette PS5 (DualSense) via Bluetooth, puis les exposer sur la liaison serie. La Raspberry Pi reçoit ces données via UART et contrôle les moteurs via ROS2.

## Structure du projet

```text
IoT/
├── esp32ps5/
│   └── Controller/
│       └── Controller.ino   # Firmware ESP32 (Bluepad32 + lecture manette)
├── raspberry/
│   └── robot_autonome_ws/   # Workspace ROS2 pour la Raspberry Pi
│       ├── src/
│       │   ├── uart_reader/      # Nœud pour lire les données UART de l'ESP32
│       │   ├── motor_controller/ # Nœud pour contrôler les moteurs via DRV8833
│       │   ├── brain/            # Nœud pour la machine à états et la logique de contrôle
│       │   ├── lidar_node/       # Nœud pour le LiDAR RPLIDAR
│       │   └── launch/           # Fichiers de lancement ROS2
├── install_ros2_humble.sh    # Script d'installation de ROS2 Humble
└── build_and_launch.sh      # Script pour construire et lancer les nœuds ROS2
```

> **Note**: Le dossier `raspberry/` contient maintenant un workspace ROS2 complet pour gérer la communication UART, le contrôle des moteurs, et l'intégration du LiDAR.

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

## Cablage UART (ESP32 -> Raspberry Pi)

Utiliser UART2 de l'ESP32 DevKit V1:
- `D17 (TX2)` ESP32 -> `RX` Raspberry Pi (ex: `/dev/ttyS0`)
- `D16 (RX2)` ESP32 <- `TX` Raspberry Pi
- `GND` ESP32 <-> `GND` Raspberry Pi (**masse commune obligatoire**)

Le firmware emet la trame de commande sur `Serial2` a `115200` bauds.

### Protocole de communication (5 bits)

- `Bit 4`: Mode (`0` = manuel, `1` = autonome)
- `Bits 0-3`: Direction

| Bit4 | Bit3 | Bit2 | Bit1 | Bit0 | Signification |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | Idle (moteur arrete) |
| 0 | 0 | 0 | 0 | 1 | Avant |
| 0 | 0 | 0 | 1 | 0 | Arriere |
| 0 | 0 | 1 | 0 | 0 | Gauche |
| 0 | 0 | 1 | 1 | 0 | Droite |
| 1 | x | x | x | x | Mode autonome (LiDAR actif) |

Exemples:
- `00001` = Avant en mode manuel
- `10001` = Avant en mode autonome

## Partie Raspberry Pi (`raspberry/`)

La Raspberry Pi exécute un workspace ROS2 (`robot_autonome_ws`) pour gérer la communication UART, le contrôle des moteurs, et l'intégration du LiDAR.

### Architecture ROS2

```text
[ESP32] --UART--> [uart_reader] --/robot/mode_and_direction--> [brain]
                                                           |
                                                           v
                                                     [motor_controller] --GPIO--> [DRV8833]
                                                           |
                                                           v
                                                     [lidar_node] <--/scan-- [RPLIDAR]
```

### Nœuds ROS2

1. **uart_reader**: Lit les données UART de l'ESP32 et publie sur `/robot/mode_and_direction`.
2. **motor_controller**: Contrôle les moteurs via DRV8833, écoute `/robot/motor_cmd`.
3. **brain**: Machine à états, gère la logique de bascule entre modes (manuel/autonome).
4. **lidar_node**: Intègre le LiDAR RPLIDAR, publie sur `/scan`.

### Installation de ROS2 Humble

Exécutez le script d'installation pour configurer ROS2 Humble et les dépendances:

```bash
chmod +x install_ros2_humble.sh
sudo ./install_ros2_humble.sh
```

Le script installe:
- ROS2 Humble Desktop
- `rplidar_ros` pour le LiDAR
- `pyserial` pour la communication UART
- `colcon` pour construire les packages ROS2

### Construction et lancement des nœuds

Utilisez le script `build_and_launch.sh` pour construire le workspace et lancer les nœuds:

```bash
chmod +x build_and_launch.sh
./build_and_launch.sh
```

Le script:
1. Vérifie que ROS2 est installé et sourcé.
2. Construit le workspace avec `colcon build`.
3. Lance les nœuds dans des terminaux séparés (si `gnome-terminal` est installé).

### Vérification des topics ROS2

Pour vérifier que les nœuds communiquent correctement:

```bash
ros2 topic list
ros2 topic echo /robot/mode_and_direction
ros2 topic echo /robot/motor_cmd
```

### Arrêt des nœuds

Pour arrêter tous les nœuds:

```bash
pkill -f "ros2 run"
```

### Configuration du LiDAR RPLIDAR

Le LiDAR est configuré pour publier sur `/scan`. Pour visualiser les données:

```bash
rviz2
```

Dans RViz2, ajoutez un `LaserScan` et sélectionnez le topic `/scan`.

### Configuration des moteurs (DRV8833)

Les broches GPIO utilisées pour le DRV8833:

| DRV8833 | Raspberry Pi GPIO |
|---------|-------------------|
| IN1     | GPIO 17           |
| IN2     | GPIO 18           |
| IN3     | GPIO 22           |
| IN4     | GPIO 23           |

### Configuration UART sur la Raspberry Pi

1. Activez l'UART dans `/boot/config.txt`:

```text
enable_uart=1
```

2. Désactivez le terminal série:

```bash
sudo raspi-config
```

- **Interface Options** -> **Serial** -> **Non** pour le shell, **Oui** pour le matériel.

3. Vérifiez le port UART:

```bash
ls /dev/tty*
```

Le port par défaut est `/dev/ttyS0`.

## Anciennes commandes PlatformIO

Les commandes suivantes ne sont plus applicables dans ce projet:

```bash
pio run -t upload
pio run -t upload && pio device monitor
pio init
```
