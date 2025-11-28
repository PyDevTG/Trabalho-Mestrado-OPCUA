import sys
import threading
import time
from opcua import Server, ua
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
import paho.mqtt.client as mqtt

#import module
import OPCClient

from opcua import Client, ua


# =====================================
# ⚙️ CONFIGURAÇÕES DO MQTT
# =====================================
BROKER = ""#"192.168.0.46"
PORT = None
USERNAME = ""
PASSWORD = ""
TOPIC_COUNTER = "ServerOPC/counter"
TOPIC_FLAG = "ServerOPC/flag"
OPC_ENDPOINT =  ""


# NodeIds (ajuste conforme o seu servidor)
FLAG_NODE_ID = ""
CONTADOR_NODE_ID = ""

# =====================================
# 🔌 CLASSE MQTT
# =====================================
class MQTTClientHandler(threading.Thread):
    def __init__(self, server_thread,cred=0):
        super().__init__()
        self.cred=cred
        self.LogMqtt = ""
        self.LogMsg=""
        self.server_thread = server_thread
        client_id = "EngMestrado"
        
       
        
        self.client = mqtt.Client(client_id=client_id)
        if(self.cred==1):
           self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        #self.client.on_log = self.on_log
        self._running = True
        self._connected = False
        self.daemon = True
        self.status = False
        self.lastvalue = 0

    # --- CALLBACKS ---
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            #print("✅ Conectado ao broker MQTT!")
            self.LogMqtt = ("✅ Conectado ao broker MQTT!")
            client.subscribe([(TOPIC_COUNTER, 0), (TOPIC_FLAG, 0)])
            #print(f"📡 Inscrito em: {TOPIC_COUNTER}, {TOPIC_FLAG}")
            self.LogMqtt = (f"📡 Inscrito em: {TOPIC_COUNTER}, {TOPIC_FLAG}")
        else:
            
            #print(f"❌ Falha na conexão MQTT. Código: {rc}")
            self.LogMqtt = (f"❌ Falha na conexão MQTT. Código: {rc}")

    def on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            self.LogMqtt = ("⚠️ Desconectado inesperadamente do broker MQTT. Tentando reconectar...")
            #print("⚠️ Desconectado inesperadamente do broker MQTT. Tentando reconectar...")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip()
        topic = msg.topic
        self.LogMsg = (f"[MQTT] Tópico '{topic}' Msg: {payload}")
        
        #flag_node = self.server_thread.get_node(FLAG_NODE_ID)
        #contador_node = self.server_thread.get_node(CONTADOR_NODE_ID)

        if topic == TOPIC_COUNTER:
            try:
                value = int(payload)
                #print("Value",value)
                #print("lastValue",self.lastvalue)
                if(value!=self.lastvalue):
                    self.server_thread.write_node_value(CONTADOR_NODE_ID,value)
                    self.lastvalue = value
                
                self.LogMqtt = (f"📨 Counter atualizado via MQTT: {value}")
                #print(f"📨 Counter atualizado via MQTT: {value}")
            except ValueError:
                #print(f"⚠️ Valor inválido em {topic}: {payload}")
                self.LogMqtt = (f"⚠️ Valor inválido em {topic}: {payload}")

        time.sleep(0.1)

    # --- LOOP PRINCIPAL ---
    def run(self):
        while self._running:
            if not self._connected:
                try:
                    print("🔌 Tentando conectar ao broker MQTT...")
                    self.LogMqtt = ("Tentando conectar ao broker MQTT..")
                    self.client.connect(BROKER, PORT, keepalive=60)
                    self.client.loop_start()  # roda em segundo plano
                except Exception as e:
                    self.LogMqtt = (f"❌ Falha na conexão MQTT. Código: {e}")
                    #print(f"❌ Erro MQTT: {e}. Tentando novamente em 5s...")
                    #time.sleep(5)
            time.sleep(0.25)

    def stop(self):
        self._running = False
        if self._connected:
            self.client.loop_stop()
            self.client.disconnect()
        print("🛑 Cliente MQTT parado.")
        self.LogMqtt = ("🛑 Cliente MQTT parado.")

    # --- Envio opcional dos valores OPC para o broker ---
    def publish_value1(self):
        if self._connected and self.server_thread.connected:
            try:
                counter = self.server_thread.counter_var.get_value()
                flag = self.server_thread.Flag_var.get_value()
                self.client.publish(TOPIC_COUNTER, counter)
                self.client.publish(TOPIC_FLAG, str(flag))
            except Exception as e:
                print(f"⚠️ Erro ao publicar: {e}")
                self.LogMqtt = (f"⚠️ Erro ao publicar: {e}")
    def publish_values(self):
        
        if self._connected:
            try:
                # Lê os valores atuais do servidor OPC
                flag = self.server_thread.read_node_value(FLAG_NODE_ID)
                counter = self.server_thread.read_node_value(CONTADOR_NODE_ID)
                

                # Inicializa variáveis de controle se ainda não existirem
                if not hasattr(self, "_last_counter"):
                    self._last_counter = None
                    self._last_flag = None

                # Só publica se o valor do contador mudou
                if counter != self._last_counter:
                    #self.client.publish(TOPIC_COUNTER, counter)
                    self._last_counter = counter
                    self.LogMqtt = f"📤 Counter publicado: {counter}"
                    
                    print("publica contador")

                # Só publica se a flag mudou
                if flag != self._last_flag:
                    self.client.publish(TOPIC_FLAG, str(flag))
                    self._last_flag = flag
                    self.LogMqtt = f"📤 Flag publicada: {flag}"
                    print("publica Flag")

            except Exception as e:
                self.LogMqtt = f"⚠️ Erro ao publicar: {e}"
                print(f"⚠️ Erro ao publicar: {e}")

    def on_log(self, client, userdata, level, buf):
        self.LogMqtt = f"[MQTT LOG] {buf}"
        print(self.LogMqtt)


# =====================================
# 🖥️ INTERFACE GRÁFICA
# =====================================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, server_thread, mqtt_thread):
        super().__init__()
        uic.loadUi("interface.ui", self)
        self.tabWidget.setCurrentIndex(0)
        self.server_thread = server_thread
        self.mqtt_thread = mqtt_thread
        self.logReceip = ""

        # Atualiza a GUI a cada 1s
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(200)
           # Atualiza a GUI a cada 1s
        self.timerLog = QTimer()
        self.timerLog.timeout.connect(self.logUpdate)
        self.timerLog.start(200)

        self.btn_toggle.clicked.connect(self.toggle_flag) 

    def update_values(self):
        contador = ""
        flag = ""
        try:
            if(self.server_thread.connected==True):
                flag = self.server_thread.read_node_value(FLAG_NODE_ID)
                contador = self.server_thread.read_node_value(CONTADOR_NODE_ID)
        except:
            pass
        

        self.lCounter.setText(f"{contador}")
        self.lFlag.setText("True" if flag==True else "False")
        self.LogMqttMsg.setText(self.mqtt_thread.LogMsg)
        
        if(self.mqtt_thread._connected==True):
            self.StatusMQTT.setText("Conectado ao Broker")
            self.StatusMQTT.setStyleSheet("color: black; background-color: rgb(85, 255, 0); border: 1px solid white;")
        else:
            self.StatusMQTT.setText("Não conectado ao Broker")
            self.StatusMQTT.setStyleSheet("color: black; background-color:rgb(255, 25, 0);; border: 1px solid white;")
        if(OPCClient_thread.connected):
            self.StatusServer.setText("OPC Client is Connected" )
            self.StatusServer.setStyleSheet("color: black; background-color:rgb(25, 255, 0);; border: 1px solid white;")
        else:
            self.StatusServer.setText("OPC Client is not Connected")
            self.StatusServer.setStyleSheet("color: black; background-color:rgb(255, 25, 0);; border: 1px solid white;")

       

        # opcional: publica periodicamente no MQTT
        self.mqtt_thread.publish_values()

    def toggle_flag(self):
        if(self.server_thread.connected==True):
            atual = self.server_thread.read_node_value(FLAG_NODE_ID)
            novo_valor = not atual
            self.server_thread.write_node_value(FLAG_NODE_ID,novo_valor)
            
            #print(f"🔁 Flag alternada manualmente para: {novo_valor}")
            self.update_values()
        else:
             self.server_thread.logOPC="Falha ao atualizar a flag o cliente OPC nao esta conectado"
            
    def logUpdate(self):
        if(self.server_thread.tries>=3):
            self.server_thread.tries = 0
        self.LogMqtt.setText(mqtt_thread.LogMqtt)
        self.LogOpc.setText(OPCClient_thread.logOPC)

def ler_configuracoes(caminho: str) -> dict:
    config = {}
    with open(caminho, 'r') as arquivo:
        for linha in arquivo:
            if '=' in linha:
                chave, valor = linha.strip().split('=')
                config[chave] = valor
    return config



conf = ler_configuracoes("config.txt")

BROKER = conf.get("broker", "0.0.0.0")
#PORT = 1883
USERNAME = conf.get("user", "Thiago")
PASSWORD = conf.get("pass", "123456")
OPC_ENDPOINT = conf.get("endpoint", "opc.tcp://localhost:4840")
CREDENTIALS=int(conf.get("credentials", 0))
PORT=int(conf.get("port", 1883))
namespaceFlag=conf.get("flag_ns", "ns=1")
IdFlag=conf.get("flag_nid", "i=1000")
namespaceCnt=conf.get("flag_ns", "ns=1")
IdCnt=conf.get("flag_nid", "i=1001")
CONTADOR_NODE_ID=namespaceCnt+";"+IdCnt
FLAG_NODE_ID = namespaceFlag+";"+IdFlag
TOPIC_COUNTER = conf.get("topic_counter", "ServerOPC/counter")
TOPIC_FLAG = conf.get("topic_flag", "ServerOPC/flag")

print(CONTADOR_NODE_ID)


# =====================================
# ▶️ EXECUÇÃO PRINCIPAL
# =====================================
if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)

    OPCClient_thread = OPCClient.OPCUAClientHandler(opc_url = "opc.tcp://localhost:4840")
    OPCClient_thread.start()

    mqtt_thread = MQTTClientHandler(OPCClient_thread,cred=CREDENTIALS)
    mqtt_thread.start()

    
    window = MainWindow(OPCClient_thread, mqtt_thread)
    window.show()

    window.LogMqtt.setText(mqtt_thread.LogMqtt) 

    
    window.addbroker.setText(BROKER)
    window.PortB.setText(str(PORT))
    
    

    exit_code = app.exec_()

    # Encerramento limpo
    mqtt_thread.stop()
    OPCClient_thread.stop()
    OPCClient_thread.join()
    mqtt_thread.join()
    sys.exit(exit_code)
