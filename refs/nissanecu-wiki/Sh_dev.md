# Sh dev

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Sh_dev
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# Writing code for the SuperH microcontrollers !

Here's a collection of notes that should help write kernels and modify stock firmware. The idea is to supplement or reword the less obvious parts of the [Datasheets](<https://nissanecu.miraheze.org/wiki/Sh_docs> "Sh docs"). 

## Advanced Timer Unit-II (ATU-II)

"Advanced Timer" indeed. Very complex unit with over 10 independant timers, each with a different set of features. 

### Interrupts

Channel 1 seems to offer interrupts for "compare-on-match", i.e. fire an interrupt when the free-running counter compares equal to one of the GRx registers (like (TCNT1A == GRA) for example). I think this **only** works when the associated bits of the TIOR registers are configured to enable pin outputs. In other words, 

  * TIOR1A = 0 "compare-match disabled; pin output undefined"
  * TSR1A.IMF* bits do not cause an interrupt



To have some kind of interval interrupt, the best solution I've found is 

  * use TCNT1B as a freerunning counter
  * set OCR as the interval
  * set TIER1B.CME to enable compare-match interrupt



## Serial Communication Interface (SCI)

### basic example

Typical code to send data will look roughly like this : 
    
    
    	/* quick ping : send 0x55 */
    	while (!SCI1.SSR.BIT.TDRE) {}	//wait for empty
    	SCI1.TDR = 0x55;
    	SCI1.SSR.BIT.TDRE = 0;		//start tx
    

Of course more finesse will be required when using interrupts, removing K line duplex echo, etc. 

### duplex removal

Since the K line is half duplex, anything sent from the mcu must either 

  * be done with RX disabled
  * have some code to read the echo and either discard or compare to the last sent byte.



I have used the first method succesfully : I disable RX until SCI1.SSR.BIT.TEND indicates that transmit is complete. I assume enabling RX before would result in bogus data or a framing error since there is still a transmission in progress. 

From the DS : 
    
    
    The SCI checks the TDRE bit when it outputs the stop bit. [...] If TDRE is 1, the SCI sets the TEND bit to 1 in SSR, outputs the stop bit, then continues output of 1-bits (marking).
    

  
There is of course a delay before the duplex echo arrives at the RX pin, but the few instructions required to check TEND and then set SCR.RE seem to be sufficient to guarantee that the RX is enabled during the stop bit. 

### misc

  * very important : if some error occurs that causes a framing error (FER flag), this **disables** any further reception and must be dealt with. This can happen when changing the baud rate, if the host sends data at the wrong speed.
  * very important #2 : if you do use SCI in synchronous mode in your code (for example, some ECU types have their SPI EEPROM wired to some SCI pins) bear in mind following statement from the CPU datasheet:  




_"Note: * In simultaneous transmit/receive operation, the TE bit and RE bit must be cleared to 0 or_ set to 1 simultaneously."_  
_

i.e. use following code 
    
    
            SCI2.SCR.BYTE |= (1<<4) | (1<<5);
    
    

instead of this 
    
    
    	SCI2.SCR.BIT.TE = 1;
            SCI2.SCR.BIT.RE = 1;
    
    

to prevent receiveng of the data shifted 1 bit right (for example 0x34 instead of 0x69)
