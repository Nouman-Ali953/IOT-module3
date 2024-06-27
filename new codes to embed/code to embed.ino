#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SoftwareSerial.h>

#define OLED_RESET 4
Adafruit_SSD1306 display(OLED_RESET);

SoftwareSerial bluetoothSerial(0, 1); // RX, TX

void setup() {
  Serial.begin(9600);
  bluetoothSerial.begin(9600);
  
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  
  display.display();
  delay(2000);
  display.clearDisplay();
}

void loop() {
  if (bluetoothSerial.available() > 0) {
    String data = bluetoothSerial.readStringUntil('\n');
    display.clearDisplay();
    display.setTextSize(1); // Set text size to small
    display.setTextColor(SSD1306_WHITE); // Set text color to default
    display.setTextWrap(false);
    
    int x = 2; // Start at the left side of the display
    int y = 0; // Start at the top of the display
    
    int letterSpacing = 2; // Space between letters
    
    int line = 0; // To keep track of the line number
    
    for (int i = 0; i < data.length(); i++) {
      if (data[i] == ',') {
        // Move to the next line
        y += 8;
        x = 2; // Reset x to start from the left side
        line++; // Increment line number
      } else if (data[i] == '\n') {
        // If end of data, break the loop
        break;
      } else {
        // Print character to the OLED display
        display.setCursor(x, y);
        display.write(data[i]);
        x += 6 + letterSpacing; // Move to next character position with added space between letters
      }
    }
    display.drawLine(0, y + 12, display.width(), y + 12, SSD1306_BLACK); // Change the line color to default
    display.display();
  }
}
