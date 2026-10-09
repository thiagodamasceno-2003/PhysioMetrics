#include "LIS3DHTR.h"
#include <Wire.h>
#include <WiFiS3.h>

LIS3DHTR<TwoWire> LIS; //I2C
#define WIRE Wire

// Configurações do Access Point (AP)
const char* ssid = "ArduinoAP";      
const char* password = "12345678";  

unsigned long lastSendTime = 0;

WiFiServer server(23);  // Servidor na porta 23 (HTTP)

void setup() {
  
    LIS.begin(WIRE, 0x19); // inicia ligação I2C
    delay(100);

    // Configura parâmetros de captura de dados
    LIS.setFullScaleRange(LIS3DHTR_RANGE_4G);
    LIS.setOutputDataRate(LIS3DHTR_DATARATE_100HZ);
    LIS.setHighSolution(true); 

    // Conecção wifi
    WiFi.beginAP(ssid, password); // Cria ponto de acesso
    server.begin(); // Inicia o servidor

}
void loop() {
  // Aguarda um cliente se conectar
  WiFiClient client = server.available();

  if (client){
    if (!LIS) {
        client.println("Acelerômetro não conectado.");
        while (1);
        return;
    }

    unsigned long currentTime = millis();
    if (currentTime - lastSendTime >= 33) { // 1000ms/30 ≈ 33ms
    lastSendTime = currentTime;

    //3 axis
    client.print(LIS.getAccelerationX()); client.print(",");
    client.print(LIS.getAccelerationY()); client.print(",");
    client.println(LIS.getAccelerationZ());

    }
    // delay(5);
  }
}

