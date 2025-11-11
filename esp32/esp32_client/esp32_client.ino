#include <WiFi.h>
#include <WiFiClient.h>

// Substitua pelo seu SSID, Senha e o IP do seu PC (192.168.0.198)
const char* ssid = "Quarto Leandro convidados";
const char* password = "Bito2211";
const char* serverHost = "192.168.0.198";
const int serverPort = 5000; // Porta do Servidor TCP (server_tcp.py)

// Verifique qual pino GPIO seu LED usa. O 2 é comum em placas ESP32 Dev.
const int ledPin = 2; 

WiFiClient client;
unsigned long lastSendTime = 0;
const long sendInterval = 2000; // Envia a cada 2 segundos [cite: 52]

void connectWiFi() {
  Serial.print("Conectando ao WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi conectado! IP local: ");
  Serial.println(WiFi.localIP());
}

void connectServer() {
  if (client.connect(serverHost, serverPort)) {
    Serial.print("Conectado ao servidor TCP: ");
    Serial.println(serverHost);
  } else {
    Serial.println("Falha na conexao com o servidor.");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); // LED apagado inicialmente [cite: 56]

  connectWiFi();
  connectServer();
}

void sendData() {
  // Dados simulados [cite: 52]
  float temp = random(200, 300) / 10.0; // 20.0 a 30.0
  float hum = random(500, 700) / 10.0;   // 50.0 a 70.0
  
  // JSON formatado conforme o requisito [cite: 53]
  String json = "{\"type\": \"data\", \"from\": \"esp32\", \"payload\": {\"temp\": " + String(temp) + ", \"hum\": " + String(hum) + "}}";
  
  client.println(json); // Envia a string (linha) para o servidor
  Serial.print("Dados enviados: ");
  Serial.println(json);
}

void handleCommands() {
  if (client.available()) {
    String command = client.readStringUntil('\n');
    command.trim();
    
    Serial.print("Comando recebido: ");
    Serial.println(command);
    
    // Processa comandos [cite: 55, 56]
    if (command == "led_on") {
      digitalWrite(ledPin, HIGH);
      client.println("ESP32: LED ACESO");
      Serial.println("LED aceso.");
    } else if (command == "led_off") {
      digitalWrite(ledPin, LOW);
      client.println("ESP32: LED APAGADO");
      Serial.println("LED apagado.");
    } else {
      // Resposta padrão para comandos desconhecidos
      client.println("ESP32: Comando desconhecido.");
    }
  }
}

void loop() {
  // Garante que o Wi-Fi esteja conectado
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado. Tentando reconectar...");
    connectWiFi();
    return;
  }
  
  // Gerencia a reconexão TCP
  if (!client.connected()) {
    Serial.println("Conexão TCP perdida. Tentando reconectar...");
    client.stop(); // Fecha a conexão antiga
    connectServer();
    // Se a reconexão falhar, retorna para tentar de novo no próximo loop
    if (!client.connected()) {
        delay(500);
        return;
    }
  }

  // Envio periódico de dados
  if (millis() - lastSendTime >= sendInterval) {
    sendData();
    lastSendTime = millis();
  }

  // Recebimento e processamento de comandos
  handleCommands();
}