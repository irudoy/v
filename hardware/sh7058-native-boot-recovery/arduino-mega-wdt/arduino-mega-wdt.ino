#include <Arduino.h>

#if !defined(__AVR_ATmega2560__)
#error "This sketch targets the Arduino Mega 2560 (ATmega2560) only."
#endif

#if F_CPU != 16000000UL
#error "The WDT timer configuration requires a 16 MHz CPU clock."
#endif

namespace {

constexpr uint8_t kWdtOutputPin = 9;  // PH6 / OC2B on Arduino Mega 2560.

void startWdtGenerator() {
  // Timer2 Fast PWM mode 7, TOP = OCR2A:
  //   16 MHz / (256 * (249 + 1)) = 250 Hz
  //   (124 + 1) / (249 + 1) = 50% duty cycle
  pinMode(kWdtOutputPin, OUTPUT);
  digitalWrite(kWdtOutputPin, LOW);

  noInterrupts();

  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2 = 0;
  TIMSK2 = 0;

  OCR2A = 249;
  OCR2B = 124;

  // Clear any pending Timer2 flags before starting the waveform.
  TIFR2 = _BV(TOV2) | _BV(OCF2A) | _BV(OCF2B);

  // Non-inverting PWM on OC2B, Fast PWM with OCR2A as TOP.
  TCCR2A = _BV(COM2B1) | _BV(WGM21) | _BV(WGM20);
  TCCR2B = _BV(WGM22) | _BV(CS22) | _BV(CS21);  // Prescaler 256.

  interrupts();
}

}  // namespace

void setup() {
  startWdtGenerator();
}

void loop() {}
