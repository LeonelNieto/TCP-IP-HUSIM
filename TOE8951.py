import time
import serial

def init_comPort( comPort:str ):
    global ser
    ser = serial.Serial(
        port=comPort,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

def init_powerSupply(  ):
        idn = send_cmd( "*IDN?" )
        print( idn )
        send_cmd( "SYST:REM", expect_response=False )              #Set power supply in remote

def set_voltage( voltage ):
    send_cmd( f"SOUR:VOLT {voltage}", expect_response=False )

def set_max_current( current ):
    send_cmd( f"SOUR:CURR {current}", expect_response=False )

def turn_ON_powerSupply( ):
    send_cmd( "OUTP ON", expect_response=False )

def turn_OFF_powerSupply( ):
    send_cmd( "OUTP OFF", expect_response=False )

def measure_voltage( ):
    voltage = send_cmd("MEAS:VOLT?")
    print( f"Volatge meausre: {voltage} V" )
    return voltage

def measure_current( ):
    current = send_cmd("MEAS:CURR?")
    print( f"Current measure: {current} A" )
    return current
    
def measure_power( ):
    power = send_cmd("MEAS:POW?")
    print( f"Power measure: {power} W" )
    return power

def send_cmd( command, expect_response=True ):
    ser.write( ( command + '\n' ).encode( ) ) 
    if expect_response:
        time.sleep( 0.1 )
        return ser.readline( ).decode( ).strip( )
    return None

def Close_Power_Supply_COM_Port( ):
    ser.close

if __name__ == '__main__':
    
    init_comPort( "COM13" )
    init_powerSupply( )
    set_voltage( 13.4 )
    set_max_current( 5 )
    turn_ON_powerSupply( )
    time.sleep( 1 )
    measure_voltage( )
    measure_current( )
    measure_power( )
    turn_OFF_powerSupply
    Close_Power_Supply_COM_Port( )
