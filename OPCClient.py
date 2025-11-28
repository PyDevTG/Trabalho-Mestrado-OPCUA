from opcua import Client,ua
import time
import threading

class OPCUAClientHandler(threading.Thread):
    
    def __init__(self, opc_url="opc.tcp://localhost:4840", mqtt_client=None):
        """
        Classe que gerencia conexão OPC UA com reconexão automática.
        Pode receber um cliente MQTT já instanciado (opcional).
        """
        print("Thread OPC Cliente Iniciada")
        super().__init__()
        self.opc_url = opc_url
        self.mqtt_client = mqtt_client   # objeto MQTT já criado e conectado externamente
        self.client = None
        self.connected = False
        self._running = True
        self.log = ""
        self.daemon = True  # encerra junto com o programa principal
        self.logOPC=""
        self.tries = 0

    # ======================================
    # 🔌 CONEXÃO OPC
    # ======================================
    def connect_opc(self):
        """Tenta conectar ao servidor OPC UA até conseguir."""
        self.logOPC= f" Tentando se conectar ao servidor OPC: {self.opc_url}"
        try:
                #print("estou na connect opc")
                self.client = Client(self.opc_url, timeout=1)
                self.client.connect()
                self.connected = True
                self.logOPC= f"✅ Conectado ao servidor OPC: {self.opc_url}"
                print(self.log)
        except Exception as e:
                self.connected = False
                self.logOPC= f"❌ Falha ao conectar OPC: {e}"
                print(self.log)
               
        time.sleep(0.1)

    def run(self):
        """Thread principal: monitora conexão OPC e reconecta se cair."""
        self.tries = 0
        self.connect_opc()

        while self._running:
            
            try:
                if self.connected:
                    pass
                  
                    #self.logOPC=("Conectado ao servidor OPC")
                else:
                    self.connect_opc()
                    self.logOPC=("🔄 Tentando reconectar ao servidor OPC...")
                    
                    self.tries = self.tries+1
            except Exception as e:
                self.logOPC=(f"⚠️ Conexão OPC perdida: {e}")
                self.connected = False
                try:
                    self.client.disconnect()
                except:
                    pass
            time.sleep(0.1)
            

    def stop(self):
        """Para a thread e desconecta com segurança."""
        self._running = False
        if self.client:
            try:
                self.client.disconnect()
                print("🛑 Cliente OPC desconectado.")
            except:
                pass
        self.connected = False
       # ======================================
    # 📖 LEITURA DE VARIÁVEL OPC
    # ======================================
    def read_node_value(self, node_id: str):
        """Lê o valor de um nó OPC UA (NodeId)."""
        if not self.connected or not self.client:
            self.logOPC=("⚠️ Cliente OPC não conectado.")
            self.connect_opc()
            return None
        try:
            node = self.client.get_node(node_id)
            value = node.get_value()
            #print(f"📘 Leitura [{node_id}] = {value}")
            return value
        except Exception as e:
            #print(f"❌ Erro ao ler o nó {node_id}: {e}")
            self.connected = False
            return None
     # ======================================
    # ✏️ ESCRITA DE VARIÁVEL OPC
    # ======================================
    def write_node_value(self, node_id: str, value):
        """Escreve um valor em um nó OPC UA (NodeId)."""
        if not self.connected or not self.client:
            self.logOPC=("⚠️ Cliente OPC não conectado. Não foi possível escrever.")
            return False
        try:
            node = self.client.get_node(node_id)
            # Detecta tipo de dado automaticamente
            variant = ua.Variant(value, self._infer_variant_type(value))
            node.set_value(variant)
            self.logOPC=(f"✅ Escrita [{node_id}] = {value}")
            return True
        except Exception as e:
            self.logOPC=(f"❌ Erro ao escrever no nó {node_id}: {e}")
            self.connected = False
            return False

    def _infer_variant_type(self, value):
        """Tenta deduzir o tipo do valor para o Variant OPC UA."""
        if isinstance(value, bool):
            return ua.VariantType.Boolean
        elif isinstance(value, int):
            return ua.VariantType.Int32
        elif isinstance(value, float):
            return ua.VariantType.Float
        elif isinstance(value, str):
            return ua.VariantType.String
        else:
            return ua.VariantType.String

if __name__ == "__main__":
    opc_thread = OPCUAClientHandler("opc.tcp://localhost:4840")
    opc_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        opc_thread.stop()