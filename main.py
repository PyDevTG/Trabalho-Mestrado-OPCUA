#main-pub-subs-contador.py
# main.py

# pub contador - subs flag

from umqtt.simple import MQTTClient
from machine import Pin
from time import sleep
import network

print('Wifi connected !')

# led setup
led = Pin(2, Pin.OUT)

CLIENT_NAME = 'UEA-MPEE-sic-est32'

#BROKER_ADDR = "192.168.0.167"
BROKER_ADDR = "lse.dev.br"
#BROKER_ADDR = "131.255.82.115"
#BROKER_ADDR = "broker.mqttdashboard.com"
#BROKER_ADDR = "192.168.0.23"
#BROKER_ADDR = "public-mqtt-broker.bevywise.com"

mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, keepalive=0)

print("Connecting to MQTT server... ", end="")

    
print('MQTT connected !')

SUB_TOPIC = b'ServerOPC/flag'
PUB_TOPIC = b'ServerOPC/counter'

flag_state = 0 # Initial state of the button (off)
contador = 0
incr = 1 # começa incrementando
led.value(0)

    
def flag(topic, msg):
    
    global flag_state
    
    m = msg.decode().strip().lower()
    
    if m in ("1", "true", "t", "on", "yes", "y"):
        flag_state = 1
        
    if m in ("0", "false", "f", "off", "no", "n"):
        flag_state = 0
        
    led.value(flag_state)
    
    #print(f"[MQTT] Flag_state = {flag_state}")




def reconnect_mqtt():
    """Tenta reconectar ao broker MQTT."""
    global mqttc
    while True:
        try:
            print("Tentando conectar ao broker MQTT...")
            mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, keepalive=10)
            
            mqttc.set_callback(flag)
            mqttc.connect()
            mqttc.subscribe(SUB_TOPIC)
            # mqtt subscription
            mqttc.set_callback(flag)
            mqttc.subscribe(SUB_TOPIC)

            mqttc.publish(PUB_TOPIC, str(contador)) # contador inicialmente zerado
            print('Contador:', contador)
            print("✅ Conectado ao broker MQTT!")
            return
        except Exception as e:
            print(f"⚠️ Erro MQTT: {e}")
            print("Tentando novamente em 5 segundos...")
            sleep(5)

try:
    reconnect_mqtt()
except Exception as e:
    print(f"⚠️ Erro de loop principal: {e}")
    reconnect_mqtt()
ultimo_valor_publicado = None

while True:
    try:

        mqttc.check_msg()

        # Check for a flag state change
        if flag_state == 1:
            
            contador = contador + incr
            
            if contador >= 9:
                incr = -1
                
            if contador < 1:
                incr = 1

            if contador != ultimo_valor_publicado:
                mqttc.publish(PUB_TOPIC, str(contador))
                ultimo_valor_publicado = contador
                print("Publicado contador:", contador)
            
        print('Flag: ', flag_state, ' Contador:', contador)

        sleep(1.0)
    except Exception as e:
        print(f"⚠️ Erro de loop principal: {e}")
        reconnect_mqtt()
        

