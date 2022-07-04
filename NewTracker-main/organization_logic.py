#* Author: @Vitovillamil - Javier Antonio Villamil Gutierrez
#* Fecha: 2022/ABRIL

import reading_and_writing								as hermes		#* Libreria CI24 para la deteccion
hermes.led_reader("blink")

from settings 					import setting							#* Servicio para llamar configuraciones

from service					import play				as playsound	#* Servicio para la reproduccion de audios
from service					import transactions						#* Servicio para ejecutar la transaccion
from service					import requests_server	as rs			#* Service request server
from service					import codification						#* Servicio para codificacion o decodificacion de datos
from service					import module_logs						#* Servicio para logs fechados y syslogs

logs = module_logs.LogPython("logic")									#* Se establece el medio de los logs

from datetime 					import datetime, timedelta
from time 						import sleep

import importlib
import json
import paho.mqtt.client									as mqtt
import threading
import socketio
sio  = socketio.Client()

if setting.machine_identification["type_device"] == "Console_Exit":
	from service							import liquidation      as liq          #* Servicio de liquidacion
	liq.settings()

	if "CardCollector" in setting.devices:
		from device.dispenser_collector		import card_collector	as card_c		#* Dispositivo de COLLECTOR DE TARJETAS

	if "Printer" in setting.devices:
		from device.printers            	import nippon_printer					#* Dispositivo de IMPRESORA TIPO NIPPON

if setting.machine_identification["type_device"] == "Console_Entry":
	if "CardDispenser" in setting.devices:
		from device.dispenser_collector		import card_dispenser	as card_d		#* Dispositivo de DISPENSADOR DE TARJETAS

if "CardCollector" in setting.devices or "CardDispenser" in setting.devices:
	from device.readers.SL025M      		import tramas			as tramasSL		#* Dispositivo de LECTOR de TARJETAS SL025M
	from device.readers.SL025M      		import main_parking		as parkingSL	#* Dispositivo de LECTOR de TARJETAS SL025M


from device.barrier							import main				as barrier
barrier = barrier.barrera(setting.loopB1)


#* ::::::::::::::::::::::::::::::::::::::::::::::::::::::::> Global variables
origen     = datetime.fromisoformat(setting.config_parking['date_origin'])
time_loop  = timedelta(milliseconds=(setting.time_loop))						#* Loop duration time
time_while = setting.time_while						      						#* Time repeat for WHILE:

for index, list_pines in enumerate(hermes.pines_queue):
	"""
		loopA1:			Por si solo identifica Moto
		loopA2:			Por si solo no identifica nada, pero en compañia de A1 identifica Carro
		loopB1:			Trabaja para la barrera
		loopB2:			Destinado para el SEMAFORO
		console_button:	Destinado para el boton de la consola de entrada
	"""
	if list_pines['pin'] == setting.loopA1: 		loopA1			= index
	if list_pines['pin'] == setting.loopA2: 		loopA2			= index
	if list_pines['pin'] == setting.loopB2: 		loopB2			= index
	if list_pines['pin'] == setting.console_button:	console_button	= index





#* ::::::::::::::::::::::::::::::::::::::::::::::::::::::::> cleaner
info_plate			= {"plate": "", "confidence": 0, "img":""}
plate_car			= ""
def cleaner_plate() -> None:
	global info_plate, plate_car, img_plate

	info_plate["plate"]			= ""
	info_plate["confidence"]	= 0
	info_plate["img"]			= ""

	plate_car					= ""
	img_plate					= ""

	insta.mqtt_pub("devicestatus","plate","")


take_snapshot	= []
take_video		= []
def cleaner_video() -> None:
	global take_snapshot, take_video

	take_snapshot	= []
	take_video		= []


token_authorizer	= ""
token_procesados	= []
def cleaner_token() -> None:
	global token_authorizer, token_procesados

	hermes.list_authorizer	= []
	token_authorizer		= ""
	token_procesados		= []


card_id		= ""
agreement	= []
hybrid		= False
def cleaner_other() -> None:
	global card_id, agreement, hybrid

	card_id		= ""
	agreement	= []
	hybrid	= False


def cleaner_all() -> None:

	cleaner_other()
	cleaner_token()
	cleaner_video()
	cleaner_plate()





#* ::::::::::::::::::::::::::::::::::::::::::::::::::::::::> Interface and sound
def inter_sound(sound:list = "", interface:str = "") -> None:
	"""[Takes care of the sound and interface messages]
	Args:
		#* sound     (list(str) or (str)): [Audio to play EXAMPLE: "name_audio"]
		#* interface (str):                [Message on screen EXAMPLE: "MSG"]
	"""
	try:
		if sound != "" and interface != "":
			logs.debug(f"SOUND: {sound}	INTERFACE: {interface}")
			playsound.play(sound)
			sio.emit('server_central_python', {'device_data': interface, 'device_reader': interface})

		elif sound != "":
			logs.debug(f"SOUND: {sound}")
			playsound.play(sound)

		elif interface != "":
			logs.debug(f"INTERFACE: {interface}")
			sio.emit('server_central_python', {'device_data': interface, 'device_reader': interface})

	except Exception as err:
		logs.error(f"Error Manager: {err}")






#* ::::::::::::::::::::::::::::::::::::::::::::::::::::::::> console organization
status_card		= "SIN VEHICULO"
date_base		= datetime.now()
id_transaction	= ""

def waiting(self) -> None:
	global date_base, id_transaction, status_card, take_video, snapshot

	status_card	= "SIN VEHICULO"
	msg_wait	= True

	hermes.button_led(False)

	while self.state_console == "waiting":

		if hermes.pines_queue[loopB2]['status'] == 1:	rs.semaphore(True)

		if hermes.pines_queue[loopA1]['status'] == 0 and hermes.pines_queue[loopA2]['status'] == 0:
			cleaner_all()
			importlib.reload(setting)

			if msg_wait:
				inter_sound("","ESPERANDO VEHICULO")
				msg_wait = False


		actual_time = datetime.now()

		if ((hermes.pines_queue[loopA2]['status'] == 1 and hermes.pines_queue[loopA1]['status'] == 0) and (actual_time - hermes.pines_queue[loopA2]['time']) > (time_loop)) and not msg_wait:
			inter_sound("","LOOP A2, ESPERANDO ACTIVACION DEL LOOP A1")
			insta.mqtt_pub("devicestatus","warning","Activacion de LOOP A2")
			msg_wait = True

		if card_id != "" and setting.machine_identification["type_device"] == "Console_Exit":
			self.state_console  = "on_console"
			status_card         = "Carro"

		if (hermes.pines_queue[loopA2]['status'] == 1 and (actual_time - hermes.pines_queue[loopA2]['time']) > time_loop) and (hermes.pines_queue[loopA1]['status'] == 1 and (actual_time - hermes.pines_queue[loopA1]['time']) > time_loop):
			self.state_console = "on_console"
			status_card        = "Carro"

		if (hermes.pines_queue[loopA2]['status'] == 0 and (actual_time - hermes.pines_queue[loopA2]['time']) > time_loop) and (hermes.pines_queue[loopA1]['status'] == 1 and (actual_time - hermes.pines_queue[loopA1]['time']) > time_loop):
			self.state_console = "on_console"

			if setting.machine_identification['loops'] == 1:

				if setting.machine_identification['type_console'] == "Carro":	status_card = "Carro"
				elif setting.machine_identification['type_console'] == "Moto":	status_card = "Moto"
				elif setting.machine_identification['type_console'] == "Mixto":	status_card = "Mixto"

			if setting.machine_identification['loops'] == 2:	status_card = "Moto"

		sleep(time_while)


	now            = datetime.now()
	difference     = now - origen
	difference     = int(difference.total_seconds()+18000)
	date_base      = now
	id_transaction = str(setting.machine_identification["id_device"]) +"-"+ str(difference)

	insta.mqtt_pub("devicestatus","info",f"{status_card} en consola")

	try:
		take_video = rs.Video("start-record",id_transaction)
		take_video = take_video['videoFiles']

	except Exception as err:	logs.warning(err)



type_id          = ""
init_button      = False
card_transaction = False
def on_console(self)-> None:

	def console_entry(self)-> None:
		global card_transaction, hybrid

		while True:

			actual_time_entry = datetime.now()

			if setting.machine_identification['console_operation'] == 'Hibrido' and int(info_plate["confidence"]) == 28 and hybrid:
				self.state_console = "generating_transaction"
				break

			if card_transaction or (hermes.pines_queue[console_button]['status'] == 1 and "ttyPrinter" in hermes.device_queue):	#* TRANSACCION OCASIONAL
				card_transaction   = False
				self.personType    = 0
				self.state_console = "generating_transaction"
				hermes.button_led(False)
				break

			if token_authorizer:
				self.state_console = "generating_transaction"
				break

			if ((hermes.pines_queue[loopA2]['status'] == 0 and (actual_time_entry - hermes.pines_queue[loopA2]['time']) > (time_loop)) and (hermes.pines_queue[loopA1]['status'] == 0 and (actual_time_entry - hermes.pines_queue[loopA1]['time']) > (time_loop))):
				logs.info(f"ACTION - ON CONSOLE_ENTRY: ERROR")
				self.state_console = "waiting"
				break

			sleep(time_while)


	def console_exit(self)-> None:
		global card_id

		while True:
			actual_time_exit = datetime.now()

			if token_authorizer or card_id != "":
				self.state_console = "generating_transaction"
				break

			if ((hermes.pines_queue[loopA2]['status'] == 0 and (actual_time_exit - hermes.pines_queue[loopA2]['time']) > (time_loop)) and (hermes.pines_queue[loopA1]['status'] == 0 and (actual_time_exit - hermes.pines_queue[loopA1]['time']) > (time_loop))):
				logs.info("ACTION - ON CONSOLE_EXIT: ERROR")
				self.state_console = "waiting"
				break

			sleep(time_while)


	while True:
		actual_time = datetime.now()

		if setting.machine_identification["type_device"] == "Console_Entry":

			if token_authorizer != "":
				console_entry(self)
				break

			if init_button or "ttyPrinter" in hermes.device_queue:
				hermes.button_led(True)
				inter_sound("presione_el_boton", f"{status_card}, Presione el boton")
				console_entry(self)
				break

		if setting.machine_identification["type_device"] == "Console_Exit" :
			if token_authorizer != "":
				console_exit(self)
				break

			if "ttyCardCollector" in hermes.device_queue:

				if status_card == "Mixto":	inter_sound("inserte_la_tarjeta", f"Inserte la tarjeta")
				else:						inter_sound("inserte_la_tarjeta", f"{status_card}, inserte la tarjeta")

			else:

				if status_card == "Mixto":	inter_sound("acerque_el_tiquete", f"Acerque el tiquete")
				else:						inter_sound("acerque_el_tiquete", f"{status_card}, Acerque el tiquete")

			console_exit(self)
			break

		if (hermes.pines_queue[loopA2]['status'] == 0 and (actual_time - hermes.pines_queue[loopA2]['time']) > time_loop) and (hermes.pines_queue[loopA1]['status'] == 0 and (actual_time - hermes.pines_queue[loopA1]['time']) > time_loop):
			self.state_console   = "waiting"
			sleep(1)
			break

		sleep(time_while)



card_retired = "INIT"
estado_impresora = ""
def transaction_entry(self)-> None:
	global hybrid

	if token_authorizer:
		logs.info(f"TOKEN: {token_authorizer} - PLATE:{plate_car}")
		info_transaction, invoice_template, info_print_qr = transactions.create(date_base, id_transaction, take_video, take_snapshot, status_card, "", token_authorizer['personType'], token_authorizer['token'], token_authorizer['tokeType'], plate_car, img_plate, agreement)
		self.dispenser = False

	elif hybrid:
		info_transaction, invoice_template, info_print_qr = transactions.create(date_base, id_transaction, take_video, take_snapshot, status_card, "", self.personType, self.token, self.tokenType, plate_car, img_plate, agreement)
		hybrid = False
		self.dispenser = False

	else:
		logs.info(f"STATUS CARD: {status_card} - USER TYPE: {self.personType} - TOKEN:{self.token} - PLATE:{plate_car}")
		info_transaction, invoice_template, info_print_qr = transactions.create(date_base, id_transaction, take_video, take_snapshot, status_card, "", self.personType, self.token, self.tokenType, plate_car, img_plate, agreement)

	if self.dispenser == True:

		if "ttyCardDispenser" in hermes.device_queue:

			while True:

				if card_retired == "approved":
					transactions.c_json(info_transaction)
					self.state_console = "allowing_passage"
					break

				elif card_retired == "not_approved":
					self.state_console = "on_console"
					break

				sleep(time_while)

		elif "ttyPrinter" in hermes.device_queue:

			err, qr_codificado = codification.coding(info_print_qr)

			if err:	logs.info(f"codification.coding: {err}")
			else:
				logs.info("--------------------------------------------")
				for x in invoice_template:	logs.info(x)
				logs.info("--------------------------------------------")

				err, data = nippon_printer.nippon_printer("/dev/ttyPrinter", 38400, qr_codificado, invoice_template)

				if err:	logs.info(f"nippon_printer.nippon_printer {err}")
				else:
					inter_sound("tome_el_tiquete","Tome el tiquete")

					transactions.c_json(info_transaction)
					self.state_console = "allowing_passage"

			logs.info(f"{info_print_qr} -> {qr_codificado}")

	else:
		transactions.c_json(info_transaction)
		self.state_console = "allowing_passage"



def transaction_exit(self)-> None:

	if token_authorizer:
		logs.info(f"TOKEN: {token_authorizer}")
		info_transaction, invoice_template, info_print_qr = transactions.create(date_base, id_transaction, take_video, take_snapshot, status_card, token_authorizer['idTransaction'], token_authorizer['personType'], token_authorizer['token'], token_authorizer['tokeType'], plate_car, img_plate, agreement)

	else:
		logs.info(f"CARD: {self.personType} {self.token} {self.tokenType}")
		info_transaction, invoice_template, info_print_qr = transactions.create(date_base, id_transaction, take_video, take_snapshot, status_card, parent_transaction, self.personType, self.token, self.tokenType, plate_car, img_plate, agreement)

	transactions.c_json(info_transaction)
	self.state_console = "allowing_passage"


stop_id = []
actual_status    = "waiting"
class machine_process(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.state_console = "waiting"
		self.dispenser     = True
		self.personType    = 0

	def run(self):
		global actual_status, plate_car, img_plate, antishock, snapshot, stop_id, bajar_barrera

		while True:
			actual_status = self.state_console

			if self.state_console == "waiting":
				logs.info("Console status: -----------------------------------------------> WAITING")
				self.dispenser = True
				waiting(self)

			elif self.state_console == "on_console":
				logs.info("Console status: -----------------------------------------------> ON CONSOLE")
				on_console(self)

			elif self.state_console == "generating_transaction":
				logs.info("Console status: -----------------------------------------------> GENERATING TRANSACTION")

				try:
					snapshot = rs.Video("take-snapshot",id_transaction,"")
					take_snapshot.append(snapshot['snapshotFiles'])

				except Exception as err:	logs.warning(err)

				if len(info_plate) > 0:
					plate_car = info_plate['plate']
					img_plate = info_plate['img']
					insta.mqtt_pub("devicestatus","plate",plate_car)

				if "ttyCardDispenser" in hermes.device_queue or "ttyCardCollector" in hermes.device_queue:
					self.token     = card_id
					self.tokenType = 2

				elif "ttyPrinter" in hermes.device_queue:
					self.token     = id_transaction
					self.tokenType = 7

				if setting.machine_identification["type_device"] == "Console_Entry":	transaction_entry(self)
				else:																	transaction_exit(self)

			elif self.state_console == "allowing_passage":
				logs.info("Console status: -----------------------------------------------> ALLOWING PASSAGE")

				if setting.machine_identification["type_device"] == "Console_Entry":	inter_sound("bienvenido",f"Bienvenido {plate_car}")
				else:																	inter_sound("vuelva_pronto",f"Vuelva pronto {plate_car}")

				stop_id.append(id_transaction)
				barrier.start()

				try:

					for element in stop_id:
						logs.info(f"PARANDO TRANSACCION: {element}")
						rs.Video("stop-record",element)

					stop_id = []

				except Exception as err:	pass

				sleep(setting.time_transaction)

				if plate_car != info_plate['plate']:
					logs.info(f"Comparacion de placas {plate_car} | {info_plate['plate']}")

					try:
						info_update = {
							"transactionType":    0,											#* TIPO DE TRANSACCIÓN ("ENTRADA:1 - SALIDA:2")
							"transactionId":      id_transaction,								#* SE CONSTRUYE CON EL ID DE LA CONSOLA Y LA HORA DE LA TRANSACCIÓN DE INGRESO
							"plate":              info_plate['plate'],							#* LA PLACA QUE SE RECONOCIO
						}
						transactions.a_json(info_update)

						insta.mqtt_pub("devicestatus","info",f"{id_transaction} - Actualizacion: {plate_car}")

					except Exception as err:	logs.warning(f"Error: {err}")

				cleaner_all()
				self.state_console = "waiting"
				rs.semaphore(False)

			sleep(time_while)








class organization_status(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		def remove_word(name):
			for x in range(len(name)):

				if name[0] != "'" and name[0] != '"':	name = name[1:]

			return name


		def Printer(reading):
			global estado_impresora

			estado_impresora = remove_word(reading)
			estado_impresora = nippon_printer.return_state(bytes(estado_impresora, encoding = 'utf-8'))
			logs.debug(f"STATE: {estado_impresora}")

			if str(estado_impresora) == "Impresora lista":			inter_sound("","Impresora lista para iniciar operacion")
			if str(estado_impresora) == "Impresora baja de papel":	inter_sound("","Impresora baja de papel")

		def Dispenser(reading):
			global dispenser_status

			state_card_dispenser = remove_word(reading)
			state_card_dispenser, msg_serial = card_d.return_state(bytes(state_card_dispenser, encoding = 'utf-8'))

			if dispenser_status != state_card_dispenser and state_card_dispenser != "SIN ESTADO":
				logs.info(f"{msg_serial}  |  {state_card_dispenser}")
				dispenser_status = state_card_dispenser

		def Collector(reading):
			global collector_status

			state_card_collector = remove_word(reading)
			state_card_collector, msg_serial = card_c.return_state(bytes(state_card_collector, encoding = 'utf-8'))

			if collector_status != state_card_collector:
				collector_status = state_card_collector
				logs.info(f"{msg_serial}  |  {state_card_collector}")



		def authorizer_token(type_id,tag_id):
			global last_token_authorizer

			type_vehicle = 0

			if status_card == "Carro":	type_vehicle = 1
			if status_card == "Moto":	type_vehicle = 2

			data = rs.authorizer(type_vehicle,type_id,tag_id)

			if not data['approved']:
				insta.mqtt_pub("devicestatus","info",f"{type_id} {tag_id} | {data['approved']}")

				if type_id == "card":
					inter_sound("tarjeta_no_valida", f"{tag_id}: {data['message']}")
					sleep(len(data['message'])/9)

				else:	inter_sound("", f"{tag_id} {type_id}: {data['message']}")

				return False

			else:
				insta.mqtt_pub("devicestatus","info",f"{type_id} {data['token']} | {data['approved']}")
				last_token_authorizer = tag_id

				if type_id == "card":	inter_sound("", f"{data['token']} {type_id}: {data['message']}")

				return data


		global token_authorizer, token_procesados, last_plate, last_text, hybrid, last_token_authorizer

		finish_token			= False
		last_plate				= ""
		last_text				= ""
		last_token_authorizer	= ""

		while True:
			try:
				def msg_serial(self):

					if "ttyPrinter" in hermes.reception_queue[0]:			Printer(hermes.reception_queue[0])
					if "ttyCardDispenser" in hermes.reception_queue[0]:		Dispenser(hermes.reception_queue[0])
					if "ttyCardCollector" in hermes.reception_queue[0]:		Collector(hermes.reception_queue[0])

					hermes.reception_queue.pop(0)

				if len(hermes.list_authorizer) > 0:

					if len(hermes.list_authorizer) > 1:	finish_token = True

					if actual_status == "on_console":
						last_text = ""

						if not token_authorizer:

							if hermes.list_authorizer[-1] in token_procesados:	hermes.list_authorizer.pop(-1)

							elif last_token_authorizer == hermes.list_authorizer[-1]['token'] and hermes.list_authorizer[-1]['typeToken'] == "tag":
								inter_sound("" ,f"TOKEN: {hermes.list_authorizer[-1]['token']}, fue autorizado previamente")
								hermes.list_authorizer.pop(-1)

							else:
								logs.info(f"----------------------------------------------------------------")
								logs.info(f"Token list: {hermes.list_authorizer}")
								logs.info(f"Token to authorize: {hermes.list_authorizer[-1]}")
								logs.info(f"Processed Tokens: {token_procesados}")

								if hermes.list_authorizer[-1]['typeToken'] == "qr":

									if setting.machine_identification["type_device"] == "Console_Exit":

										err, token_qr = codification.decoding(str(hermes.list_authorizer[-1]['token']))

										if err:
											logs.info(f"codification.coding: {err} {token_qr}")
											inter_sound("intentelo_de_nuevo" ,"Intentelo de nuevo")
											sleep(1)
										else:
											temp1 = token_qr[:len(token_qr)//2]
											temp2 = token_qr[len(token_qr)//2+1:]

											if temp1 == temp2:	token_qr = temp1

											data	= liq.process_qr(status_card,token_qr)

											if data['approved']:	token_authorizer = data

											else:
												if "Contactese con la administracion del parqueadero" in data['message']:	inter_sound("contactese_con_la_administracion_del_parqueadero" ,data['message'])
												if "Limite de tiempo superado" in data['message']:							inter_sound(["limite_de_tiempo_superado","vaya_al_punto_de_pago"] ,data['message'])
												else:																		inter_sound("intentelo_de_nuevo" ,data['message'])

									logs.info(f"----------------------------------------------------------------")

								else:
									token_authorizer = authorizer_token(hermes.list_authorizer[-1]['typeToken'],hermes.list_authorizer[-1]['token'])

								if len(hermes.list_authorizer) > 0:

									if hermes.list_authorizer[-1] in token_procesados:	logs.info(f"El Token: {hermes.list_authorizer[-1]['token']} ya fue procesado")
									else:												token_procesados.append(hermes.list_authorizer[-1])

									hermes.list_authorizer.pop(-1)

								else:	hermes.list_authorizer =  []

						else:
							hermes.list_authorizer = []

					elif actual_status == "waiting":
						list_print_token = []

						for element in hermes.list_authorizer:	list_print_token.append(f"TOKEN: {element['token']}")

						text = str(list_print_token)[1:-2].replace("'",'')

						if last_text != text:
							last_text = text
							inter_sound("",f"{text}")

				else:
					if finish_token:
						finish_token = False
						logs.info("COLA DE PROCESAMIENTO EN 0")

				if info_plate['plate'] != '' and setting.config_parking['exit_plate'] and info_plate['plate'] != last_plate and actual_status == "on_console":
					last_plate = info_plate['plate']
					logs.info(f"TOKEN: PLATE - {info_plate['plate']}")
					token_authorizer = authorizer_token("plate",info_plate['plate'])

					if not token_authorizer:
						hybrid = True

				if len(hermes.reception_queue) != 0:
					msg_serial(self)

			except Exception as err:
				logs.warning(f"Error: {err}")

			sleep(time_while)











invalid_card = []
def read_mark()->tuple:
	"""[Esta función se encarga de leer y realizar el marcado una tarjeta RFID con la lectora SL025m]

	Returns:
		str ([tuple(bool,str)]): [el booleano es si logró hacer el marcado o no. El dict es el diccionario con los datos de la tarjeta]
	"""
	def reloadCard()->bool:
		"""[Funcion para recargar el carrito y de volver a hacer el marcado en tarjeta cuando algo sale mal]

		Returns:
			bool: [Si pudo o no recargar y hacer el marcado de la tarjeta]
		"""
		hermes.message_queue.insert(0,"ttyCardDispenser b'\x02\x30\x43\x50\x03\x22\x05'") #RECICLER CARD
		status = False

		while not status:

			if "TARJETA RECICLADA" in dispenser_status or "TARJETA EN POSICION" in dispenser_status:
				hermes.message_queue.append("ttyCardDispenser b'\x02\x30\x44\x48\x03\x3D\x05'") #SEND CARD LECTOR
				while not status:

					if dispenser_status == "TARJETA EN LECTORA":
						status = True

					sleep(time_while)

			sleep(time_while)

		return status

	def mark_card(reading = False)->bool:
		"""[Marca la tarjeta en la lectora.]

		Args:
			reading (bool, optional): [lectura previa]. Defaults to False.

		Returns:
			bool: [Si pudo o no hacer el marcado la tarjeta.]
		"""
		try:

			type_vehicle = 0

			if status_card == "Carro":
				type_vehicle = 1
			if status_card == "Moto":
				type_vehicle = 2
    
			if not reading:
				args = {
					"DateEntry":   date_base,
					"cardtype":    0,                                    			# 0: normal, 1: VIP, 2: mensual, 5: Tiquetera, 8: VIP con restricciones
					"idconsole":   setting.machine_identification["id_device"],		# Id que identifica la consola de entrada o salida.
					"agreement":   (),                                   			# Convenio a aplicar
					"cardstatus":  0,                                    			# Normal: 0 dentro, 1 pago, 2 salio. VIP: 3 dentro
					"idpark":      setting.machine_identification["id_parking"],	# Id del parqueadero
					"vehicletype": type_vehicle,                         			# Type vehicle
					"optional2":   0,                                    			# Optional 2 : N/A
					"MinToExit":   0} 			# TIME GRACE
			else:
				args = {
					"DateEntry":   reading["DateEntry"],
					"date":        date_base,
					"cardtype":    0,
					"idconsole":   setting.machine_identification["id_device"],
					"cardstatus":  2,
					"idpark":      setting.machine_identification["id_parking"],
					"vehicletype": reading['vehicletype'],
					"optional2":   0,
					"MinToExit":   0}

		except Exception as e:
			logs.error(f"ERROR EN DATOS DE MARCADO {str(e)}")
		finally:
			return args

	marcado             = False
	trama_desencriptada = False
	id_card             = False

	global token, parent_transaction, card_id, agreement

	try:

		def logeo():
			"""[With the key downloaded in the SL025M reader, it will log in]
			If you can not log in with the key, it will give a communication error message and try again
			Returns:
				status
			"""
			hermes.comando_mux = tramasSL.loginSectorStoredKey() 												#* OPTIENE LA TRAMA PARA LOGUEARSE EN LA TARJETA
			cont               = 0

			while True:
				if hermes.response_card != b"":
					resp_logeo = hermes.response_card
					ver_trama  = tramasSL.verificarTrama(resp_logeo)
					logs.info(f"LOGEO: {resp_logeo} | {ver_trama}")
					hermes.response_card = b""
					return ver_trama
				else:
					cont += 1

					if cont == 20:
						inter_sound("","No se ha establecido comunicacion con la lectora de tarjetas ocasionales - Logeo")
						insta.mqtt_pub("devicestatus","warning",f"No se ha establecido comunicación con la lectora de tarjetas ocasionales  - Logeo")
						sleep(1)
						return "ERROR"

				sleep(time_while)

		resp_logeo = logeo()

		if resp_logeo != "Operacion Exitosa":
			logs.info("SEGUNDO INTENTO")
			resp_logeo = logeo()


		if resp_logeo == "Operacion Exitosa":

			hermes.comando_mux = tramasSL.selectCard() 															#* LLAMA LA TRAMA PARA OBTENER EL ID DE LA TARJETA

			while True:

				if hermes.response_card != b"":
					response_id_card = tramasSL.selectCard(hermes.response_card) 								#* OBTIENE EL ID DE LA TARJETA

					logs.info(f"CARD: {hermes.response_card} | {response_id_card}")
					hermes.response_card = b""

					if "ERROR" in response_id_card:
						logs.warning("NO SE PUDO INDENTIFICAR LA TARJETA")
						break
					else:

						if setting.machine_identification["type_device"] == "Console_Exit":
							hermes.comando_mux = tramasSL.readDataBlock()											#* LLAMA LA TRAMA PARA LEER LA TARJETA

							while True:

								if hermes.response_card != b"":
									response_lectura = tramasSL.readDataBlock(hermes.response_card) 				#* OBTENER LA LECTURA DE LA TARJETA
									logs.info(f"READ: {hermes.response_card} | {response_lectura}")
									hermes.response_card = b""

									if response_lectura == False:
										logs.warning("ERROR EN LA LECTURA -")
										break

									trama_desencriptada = parkingSL.lectura(response_id_card, response_lectura)	#* DESENCRIPTA LA INFORMACION DE LA TARJETA

									mark_card_info, sound, text, parent_transaction, card_id, agreement = liq.process_card(trama_desencriptada) #TODO: LEE LA TARJETA PARA SOLICITAR ESTATUS DE LA LECTURA DE LA TARJETA
									inter_sound(sound,text)
									sleep(len(text)/30)
									break

								sleep(time_while)

						else:
							id_card        = parkingSL.getSerialCard(response_id_card)
							mark_card_info = True


						if mark_card_info:
							marcado = False
							tries   = 0

							if setting.machine_identification["type_device"] == "Console_Exit": 	#TODO: OBTIENE EL TOKEN DE LA LECTURA Y MARCA LA TARJETA TENIENDO EN CUENTA LA INFORMACION YA EXISTENTE DE LA TARJETA
								seconds_base = datetime.strptime(trama_desencriptada['DateEntry'], "%Y-%m-%d %H:%M:%S")
								seconds_base = seconds_base - origen
								seconds_base = int(seconds_base.total_seconds()+18000)
								token        = f"{trama_desencriptada['idconsole']}-{seconds_base}-{trama_desencriptada['serialCard']}"
								data_mark    = mark_card(trama_desencriptada)
							else:
								data_mark = mark_card()

							while not marcado:

								resp_logeo = logeo()

								tries += 1
								if tries == 3:
									break

								if resp_logeo == "Operacion Exitosa":
									for x in data_mark:
										logs.info(f"{x}	- {data_mark[x]}")

									data_encriptada = parkingSL.write(response_id_card,data_mark)
									logs.info(f"ENCRYPTED INFO: {data_encriptada}")

									hermes.comando_mux = trama = tramasSL.writeDataBlock(data_encriptada)

									while True:

										if hermes.response_card != b"":
											response_trama = tramasSL.verificarTrama(hermes.response_card)
											logs.info(f"VERIFY:  {hermes.response_card} - {response_trama}")

											if response_trama != "Operacion Exitosa":
												logs.info("LE FALLE AL MUNDO")
											else:

												hermes.comando_mux = tramasSL.readDataBlock()
												while True:

													if hermes.response_card != b"":

														if hermes.response_card[4:-1] == trama[4:-1]:
															logs.info("VERIFICACION REALIZADA = IGUALES")
															marcado = True
															break
														else:
															logs.warning(f"{hermes.response_card[4:-1]} - {trama[4:-1]}")

													sleep(time_while)

											break

										sleep(time_while)

								sleep(time_while)

							break
						else:
							break

				sleep(time_while)

		else:
			logs.warning("NO ME PUDE LOGEAR")
			if setting.machine_identification["type_device"] == "Console_Entry":
				status_reload_card = reloadCard()
				if status_reload_card:
					hermes.comando_mux = tramasSL.loginSectorStoredKey() 											#* OPTIENE LA TRAMA PARA LOGUEARSE EN LA TARJETA
					logs.info(f"ERROR	LOGUEO: {hermes.comando_mux}")

	except Exception as err:
		marcado = False
		logs.warning(f"ERROR: {err}")
	finally:

		if setting.machine_identification["type_device"] == "Console_Exit":
			return marcado, trama_desencriptada
		else:
			logs.info(f"reloadCard {marcado} - {id_card}")
			return marcado, id_card


dispenser_status = collector_status = "INITIAL"

def key_reader() -> None:
	"""[Download key to reader SL025M]
		If the key cannot be lowered, it will give a communication error message and it will be tried again
	"""
	global descargar_llave

	hermes.comando_mux = tramasSL.downloadKeyIntoReader(setting.config_parking['key'])					#* DESCARGAR LA LLAVE DENTRO DE LA LECTORA
	cont               = 0

	while not descargar_llave:

		if hermes.response_card != b"":
			download_key = tramasSL.verificarTrama(hermes.response_card)								#* VERIFICA LA TRAMA DE RESPUESTA DE LA DESCARGA DE LA LLAVE
			logs.info(f"KEY:	{hermes.response_card} - {download_key}")
			hermes.response_card = b""

			if download_key == "Operacion Exitosa":
				descargar_llave = True
			else:
				hermes.comando_mux = tramasSL.downloadKeyIntoReader(setting.config_parking['key'])		#* DESCARGAR LA LLAVE DENTRO DE LA LECTORA

		else:
			cont += 1
			if cont == 20:
				inter_sound("","No se ha establecido comunicacion con la lectora de tarjetas ocasionales - LLAVE")
				insta.mqtt_pub("devicestatus","warning",f"No se ha establecido comunicación con la lectora de tarjetas ocasionales  - LLAVE")
				cont = 0
				sleep(1)
				hermes.comando_mux = tramasSL.downloadKeyIntoReader(setting.config_parking['key'])		#* DESCARGAR LA LLAVE DENTRO DE LA LECTORA

		sleep(time_while)



def verify_device() -> None:
	global descargar_llave

	descargar_llave = False

	while True:

		if not descargar_llave:
			key_reader()

		if "CardDispenser" in setting.devices:
			if dispenser_status == "INITIAL":
				inter_sound("","No se ha establecido comunicacion con el carro dispensador")
				insta.mqtt_pub("devicestatus","warning",f"No se ha establecido comunicación con el carro dispensador")

			else:
				inter_sound("","Comunicación establecida con el carro dispensador")
				insta.mqtt_pub("devicestatus","info",f"Comunicación establecida con el carro dispensador")
				inter_sound("","Esperando vehiculo")
				break

		if "CardCollector" in setting.devices:
			if collector_status == "INITIAL":
				inter_sound("","No se ha establecido comunicacion con el carro colector")
				insta.mqtt_pub("devicestatus","warning",f"No se ha establecido comunicación con el carro colector")

			else:
				inter_sound("","Comunicación establecida con el carro colector")
				insta.mqtt_pub("devicestatus","info",f"Comunicación establecida con el carro colector")
				inter_sound("","Esperando vehiculo")
				break

		sleep(time_while)


class card_dispenser(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global init_button, status_s, card_retired, dispenser_status, card_id, card_transaction

		activate_position = True

		verify_device()

		while True:

			if dispenser_status == "TARJETA EN POSICION" and activate_position:
				hermes.message_queue.insert(0,"ttyCardDispenser b'\x02\x30\x44\x48\x03\x3D\x05'") #SEND CARD LECTOR
				activate_position = False

			if actual_status == "on_console" and not token_authorizer:

				if dispenser_status == "TARJETA EN LECTORA":
					card_retired  = "INIT"
					reading       = False
					mark          = False

					while not mark:
						mark, reading = read_mark()

					card_id     = reading[0]
					init_button = True

					logs.info(f"DISPENSE CARD:	{reading[0]} - STATUS BUTTON {init_button}")

					while True:
						sleep(time_while/12)
						actual_time = datetime.now()

						if actual_status == "on_console" and not token_authorizer:

							if hermes.pines_queue[console_button]['status'] == 1:
								card_transaction	= True
								hermes.message_queue.insert(0,"ttyCardDispenser b'\x02\x30\x44\x43\x03\x36\x05'") #send_card_out_from_ready
								inter_sound("tome_la_tarjeta","Tome la tarjeta")

								while True:

									if dispenser_status != "TARJETA EN LECTORA":

										while True:

											if "TARJETA RECICLADA" in dispenser_status or dispenser_status == "SIN ESTADO":
												card_retired = "not_approved"
												break

											elif (hermes.pines_queue[loopA2]['status'] == 0 and (actual_time - hermes.pines_queue[loopA2]['time']) > time_loop) and (hermes.pines_queue[loopA1]['status'] == 0 and (actual_time - hermes.pines_queue[loopA1]['time']) > time_loop):
												hermes.message_queue.insert(0,"ttyCardDispenser b'\x02\x30\x43\x50\x03\x22\x05'") #RECICLER CARD
												card_retired = "not_approved"
												break

											elif dispenser_status == "TARJETA EN POSICION" or dispenser_status == "DISPENSADOR LISTO" or dispenser_status == "DISPENSADOR VACIO":
												insta.mqtt_pub("devicestatus","info",f"TARJETA OCASIONAL")
												card_retired = "approved"
												break

											sleep(time_while)


										if card_retired == "not_approved":

											while True:

												if "TARJETA RECICLADA" in dispenser_status:
													insta.mqtt_pub("devicestatus","info","Tarjeta reciclada")
													logs.warning("-------------------------------> SE RECICLO CORRECTAMENTE")
													break
												elif "TARJETA EN POSICION" in dispenser_status:
													insta.mqtt_pub("devicestatus","warning","Tarjeta perdida")
													logs.critical("-------------------------------> TARJETA PERDIDA")
													break
												break

												sleep(time_while/6)

										logs.info(f"DESHABILITARE EL ESTADO PARA SACAR TARJETA 2")
										init_button			= False
										activate_position	= True
										break

									sleep(time_while/6)

								break

							if (hermes.pines_queue[loopA2]['status'] == 0 and (actual_time - hermes.pines_queue[loopA2]['time']) > (time_loop)) and (hermes.pines_queue[loopA1]['status'] == 0 and (actual_time - hermes.pines_queue[loopA1]['time']) > (time_loop)):
								logs.info(f"DESHABILITARE EL ESTADO PARA SACAR TARJETA 2")
								init_button = False
								sleep(2)
								break
						else:
							break

			elif "ERROR" in dispenser_status or "ATASCAMIENTO" in dispenser_status or "SIN ESTADO" == dispenser_status or "DISPENSADOR VACIO" == dispenser_status or "SIN TARJETAS" == dispenser_status:
				while True:

					if dispenser_status == "DISPENSADOR VACIO" or dispenser_status == "SIN TARJETAS":
						audio = "no_hay_tarjetas"
						texto = "NO HAY TARJETAS"
						insta.mqtt_pub("devicestatus","warning",texto)

					if "ERROR" in dispenser_status or "SIN ESTADO" == dispenser_status or "ATASCAMIENTO" == dispenser_status:
						hermes.message_queue.insert(0,"ttyCardDispenser b'\x02\x30\x44\x48\x03\x3D\x05'") #SEND CARD LECTOR
						audio = ["lo_sentimos","punto_fuera_de_servicio"]
						texto = "ERROR EN DISPENSADOR, PUNTO FUERA DE SERVICIO"
						insta.mqtt_pub("devicestatus","error",f"Error: {texto}")

					if "TARJETA EN POSICION" in dispenser_status or "TARJETA EN LECTORA" in dispenser_status:
						insta.mqtt_pub("devicestatus","warning",f"SOLUCIONADO: {texto}")
						break

					inter_sound(audio,texto)
					sleep(len(texto)/10)

			sleep(time_while/6)

class card_collector(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		verify_device()

		count = 0

		while True:

			if actual_status == "on_console":

				if collector_status == "TARJETA EN LECTORA":
					inter_sound(["un_momento_por_favor","procesando_tarjeta"], " UN MOMENTO POR FAVOR, PROCESANDO TARJETA")
					insta.mqtt_pub("devicestatus","info","Tarjeta en lectora")

					reading	= False
					mark	= False
					tries	= 0

					while (not mark and not reading) or collector_status != "TARJETA EN LECTORA":
						sleep(time_while)

						tries += 1
						mark, reading = read_mark()

						if type(reading) == bool:	mark = False

						if tries >= 5:
							inter_sound("error_en_la_tarjeta", "TARJETA NO RECONOCIDA")
							insta.mqtt_pub("devicestatus","warning","Tarjeta no reconocida")
							sleep(2)
							break

					if mark:
						hermes.message_queue.insert(0,"ttyCardCollector b'\x02\x43\x50\x03\x12'")
						hermes.message_queue.insert(0,"ttyCardCollector b'\x02\x43\x50\x03\x12'")

						while collector_status == "TARJETA EN LECTORA":	sleep(time_while*2)

						insta.mqtt_pub("devicestatus","info","Ingresando Tarjeta")

					else:
						hermes.message_queue.append("ttyCardCollector b'\x02\x44\x43\x03\x06'")
						hermes.message_queue.append("ttyCardCollector b'\x02\x44\x43\x03\x06'")
						tries = 0

						while collector_status == "TARJETA EN LECTORA":
							tries += 1

							if tries == 5:	hermes.message_queue.append("ttyCardCollector b'\x02\x44\x43\x03\x06'")

							sleep(1)

						insta.mqtt_pub("devicestatus","warning","Devolviendo tarjeta")

				elif  "ATASCO" in collector_status or collector_status == "RETIRE LA TARJETA":

					count += 1
					if count == 5:
						insta.mqtt_pub("devicestatus","warning","ERROR EN LA TARJETA")
						hermes.message_queue.append("ttyCardCollector b'\x02\x44\x43\x03\x06'")
						count = 0
						inter_sound("tarjeta_no_permitida", "TARJETA NO PERMITIDA")

					sleep(1)
			sleep(time_while)



def action(action:str,petitionID):
	logs.info(f"EVENT MONITORING: {action}: {petitionID}")
	status	= True
	msg		= "Comando realizado"

	if action == "openBarrier":
		insta.mqtt_pub("devicestatus","warning","ABRIENDO BARRERA - COMANDO")
		barrier.monitorin(True)
		barrier.start()
		insta.mqtt_pub("devicestatus","warning","BARRERA ABIERTA - COMANDO")

	elif action == "closeBarrier":
		insta.mqtt_pub("devicestatus","warning","CERRANDO BARRERA - COMANDO")
		barrier.monitorin(True)
		barrier.act_down()
		insta.mqtt_pub("devicestatus","warning","BARRERA CERRADA - COMANDO")

	elif action == "KeepOpenBarrier":
		insta.mqtt_pub("devicestatus","warning","ABRIENDO BARRERA - COMANDO")
		barrier.monitorin(False)
		barrier.act_up()
		insta.mqtt_pub("devicestatus","warning","BARRERA ABIERTA - COMANDO")
		insta.mqtt_pub("devicestatus","error","SE MANTENDRA BARRERA ABIERTA")

	else:
		logs.info(f"{action}: it is not a possible action")
		status = False
		msg    = "Comando no reconocido"

	return petitionID, status, msg


class service_mqtt(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.mqttc = mqtt.Client(transport="websockets")

	def run(self):

		def on_connect(mqttc, obj, flags, rc):	pass

		def on_message(mqttc, obj, msg):

			try:
				#logs.info(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
				response = json.loads(msg.payload)
				if msg.topic == "commands" and response['deviceId'] == setting.machine_identification['id_device']:
					response = action(response['command'],response['petitionID'])
					insta.mqtt_pub("commands","",response)

			except Exception as err:	pass
			finally:					pass

		def on_publish(mqttc, obj, mid):	pass

		def on_subscribe(mqttc, obj, mid, granted_qos):	pass

		def on_log(mqttc, obj, level, string):	pass

		self.mqttc.on_connect	= on_connect
		self.mqttc.on_message	= on_message
		self.mqttc.on_publish	= on_publish
		self.mqttc.on_subscribe	= on_subscribe
		self.mqttc.on_log		= on_log

		try:						self.mqttc.connect(setting.mqtt['broker'], setting.mqtt['port'], 10)
		except Exception as err:	logs.critical("ERROR MQTT")

		self.mqttc.subscribe([('commands', 1),('devicestatus', 0)])

		self.mqttc.loop_forever()

	def mqtt_pub(self,topic,level,msg):
		try:
			self.mqttc.connect(setting.mqtt['broker'], setting.mqtt['port'], 10)

			if topic == "commands":		message = json.dumps({"petitionID":msg[0], "status":msg[1], "message":msg[2]})
			if topic == "devicestatus":	message = json.dumps({"scope":level, "message":msg, "datetime":str(datetime.now()), "device":setting.machine_identification['id_device']})

			result		= self.mqttc.publish(topic, message,0)
			msg_logs	= f"MSG: {msg}"

			if level == "info":			logs.info(msg_logs)
			elif level == "warning":	logs.warning(msg_logs)
			elif level == "error":		logs.error(msg_logs)

		except Exception as err:		logs.info(f"{err} | Topic: {topic} | MSG: {level}:{msg}")




#* ::::::::::::::::::::::::::::> Inicializador de hilos
service_mqtt_th = service_mqtt()
service_mqtt_th.start()
insta = service_mqtt()

organization_status = organization_status()
organization_status.start()

machine_process = machine_process()
machine_process.start()

if "CardDispenser" in setting.devices:
	card_dispenser = card_dispenser()
	card_dispenser.start()

if "CardCollector" in setting.devices:
	card_collector = card_collector()
	card_collector.start()










# ::::::::::::::::::::::::::::> SOCKET TYPE - CLIENT
@sio.event
def connect_error(data):
	logs.info("The connection failed!")
	sleep(2)
	sio.connect('http://localhost:3100')

@sio.event
def plate(plate)-> None:
	global info_plate

	try:
		if plate['plate'] != "NoLicensePlate":

			if type(plate['confidence']) == str:	plate['confidence'] = int(plate['confidence'])

			plate['img'] = plate.get('img')

			if info_plate == "":
				info_plate = plate
				logs.info(f"ACTUAL PLATE: {info_plate['plate']} - {info_plate['confidence']}")
			else:

				if float(plate['confidence']) > float(info_plate['confidence']):
					info_plate = plate
					logs.info(f"ACTUAL PLATE: {info_plate['plate']} - {info_plate['confidence']}")

	except Exception as err:
		logs.warning(err)

sio.connect('http://localhost:3100',wait_timeout = 5)