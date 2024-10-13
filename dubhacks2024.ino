const int segmentPins[7] = {2, 3, 4, 5, 6, 7, 8};  // Segment A to G
const int buzzerPin = 9;

// Segment patterns for each letter
const int n[7] = {HIGH, HIGH, HIGH, LOW, HIGH, HIGH, LOW};
const int o[7] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, LOW};
const int s[7] = {HIGH, LOW, HIGH, HIGH, LOW, HIGH, HIGH};
const int l[7] = {LOW, LOW, LOW, HIGH, HIGH, HIGH, LOW};
const int e[7] = {HIGH, LOW, LOW, HIGH, HIGH, HIGH, HIGH};
const int p[7] = {HIGH, HIGH, LOW, LOW, HIGH, HIGH, HIGH};
const int i[7] = {LOW, HIGH, HIGH, LOW, LOW, LOW, LOW};
const int g[7] = {HIGH, HIGH, HIGH, HIGH, LOW, HIGH, HIGH};

// Segment pattern to turn OFF all segments
const int off[7] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW};

// Flag to track if the message is displayed or buzzer is sounded once already
bool messageDisplayed = false;
bool buzzerHeard = false;

void setup() {
  // Initialize pins as outputs and start with segments off
  for (int pin = 0; pin < 7; pin++) {
    pinMode(segmentPins[pin], OUTPUT);
    digitalWrite(segmentPins[pin], LOW);
  }
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(9600);  // Start serial communication
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();  // Read signal from Python

    if (signal == '1' && !messageDisplayed) {
      displayMessage();  // Display the "no sleeping" message once
      messageDisplayed = true;  // Set flag to indicate message has been displayed
    } else if (signal == '2' && !buzzerHeard) {
      soundBuzzer();  // buzzer sound one time
      buzzerHeard = true;  // set flag
    } else if (signal == '0') {
      displayLetter(off);  // Turn off the display if the signal is 0
      noTone(buzzerPin);   // Stop the buzzer
      messageDisplayed = false;  // Reset flags
      buzzerHeard = false;
    }
  }
}

void displayMessage() {
  // Display "no sleeping" letter by letter, with a delay between each
  for (int i = 0; i < 7; i++) {
    if (Serial.available() > 0 && Serial.read() == '0') return;  // Stop if signal is 0
    displayLetter(n); delay(1000);
    displayLetter(o); delay(1000);
    displayLetter(off); delay(500);  // Clear between words

    displayLetter(s); delay(1000);
    displayLetter(l); delay(1000);
    displayLetter(e); delay(1000);
    displayLetter(e); delay(1000);
    displayLetter(p); delay(1000);
    displayLetter(i); delay(1000);
    displayLetter(n); delay(1000);
    displayLetter(g); delay(1000);

    displayLetter(off);  // Turn off display after message
  }
}

void displayLetter(const int pattern[7]) {
  // Update the segments with the corresponding pattern
  for (int pin = 0; pin < 7; pin++) {
    digitalWrite(segmentPins[pin], pattern[pin]);
  }
}

void soundBuzzer() {
  // Sound buzzer with check for signal change
  for (int i = 0; i < 10; i++) {  // Repeat 10 times for longer beep
    if (Serial.available() > 0 && Serial.read() == '0') return;  // Stop if signal is 0
    tone(buzzerPin, 1000);
    delay(50);  // Short beep
    noTone(buzzerPin);
    delay(100);
  }
}
