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

  //PRR |= (0<<PRADC);
  //ADCSRA |= (1<<ADEN) | (1<<ADSC) | (1<<ADPS0) | (1<<ADPS1) | (1<<ADPS2);
  //ADMUX |= (1<<ADLAR) ;
  //ADMUX |= (1<<REFS0);

  //TCCRA |= (1 << COM0A1);
  //TCCRA |= (1 << WGM01) | (1 << WGM00);
  //TCCRB |= (1 << CS01);
  sei();

  DDRC = 0b00000111;
  DDRB = 0xFF;

  while(1){
    PORTB |= (1);
    _delay_ms(25);
    PORTB = 0;
    _delay_ms(25);
  }

  return 0;
}
