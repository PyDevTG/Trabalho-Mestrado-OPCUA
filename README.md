Este projeto foi desenvolvido para implementar a comunicação entre um Esp32 e um Servidor OPC UA usando um servidor Broker MQTT como gateway principal na troca de dados entre Esp32 e servidor OPCUA
dentro do servidor tem 2 variaveis sendo:
1 Flag booleana de controle
2 Contador Int16

foi implementado uma logica para testar o funcionamento da troca de dados:
se flag = True Esp32 inscrementa ou decrementar um contador circular 0-9-0
se flag=false Contador mantem o ultimo valor escrito

O gateway foi desenvolvido em python juntamente com a interface de usuário que foi implementada em Pyqt5 usandoo qtdesigner
