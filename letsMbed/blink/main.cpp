#include "mbed.h"
 
DigitalOut led1(LED1);
 
int main()
{
    while (1) {
        led1 = !led1;
        wait_ms(500);
    }
}
