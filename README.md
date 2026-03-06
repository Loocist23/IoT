# IoT - Robot

Ce projet utilise un ESP32 pour recevoir les données d'une manette PS5 (DualSense) et les transmettre via liaison série à un Raspberry Pi pour traitement.

## 📁 Structure du Projet dans `esp32ps5`

```
IoT/
├── esp32ps5/          # Code ESP32 - Réception des données de la manette PS5
│   ├── src/
│   │   └── main.cpp   # Code principal de l'ESP32
│   ├── platformio.ini # Configuration PlatformIO
│   ├── include/
│   ├── lib/
│   └── test/
└── raspberry/         # Code Raspberry Pi - Traitement des données (à venir)
```

> **Note** : Le dossier `raspberry/` sera ajouté ultérieurement pour contenir le code qui traitera les données envoyées par l'ESP32.

## 🔧 `esp32ps5` - Configuration et Utilisation

### Prérequis

- [PlatformIO](https://platformio.org/) installé
- ESP32 connecté via USB
- Manette PS5 (DualSense)

### Installation

#### 1. Initialiser le projet PlatformIO

Si le dossier `.pio` n'existe pas encore, créez-le avec :

```bash
cd esp32ps5
pio init
```

Cela créera automatiquement la structure nécessaire pour PlatformIO.

#### 2. Installer les dépendances

Les dépendances sont définies dans `platformio.ini` et seront installées automatiquement lors de la première compilation.

### Fonctionnalités

Le code ESP32 :
- Se connecte à une manette PS5 via Bluetooth
- Lit les données du joystick gauche (LStickX, LStickY)
- Gère un mode robot qui bascule avec le bouton Triangle
- Envoie les données formatées via Serial (115200 baud) toutes les 100ms

Format des données envoyées :
```
DATA: <LStickX>,<LStickY>,<RobotMode> |END
```

### Compilation et Upload

Pour compiler et téléverser le code sur l'ESP32 :

```bash
cd esp32ps5
pio run -t upload
```

### Lancer avec Monitoring Série

Pour téléverser le code ET ouvrir le moniteur série en une seule commande :

```bash
cd esp32ps5
pio run -t upload && pio device monitor
```

Le moniteur série affichera :
- Les messages de connexion de la manette
- Les données envoyées (format CSV)
- Les exceptions décodées en cas d'erreur (grâce à `esp32_exception_decoder`)

### Commandes Utiles

```bash
# Compiler sans téléverser
pio run

# Nettoyer le projet
pio run -t clean

# Moniteur série uniquement
pio device monitor

# Lister les ports disponibles
pio device list
```

## 🎮 Configuration de la Manette PS5

L'adresse MAC de la manette est configurée dans le code :
```cpp
ps5.begin("10:18:49:C6:1C:68");
```

Pour appairer votre manette :
1. Maintenez les boutons **PS + Share** pendant 3 secondes
2. La LED de la manette doit clignoter rapidement
3. L'ESP32 détectera automatiquement la manette

## 📡 Communication Série

- **Baudrate** : 115200
- **Format** : `DATA: X,Y,Mode |END`
  - `X` : Position du joystick gauche (axe X) [-128 à 127]
  - `Y` : Position du joystick gauche (axe Y) [-128 à 127]
  - `Mode` : Mode du robot [0 ou 1], basculé avec Triangle
