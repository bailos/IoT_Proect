#include "DHT.h"

// Paramètres DHT11
#define DHTTYPE DHT11
#define DHTPIN  2
DHT dht(DHTPIN, DHTTYPE);
#define Red_LED 12
#define Green_LED 11
#define Buzzer 10

// Reception commande
String commande = "";
String commande_precedente = "";

// Gestion du temps
unsigned long t0 = 0;
unsigned long intervalle = 0;

void setup() {
  Serial.begin(9600);
  dht.begin();
  // A compléter
  pinMode(Red_LED, OUTPUT);
  pinMode(Green_LED, OUTPUT);
  pinMode(Buzzer, OUTPUT);
  digitalWrite(Green_LED, HIGH);
}

void loop() {
  // Réception commande (alerte en cas de risque)
  commande = Serial.readString();
  commande.trim();
  delay(10);

  if (commande.length() <= 0 ){
    commande = commande_precedente;
  }

  if (commande == "ASTHME"){
    digitalWrite(Red_LED, HIGH);
    digitalWrite(Buzzer, HIGH);
    digitalWrite(Green_LED, LOW);

    commande_precedente = commande;
  }
  if (commande == "HYPERTENSION"){
    digitalWrite(Red_LED, HIGH);
    digitalWrite(Buzzer, HIGH);
    digitalWrite(Green_LED, LOW);

    commande_precedente = commande;
  }
  if (commande == "AVC"){
    digitalWrite(Red_LED, HIGH);
    digitalWrite(Buzzer, HIGH);
    digitalWrite(Green_LED, LOW);

    commande_precedente = commande;
  }
  else{  // NO RISK
    digitalWrite(Red_LED, LOW);
    digitalWrite(Buzzer, LOW);
    digitalWrite(Green_LED, HIGH);
    commande_precedente = commande;
  }

  // A chaque intervalle de 60s
  intervalle = millis() - t0;
  if (intervalle >= 60000){
    t0 = millis();

    float temperature = dht.readTemperature(); 
    float humidite = dht.readHumidity();
    
    if (isnan(temperature) || isnan(humidite)) {
      Serial.println("Failed to read from DHT sensor");
      delay(5000);
      return;
    }
    String serial_data = "#" + String(humidite) + "," + String(temperature);
    Serial.println(serial_data);
    // delay(10000);
}

  }

