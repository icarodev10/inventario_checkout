#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
#define BUZZER_PIN 8 

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.println("Passe a tag na frente do leitor:");
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    
    // Efeito sonoro: Frequência de 2000Hz por 100 milissegundos
    tone(BUZZER_PIN, 2000, 100); 
    
    Serial.print("ID da Tag Lido: ");
    for (byte i = 0; i < rfid.uid.size; i++) {
      Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
      Serial.print(rfid.uid.uidByte[i], HEX);
    }
    Serial.println();
    
    rfid.PICC_HaltA();
    delay(1500); // Delay um pouco maior para dar tempo de afastar a tag
  }
}