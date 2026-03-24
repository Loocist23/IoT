#include <Bluepad32.h>

// Variables globales
ControllerPtr myController = nullptr;
bool trianglePrev = false;
unsigned long lastTriangleToggleMs = 0;
uint8_t robotMode = 0;

// Couleurs pour les modes
const uint8_t modeColors[2][3] = {
    {255, 0, 0},    // Mode 0: Rouge
    {0, 255, 0}     // Mode 1: Vert
};

// Callbacks Bluetooth
void onConnectedController(ControllerPtr ctl) {
    Serial.printf("Controller connected: %s\n", ctl->getModelName().c_str());
    myController = ctl;
    // Couleur initiale: Rouge (mode 0)
    ctl->setColorLED(255, 0, 0);
}

void onDisconnectedController(ControllerPtr ctl) {
    Serial.println("Controller disconnected");
    myController = nullptr;
}

// Traitement principal de la manette
void processController(ControllerPtr ctl) {
    // Gestion du bouton Triangle (Y dans Bluepad32)
    const bool triangleNow = ctl->y();

    if (triangleNow && !trianglePrev && (millis() - lastTriangleToggleMs > 120)) {
        // Toggle du mode robot (0 <-> 1)
        robotMode = (robotMode + 1) % 2;
        lastTriangleToggleMs = millis();

        // Changement de couleur LED selon le mode
        ctl->setColorLED(modeColors[robotMode][0], modeColors[robotMode][1], modeColors[robotMode][2]);

        // Vibration feedback
        ctl->playDualRumble(0, 200, 0x80, 0x40);

        Serial.printf("Mode changed to %d\n", robotMode);
    }
    trianglePrev = triangleNow;

    // Affichage du joystick (axe X et Y)
    Serial.printf("Joystick - X:%4d  Y:%4d  Mode:%d\n", ctl->axisX(), ctl->axisY(), robotMode);
}

// Arduino setup function
void setup() {
    Serial.begin(115200);
    Serial.printf("Firmware: %s\n", BP32.firmwareVersion());
    const uint8_t* addr = BP32.localBdAddress();
    Serial.printf("BD Addr: %2X:%2X:%2X:%2X:%2X:%2X\n", addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]);

    // Setup the Bluepad32 callbacks
    BP32.setup(&onConnectedController, &onDisconnectedController);

    // Désactiver le virtual device
    BP32.enableVirtualDevice(false);

    Serial.println("Waiting for PS5 Controller to connect...");
}

// Arduino loop function
void loop() {
    // Update Bluepad32
    BP32.update();

    // Traiter la manette si elle est connectée
    if (myController && myController->isConnected() && myController->hasData()) {
        processController(myController);
    }

    delay(20);
}
