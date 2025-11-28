Este projeto foi desenvolvido para implementar a comunicação entre um Esp32 e um Servidor OPC UA usando um servidor Broker MQTT como gateway principal na troca de dados entre Esp32 e servidor OPCUA
dentro do servidor tem 2 variaveis sendo:
1 Flag booleana de controle
2 Contador Int16

foi implementado uma logica para testar o funcionamento da troca de dados:
se flag = True Esp32 inscrementa ou decrementar um contador circular 0-9-0
se flag=false Contador mantem o ultimo valor escrito

O gateway foi desenvolvido em python juntamente com a interface de usuário que foi implementada em Pyqt5 usandoo qtdesigner
Dados de comunicação, e configuração de variaveis pode ser feito alterando seus valores no arquivo config.txt


ESP32 ↔ OPC UA Integration via MQTT
Descrição


O sistema inclui:

ESP32 rodando MicroPython, responsável pela captura de variáveis e publicação via MQTT;
Broker MQTT para comunicação entre ESP32 e gateway;
Gateway em Python com interface PyQt5, sincronizando dados com o servidor OPC UA.

Funcionalidades
Comunicação bidirecional ESP32 ↔ OPC UA via MQTT.
Publicação seletiva de dados, reduzindo tráfego de rede.
Controle remoto da lógica do contador por meio de uma flag.
Interface gráfica para supervisão em tempo real das variáveis.
Reconexão automática do MQTT para robustez na comunicação.

Arquitetura do Sistema
ESP32 (contador/flag) → MQTT Broker → Gateway Python → Servidor OPC UA
Servidor OPC UA → Gateway Python → MQTT Broker → ESP32


Componentes principais:
ESP32 (MicroPython): captura e publica variáveis; subscreve flag de controle.
Broker MQTT: garante a entrega de mensagens e sincronização de dados.
Gateway Python + PyQt5: atua como cliente OPC UA e cliente MQTT; atualiza servidores e exibe interface gráfica.




A interface PyQt5 exibirá o contador, a flag e o status da conexão em tempo real.
Alterações na flag pelo gateway ou outro cliente controlam a lógica do contador no ESP32.
