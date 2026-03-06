#include <Arduino.h>
#include <ps5Controller.h>

bool trianglePrev = false;
unsigned long lastTimeStamp = 0;
unsigned long lastTriangleToggleMs = 0;
uint8_t robotMode = 0;

void notify() {
    const bool triangleNow = ps5.Triangle();

    if (triangleNow && !trianglePrev && (millis() - lastTriangleToggleMs > 120)) {
        robotMode = (robotMode + 1) % 2;
        lastTriangleToggleMs = millis();
    }
    trianglePrev = triangleNow;

    if (millis() - lastTimeStamp > 100)
    {
        char message[100];
        sprintf(message, "%d,%d,%d", ps5.LStickX(), ps5.LStickY(), robotMode);
        Serial.print("DATA: ");
        Serial.print(message);
        Serial.println(" |END");
        lastTimeStamp = millis();
    }
}

void onConnect() {
    Serial.println("\nController connected");
}

void setup() {
    Serial.begin(115200);

    ps5.begin("10:18:49:C6:1C:68");
    ps5.attach(notify);
    ps5.attachOnConnect(onConnect);

    Serial.println("Waiting for PS5 Controller to connect...");
}

void loop() {

}
