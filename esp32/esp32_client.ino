#include <WiFi.h>
#include <WiFiClient.h>

const char* ssid = "SEU_WIFI_SSID";
const char* password = "SUA_SENHA_WIFI";
const char* serverHost = "SEU_IP_DO_SERVIDOR_TCP";
const int serverPort = 5000; // Conexão com o servidor TCP [cite: 51]
const int ledPin = 2; // Exemplo de pino do LED

WiFiClient client;
unsigned long lastSendTime = 0;
const long sendInterval = 2000; // Envia a cada 2 segundos [cite: 52]

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  WiFi.begin(ssid, password);
  // Implementar espera por conexão Wi-Fi
  // Implementar conexão com servidor TCP
}

void loop() {
  // Lógica de reconexão
  if (!client.connected()) {
    // Tentar reconexão com o servidor TCP
    return;
  }

  // Envio periódico de dados simulados (a cada 2s) [cite: 52]
  if (millis() - lastSendTime >= sendInterval) {
    float temp = 25.0 + random(0, 100) / 100.0;
    float hum = 60.0 + random(0, 100) / 100.0;
    
    // JSON de exemplo: {"type": "data", "from": "esp32", "payload": {"temp": 25.3, "hum": 60}} [cite: 53]
    String json = "{\"type\": \"data\", \"from\": \"esp32\", \"payload\": {\"temp\": " + String(temp) + ", \"hum\": " + String(hum) + "}}";
    client.println(json);
    
    lastSendTime = millis();
  }

  // Recebimento de comandos
  if (client.available()) {
    String command = client.readStringUntil('\n');
    command.trim();
    
    // Tratamento de comandos 
    if (command == "led_on") {
      digitalWrite(ledPin, HIGH);
      client.println("LED ON");
    } else if (command == "led_off") {
      digitalWrite(ledPin, LOW);
      client.println("LED OFF");
    }
  }
}
