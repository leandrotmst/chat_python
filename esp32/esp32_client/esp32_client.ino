// Inclua as bibliotecas necessárias
#include <WiFi.h>
#include <WiFiClient.h>
#include <ArduinoJson.h> // Será necessário instalar esta biblioteca (ex: via Gerenciador de Bibliotecas)

// Configurações Wi-Fi e Servidor
const char* ssid = "Quarto Leandro convidados";
const char* password = "Bito2211";
const char* host = "192.168.0.131"; // IP do seu PC rodando server_tcp.py
const int port = 5000;          // Porta do servidor TCP [cite: 51]

// Objeto cliente TCP
WiFiClient client;

// Variável para controle de tempo (enviar a cada 2 segundos)
unsigned long lastSendTime = 0;
const long interval = 2000; // 2000 ms = 2 segundos 

// Configuração do LED
const int LED_PIN = 2; // O pino do LED embutido no ESP32 costuma ser o 2

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // LED começa apagado [cite: 56]
  
  // Conexão Wi-Fi
  Serial.print("Conectando-se a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Conectado!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  if (!client.connected()) {
    Serial.println("Tentando reconectar ao servidor...");
    if (client.connect(host, port)) {
      Serial.println("Reconectado!");
    } else {
      Serial.print("Falha na reconexão, rc=");
      Serial.print(client.connected());
      Serial.println(" aguardando 5 segundos...");
      delay(5000);
    }
  }
}

void sendData() {
  // Simula dados (ex: temperatura e umidade) [cite: 53]
  float temp = 25.0 + sin(millis() / 50000.0) * 2.0;
  float hum = 60.0 + cos(millis() / 30000.0) * 5.0;

  // Cria o objeto JSON
  StaticJsonDocument<256> doc;
  doc["type"] = "data";
  doc["from"] = "esp32";
  
  // Cria o payload
  JsonObject payload = doc.createNestedObject("payload");
  payload["temp"] = temp;
  payload["hum"] = hum;

  // Serializa (converte o JSON em string)
  String jsonString;
  serializeJson(doc, jsonString);

  // Envia os dados
  client.println(jsonString); // client.println() é conveniente para TCP
  Serial.print("Dados enviados: ");
  Serial.println(jsonString);
}

void handleCommands() {
  if (client.available()) {
    String command = client.readStringUntil('\n'); // Lê a linha completa
    command.trim(); // Remove espaços em branco
    
    Serial.print("Comando recebido: ");
    Serial.println(command);
    
    // Verifica os comandos [cite: 55, 56]
    if (command.equalsIgnoreCase("led_on")) {
      digitalWrite(LED_PIN, HIGH);
      client.println("ESP32: LED ACESO");
    } else if (command.equalsIgnoreCase("led_off")) {
      digitalWrite(LED_PIN, LOW);
      client.println("ESP32: LED APAGADO");
    }
    // Você pode adicionar uma resposta padrão
    client.println("ESP32: Comando processado.");
  }
}

void loop() {
  reconnect(); // Garante que a conexão TCP esteja ativa
  
  if (client.connected()) {
    // 1. Envio de dados periodicamente
    unsigned long currentMillis = millis();
    if (currentMillis - lastSendTime >= interval) {
      lastSendTime = currentMillis;
      sendData();
    }
    
    // 2. Recebimento e tratamento de comandos
    handleCommands();
  }
}