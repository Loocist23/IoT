#include <Bluepad32.h>

// UART2 pins on ESP32 DevKit V1 (D16/D17)
static const int UART2_RX_PIN = 16;
static const int UART2_TX_PIN = 17;
static const uint32_t UART_BAUD = 115200;

// 5-bit protocol constants (bit4 = mode, bits0..3 = direction)
static const uint8_t DIR_IDLE = 0b0000;
static const uint8_t DIR_FORWARD = 0b0001;
static const uint8_t DIR_BACKWARD = 0b0010;
static const uint8_t DIR_LEFT = 0b0100;
static const uint8_t DIR_RIGHT = 0b0110;

static const int AXIS_DEADZONE = 50;

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

uint8_t computeDirectionNibble(int x, int y) {
    const bool xActive = abs(x) >= AXIS_DEADZONE;
    const bool yActive = abs(y) >= AXIS_DEADZONE;

    if (!xActive && !yActive) {
        return DIR_IDLE;
    }

    // Keep only one direction: dominant axis wins.
    if (yActive && (!xActive || abs(y) >= abs(x))) {
        return (y < 0) ? DIR_FORWARD : DIR_BACKWARD;
    }

    return (x < 0) ? DIR_LEFT : DIR_RIGHT;
}

uint8_t buildFrame5bit(uint8_t mode, uint8_t directionNibble) {
    const uint8_t modeBit = (mode & 0x01) << 4;
    return modeBit | (directionNibble & 0x0F);
}

void sendControlFrame(ControllerPtr ctl) {
    const uint8_t direction = computeDirectionNibble(ctl->axisX(), ctl->axisY());
    const uint8_t frame = buildFrame5bit(robotMode, direction);

    // Raw binary frame over UART2 (0..31)
    Serial2.write(frame);

    // Keep USB serial logs for monitoring.
    Serial.printf(
        "Joystick - X:%4d  Y:%4d  Mode:%d  Frame:0x%02X\n",
        ctl->axisX(),
        ctl->axisY(),
        robotMode,
        frame
    );
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

    sendControlFrame(ctl);
}

// Arduino setup function
void setup() {
    Serial.begin(115200);
    Serial2.begin(UART_BAUD, SERIAL_8N1, UART2_RX_PIN, UART2_TX_PIN);
    Serial.println("UART2 ready on RX=16 TX=17 (common GND required)");
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
