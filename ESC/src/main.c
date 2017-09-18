#define F_CPU 16000000L
#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <stdbool.h>

#define Phase_A_Read 3
#define Phase_B_Read 4
#define Phase_C_Read 5

uint16_t ReadADC(uint8_t ADCchannel)
{
 //select ADC channel with safety mask
 ADMUX = (ADMUX & 0xF0) | (ADCchannel & 0x0F);
 //single conversion mode
 ADCSRA |= (1<<ADSC);
 // wait until ADC conversion is complete
 while( ADCSRA & (1<<ADSC) );
 return ADCH;
}


int main(void) {

  PRR |= (0<<PRADC);
  ADCSRA |= (1<<ADEN) | (1<<ADSC) | (1<<ADPS0) | (1<<ADPS1) | (1<<ADPS2);
  ADMUX |= (1<<ADLAR) ;
  ADMUX |= (1<<REFS0);

  TCCR2A |= (1 << COM0A1);
  TCCR2A |= (1 << WGM01) | (1 << WGM00);
  TCCR2B |= (1 << CS01);

  TCCR1A |= (1 << COM0A1);
  TCCR1A |= (1 << WGM01) | (1 << WGM00);
  TCCR1B |= (1 << CS01);

  TCCR0A |= (1 << COM0A1);
  TCCR0A |= (1 << WGM01) | (1 << WGM00);
  TCCR0B |= (1 << CS01);

  sei();

  DDRC = 0b00000111;

  while(1){
    OCR0A = ReadADC(Phase_A_Read);
    OCR1A = ReadADC(Phase_B_Read);
    OCR2A = ReadADC(Phase_C_Read);

//    PORTC = 0b00000111;
    PORTC |= (1);

    _delay_ms(500);
    PORTC = 0;

    PORTC |= (1<<1);

    _delay_ms(500);
    PORTC = 0;

    PORTC |= (1<<2);
    _delay_ms(500);
    //PORTC = 0b00000000;
    PORTC = 0;

    _delay_ms(500);
  }

  return 0;
}
