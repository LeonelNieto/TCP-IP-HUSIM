import socket
import subprocess
import psutil
import time
import configparser
from toe8951 import *

config = configparser.ConfigParser()
config.read('config.ini')

BUFFER_SIZE           = 1024
IP                    = config['HUSIM']['IP_ADDRESS']
TCP_PORT              = int( config['HUSIM']['TCP_PORT'] )
HUSIM_PATH            = config['HUSIM']['PATH']
HUSIM_COM_PORT        = int( config['HUSIM']['COM_PORT'] )
POWER_SUPPLY_COM_PORT = config['POWER_SUPPLY']['COM_PORT']
POWER_SUPPLY_VOLTAGE  = config['POWER_SUPPLY']['VOLTAGE']
POWER_SUPPLY_CURRENT  = config['POWER_SUPPLY']['CURRENT']

def readMultiFrame(command, timeout=0.2):
    raw_data = ""
    i=1
    s.settimeout(timeout)
    s.send( command.encode( ) )
    s.recv( BUFFER_SIZE ).decode( )
    try:
        while True:
            answer = s.recv( BUFFER_SIZE ).decode( )
            frame_length = answer[ 16 : 18 ]
            if ( i % 2 ):
                if frame_length in ["1C", "2C", "3C", "4C", "33"]:
                    raw_data += answer[ 20 : ]
                else:
                    raw_data += answer[ 18 : 18 + ( int ( frame_length ) * 2 ) ]        
            i+=1
    except Exception as e:
        return raw_data

####################  INIT POWER SUPPLY  ####################
reference_time = time.time( )
init_comPort( POWER_SUPPLY_COM_PORT )
init_powerSupply( )
set_voltage( POWER_SUPPLY_VOLTAGE )
set_max_current( POWER_SUPPLY_CURRENT )

####################  OPEN HUSIM AND GET PID APP  ####################
print( "Abriendo HUSIM..." )
process = subprocess.Popen( HUSIM_PATH )
pid = process.pid
print( pid )
turn_ON_powerSupply( )
time.sleep( 1.5 )
print( "Se ha abierto correctamente la aplicación de HUSIM" )

####################  INIT TCP/IP SESION  ####################
try: 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect( ( IP, TCP_PORT ) )

    ####################  CONNECT TO HUSIM COM PORT  ####################
    huSim_com_port = f"{HUSIM_COM_PORT:02d}"
    s.send( ("connect_serial_" + huSim_com_port).encode( ) )
    answer = s.recv( BUFFER_SIZE ).decode( )
    print(answer)
    time.sleep( 2 )
    ####################  GET S32K CHECKSUM  ####################
    answer = readMultiFrame( "DirectBusMessage_0101_22_60_0F40_02_00000019", 0.2 )
    print( "S32K Checksum: " + answer )

    ####################  GET FBL CHECKSUM  ####################
    FBL_Checksum = readMultiFrame( "DirectBusMessage_0101_22_60_0F40_02_000D02FF", 0.2)          
    print( "FBL Checksum: " + FBL_Checksum )

    ####################  GET DSP CHECKSUM  ####################
    while True:
        DSP_Checksum = readMultiFrame( "DirectBusMessage_0101_22_60_0F40_02_000504FF", 0.2)
        if DSP_Checksum != "42":      
            print( "DSP Checksum: " + DSP_Checksum[ : 70 ] )
            break
        time.sleep( 0.3 )
        
    ####################  CLOSE HUSIM APP  ####################
    s.close()
    time.sleep( 0.2 )
    turn_OFF_powerSupply( )
    proc = psutil.Process( pid )
    proc.terminate( )
    Close_Power_Supply_COM_Port( )
    current_time = time.time( )
    cycle_time = current_time - reference_time
    print(f"Cycle time: {cycle_time} s")
    
except Exception as e:
    s.close( )
    time.sleep( 0.2 )
    turn_OFF_powerSupply( )
    proc = psutil.Process( pid )
    proc.terminate( )
    print( e )
    Close_Power_Supply_COM_Port( )
