from device.readers.SL025M      import tramas       as tramasSL         #* Dispositivo de LECTOR de TARJETAS SL025M

from datetime                   import datetime
from time 						import sleep

import threading                                                        # Importacion para el uso de hilos
import serial

from adafruit_mcp230xx.mcp23017 import MCP23017

import RPi.GPIO                                     as GPIO
import digitalio
import board
import busio

# --------------------------------------------------------------------------------------------- Importar librerias de servicios - Import Library of service
from settings 					import setting							#* Servicio para llamar configuraciones
from service					import module_logs						#* Servicio para logs fechados y syslogs
logs = module_logs.LogPython("readed")									#* Se establece el medio de los logs# --------------------------------------------------------------------------------------------- Configuracion y cargadores de librerias - Library configurations and launchers
from settings                   import config

# IMPORT AND CONFIG GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(24, GPIO.IN)
GPIO.setup(23, GPIO.IN)

# CONFIG  I2C - MCP
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c, address=0x20)

# ---------------------------------------------------------------- configuracion luz del boton
LuzBoton           = mcp.get_pin(12)
LuzBoton.direction = digitalio.Direction.OUTPUT   #Luz Boton
def button_led(status:bool)-> None:
    """[SE ENCARGA DE LA LUZ DEL BOTON DE LA ENTRADA]

    Args:
        status (bool): [Turn the button light on or off (True or False)]
    """
    LuzBoton.value = status

def remove_word(name:str)-> str:
	for x in range(len(name)):
		if name[0] != "'" and name[0] != '"':
			name = name[1:]
	return name
# ---------------------------------------------------------------- HILOS DE
reception_queue = [] # serial, pines
message_queue   = [] # serial
device_queue    = [] # list_device

#global puerto_serial_hilo, comando_mux,serial_open
ultima_pos = 0
buffer     = b""
def reading_tag()-> bytearray:
    """[LEE EL TAG Y LO PROCESA PARA IDENTIFICAR SU ID]

    Returns:
        bytearray: [description]
    """
    msg_start_token = bytearray((int(0xee), int(0x00)))
    msg_end_token   = bytearray((int(0xee), int(0x00)))

    def get_message(start_pos):
        global ultima_pos

        msg_start  = buffer.find(msg_start_token, start_pos + 1)
        msg_end    = buffer.find(msg_end_token,msg_start+1)

        if msg_end == -1:   msg = bytearray()
        else:               msg = buffer[msg_start+2:msg_end-4]

        ultima_pos = msg_end
        return msg

    try:
        tag = get_message(ultima_pos)
        return tag.hex()
    except Exception as e:
        logs.warning(f"ERROR: {e}")

puerto_serial_hilo = 0
buffer_serial_mux  = b""
comando_mux        = b""
comando_mux_led    = []
tag_queue          = [] # list_tag
response_card      = b""

def led_reader(state:str)->None:
    """[LED CARD]

    Args:
        state (str): [on, off, blink]
    """

    global serial_open, puerto_serial_hilo, comando_mux_led

    serial_open        = False
    puerto_serial_hilo = 4

    sleep(1)

    if state == "off":
        comando_mux_led = [2, 57, 48, 48, 48, 53, 48, 49, 63, 63, 48, 48, 48, 48, 48, 49, 61, 51, 16, 3] #GreenOff

    if state == "on":
        comando_mux_led = [2, 57, 48, 49, 48, 53, 48, 49, 63, 63, 48, 48, 48, 48, 48, 49, 61, 50, 16, 3] #GreenOn

    if state == "blink":
        comando_mux_led = [2, 57, 48, 50, 48, 53, 48, 49, 63, 63, 48, 48, 48, 48, 48, 49, 61, 49, 16, 3] #GreenBlink

    sleep(1)

    serial_open        = False
    puerto_serial_hilo = setting.hilo_reader


class hilo_serial_mux(threading.Thread): # --------------------------------------------------------------------------------------------> MANEJADOR DE ENTRADA DE PINES E HILOS

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        global buffer_serial_mux, bytes_recived_mux, puerto_serial_hilo, comando_mux,comando_mux_led, serial_open

        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 9600
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        global buffer, response_card

        serial_open   = False
        device_queue.append(self.serial)

        while True:
            sleep(.1)

            if puerto_serial_hilo > 0:

                if not serial_open:

                    if port.is_open:
                        port.close()
                        sleep(1)

                    if puerto_serial_hilo == 1:     #* MUX PARA ANTENNA, QR
                        logs.info(f"CAMBIANDO MUX A {puerto_serial_hilo}: (26:True - 19: False)")
                        GPIO.output(26, True)
                        GPIO.output(19, False)

                    if puerto_serial_hilo == 2:     #* MUX PARA LECTORA SL025M EN CARRO
                        logs.info(f"CAMBIANDO MUX A {puerto_serial_hilo}: (26:False - 19: False)")
                        GPIO.output(26, False)
                        GPIO.output(19, False)

                    if puerto_serial_hilo == 3:     #* MUX PARA LECTORA SL025M VIP
                        logs.info(f"CAMBIANDO MUX A {puerto_serial_hilo}: (26:False - 19: True)")
                        GPIO.output(26, False)
                        GPIO.output(19, True)

                    if puerto_serial_hilo == 4:     #* MUX POR DEFINIR
                        logs.info(f"CAMBIANDO MUX A {puerto_serial_hilo}: (26:True - 19: True)")
                        GPIO.output(26, True)
                        GPIO.output(19, True)

                    sleep(.1)                 #* ESPERA DE TIEMPO PARA ABRIR EL PUERTO 10ms
                    port.open()
                    serial_open = True

                else:

                    if len(comando_mux_led)>0 and puerto_serial_hilo == 4 and serial_open:
                        port.write(comando_mux_led)
                        sleep(1)

                        comando_mux_led = []

                    if len(comando_mux)>0:
                        logs.info(f"COMANDO INIT comando_mux:   {comando_mux}")
                        port.write(comando_mux)
                        comando_mux = b""
                        sleep(.05)

                    else:
                        listen             = port.read(port.in_waiting)
                        buffer_serial_mux  += bytearray(listen)

                        if str(listen) != "b''":

                            if puerto_serial_hilo == 1:
                                pass

                            if puerto_serial_hilo == 2:
                                response_card = listen

                            if puerto_serial_hilo == 3:
                                logs.info(f"{len(listen)} - {listen}")

                                if len(listen) == 10:
                                    selectC   =  tramasSL.selectCard(listen)
                                    keySerial = selectC["uid"][6:8]+selectC["uid"][4:6]+selectC["uid"][2:4]+selectC["uid"][0:2] #Se invierte el patron de bits
                                    listen    = int(keySerial,16)
                                    logs.debug("----------------------------------------------")
                                    reception_queue.append(str(self.serial) + " b'" + str(listen)+"'")
                                else:
                                    logs.info("NO LLEGO CORRECTO")

                        port.reset_input_buffer()
                        port.reset_output_buffer()

list_authorizer = []

class lector_qr(threading.Thread): # -----------------------------------------------------------------------------------------> MANEJADOR SERIAL VIP/MENSUALIDAD/ESPACIALES

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 9600
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        comando_vip = b""
        last_listen_qr = ""
        last_listen = ""

        while True:
            sleep(1)
            try:
                if not port.is_open:
                    port.open()

                    if port.is_open:
                        device_queue.append(self.serial)

                        while True:
                            sleep(1)

                            listen = port.readline()

                            if listen != b'':

                                listen = str(listen)[2:-1]
                                """
                                if len(listen) % 2 == 0:
                                    if listen[:int((len(listen)/2))] == listen[int((len(listen)/2)):]:
                                        listen = listen[:int((len(listen)/2))]
                                """
                                list_lector = list(listen.split("EE01"))

                                res = []
                                for element in list_lector:
                                    if element.strip():
                                        res.append(element)

                                for element in res:

                                    if "\\xee\\x02" in element:
                                        list_lector_qr = list(element.split("\\xee\\x02"))
                                        res_qr = []

                                        for element_qr in list_lector_qr:
                                            if element_qr.strip():
                                                res_qr.append(element_qr)

                                        for element_qr in res_qr:
                                            if len(element_qr)>10:
                                                if element_qr not in list_authorizer:
                                                    list_authorizer.append({"typeToken": "qr", "token": element_qr})
                                                    #logs.info(f"QR: {element_qr}")
                                    else:
                                        list_authorizer.append({"typeToken": "card", "token": element})
                                        #logs.info(f"CARD: {element}")

            except Exception as err:
                logs.warning(f"Error: {port.port} - {err}")
                port.close()

class lector_sl025(threading.Thread): # -----------------------------------------------------------------------------------------> MANEJADOR SERIAL VIP/MENSUALIDAD/ESPACIALES

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 9600
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        global last_token_sl025m
        last_token_sl025m = ""

        if not port.is_open:
            port.open()

            while port.is_open:

                trama = tramasSL.selectCard()
                port.write(trama)
                sleep(.02)

                listen = port.read(port.in_waiting)
                if str(listen) != "b''" and len(listen) >= 6: #Debe de llegar 10 bytes para sacar el UID
                    #logs.info(listen)

                    if listen[0] == 189 and listen[1] == 8 and listen[2] == 1 and listen[3] == 0:

                        uid = listen[4:listen[1]].hex()
                        keySerial = uid[6:8]+uid[4:6]+uid[2:4]+uid[0:2]

                        listen = int(keySerial,16)
                        if last_token_sl025m != listen:
                            #logs.warning(listen)
                            list_authorizer.append({"typeToken": "card", "token": listen})
                            last_token_sl025m = listen
                else:
                    last_token_sl025m = ""

                sleep(.2)


last_tag = ""
class hilo_tag(threading.Thread): # -----------------------------------------------------------------------------------------> MANEJADOR SERIAL VIP/MENSUALIDAD/ESPACIALES

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 9600
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        global buffer,last_tag

        while True:
            sleep(1)
            try:
                if not port.is_open:
                    port.open()

                    if port.is_open:
                        device_queue.append(self.serial)

                        while True:
                            sleep(.01)

                            listen = port.read(port.in_waiting)

                            if str(listen) != "b''":
                                buffer += bytearray(listen)

                                while True:
                                    tag    = reading_tag()
                                    tag    = tag.upper()
                                    buffer = buffer[ultima_pos+1:]

                                    if ultima_pos > 0:

                                        if tag and len(tag) == 24:
                                            if len(list_authorizer) == 0:
                                                list_authorizer.append({"typeToken": "tag", "token": tag})
                                                #logs.info(f"TAG: {tag}")
                                            else:
                                                add_list = True

                                                for element_list_authorizer in list_authorizer:
                                                    if tag in element_list_authorizer['token']:
                                                        add_list = False

                                                if add_list:
                                                    list_authorizer.append({"typeToken": "tag", "token": tag})
                                                    #logs.info(f"TAG: {tag}")

                                        else:
                                            last_tag = ""

                                        break

                                    else:
                                        break

                                port.reset_input_buffer()
                                port.reset_output_buffer()



            except Exception as err:
                logs.warning(f"Error: {port.port} - {err}")
                port.close()



class hilo_printer(threading.Thread): # ------------------------------------------------------------------------------------------> MANEJADOR SERIAL DE LA IMPRESORA

    def __init__(self,serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 38400
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        while True:
            sleep(1)
            try:
                if not port.is_open:
                    port.open()

                    if port.is_open:
                        device_queue.append(self.serial)
                        logs.stage(f"INIT:   Configurations were sent to: {self.serial}")
                        port.write(b'\x1D\x76\x00')
                        port.write(b'\x1B\x68\x03')
                        logs.stage(f"FINISH: Configurations were sent to: {self.serial}")

                        while True:
                            sleep(.01)
                            listen = port.readline()

                            if str(listen) != "b''":
                                reception_queue.append(str(self.serial) + " " + str(listen))

            except Exception as err:
                logs.warning(f"Error: {port.port} - {err}")
                port.close()

class hilo_card_dispenser(threading.Thread): # -----------------------------------------------------------------------------------> MANEJADOR SERIAL DEL DISPENSADOR

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 9600
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        while True:
            sleep(1)
            try:
                if not port.is_open:
                    port.open()

                    if port.is_open:
                        device_queue.append(self.serial)

                        while True:
                            sleep(.01)
                            listen = port.readline()

                            if str(listen) != "b''":
                                reception_queue.append(str(self.serial) + " " + str(listen))

                            if len(message_queue) == 0:
                                port.write(b'\x02\x30\x52\x46\x03\x25\x05')

                            if len(message_queue) > 0:

                                if self.serial in message_queue[0]:
                                    send = remove_word(message_queue[0])
                                    port.write(bytes(send, encoding = "utf-8"))
                                    message_queue.pop(0)

            except Exception as err:
                logs.warning(f"Error: {port.port} - {err}")
                port.close()

class hilo_card_collector(threading.Thread): # -----------------------------------------------------------------------------------> MANEJADOR SERIAL DEL COLECTOR

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial    = serial

    def run(self):
        port          = serial.Serial()
        port.port     = '/dev/'+self.serial
        port.baudrate = 9600
        port.parity   = serial.PARITY_NONE
        port.stopbits = serial.STOPBITS_ONE
        port.bytesize = serial.EIGHTBITS
        port.timeout  = 1
        port.xonxoff  = 0
        port.rtscts   = 0
        port.dsrdt    = 0

        while True:
            sleep(1)
            try:
                if not port.is_open:
                    port.open()

                    if port.is_open:
                        device_queue.append(self.serial)

                        while True:
                            sleep(.01)
                            listen = port.readline()

                            if str(listen) != "b''":
                                reception_queue.append(str(self.serial) + " " + str(listen))

                            if len(message_queue) == 0:
                                port.write(b'\x02\x52\x46\x03\x15')

                            if len(message_queue) > 0:

                                if self.serial in message_queue[0]:
                                    send = remove_word(message_queue[0])
                                    port.write(bytes(send, encoding = "utf-8"))
                                    message_queue.pop(0)

            except Exception as err:
                logs.warning(f"Error: {port.port} - {err}")
                port.close()

pines_queue     = [] # list_pines
class hilo_pines(threading.Thread): # --------------------------------------------------------------------------------------------> MANEJADOR DE ENTRADA DE PINES E HILOS

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID  = threadID

    def run(self):

        GPIO.setup(self.threadID, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        pines_queue.append({'pin':self.threadID, 'status': 0, 'time': datetime.now()})
        loop = True

        while True:
            sleep(.01)
            if not GPIO.input(self.threadID):
                if loop:
                    loop = False
                    for list_pines in pines_queue:
                        if self.threadID == list_pines['pin']:
                            list_pines['status'] = 1
                            list_pines['time']   = datetime.now()
                            if setting.loopB1 != self.threadID:
                                logs.info(list_pines)
            else:
                if not loop:
                    loop = True
                    for list_pines in pines_queue:
                        if self.threadID == list_pines['pin']:
                            list_pines['status'] = 0
                            list_pines['time']   = datetime.now()
                            if setting.loopB1 != self.threadID:
                                logs.info(list_pines)

# ------------------------------------------------------------> DISPOSITIVOS
if "Reader" in setting.devices:
    serial_open        = False
    puerto_serial_hilo = setting.hilo_reader
    thread_serial_01= hilo_serial_mux("ttyReader")
    thread_serial_01.start()

if "lector_qr" in setting.devices:
    lector_qr = lector_qr("ttyCardReader")
    lector_qr.start()

if "lector_sl025m" in setting.devices:
    lector_sl025 = lector_sl025("ttyCardReader")
    lector_sl025.start()

if "Antenna" in setting.devices:
    hilo_tag = hilo_tag("ttyAntenna")
    hilo_tag.start()

if "Printer" in setting.devices:
    thread_serial_02 = hilo_printer("ttyPrinter")
    thread_serial_02.start()

if "CardDispenser" in setting.devices:
    thread_serial_03 = hilo_card_dispenser("ttyCardDispenser")
    thread_serial_03.start()

if "CardCollector" in setting.devices:
    thread_serial_04 = hilo_card_collector("ttyCardCollector")
    thread_serial_04.start()

# ------------------------------------------------------------> PINES

thread_pin_08 = hilo_pines(8)
thread_pin_08.start()

thread_pin_21 = hilo_pines(21)
thread_pin_21.start()

thread_pin_22 = hilo_pines(22)
thread_pin_22.start()

thread_pin_25 = hilo_pines(25)
thread_pin_25.start()

thread_pin_27 = hilo_pines(27)
thread_pin_27.start()

for pines in pines_queue:
    logs.debug(pines)