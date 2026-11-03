# Smart Access — Requisitos do Sistema

## 1. Problema

Em estacionamentos e ambientes com controle de acesso, o acionamento de cancelas pode exigir acompanhamento local, dificultando o monitoramento e o registro dos eventos.

O Smart Access propõe um protótipo educacional capaz de detectar a aproximação de objetos, controlar o acionamento lógico de uma cancela, permitir comandos remotos e registrar informações de funcionamento por meio de uma arquitetura IoT.

## 2. Objetivo

Desenvolver um protótipo educacional de cancela automatizada, integrando sensores, atuadores, comunicação MQTT, processamento de dados, banco de dados e painel web para monitoramento e controle.

## 3. Requisitos funcionais

- **RF01:** Realizar medições de distância utilizando o sensor ultrassônico HC-SR04.
- **RF02:** Identificar a aproximação de objetos com base em limites configurados no firmware.
- **RF03:** Controlar a abertura e o fechamento da cancela por meio de um servo motor.
- **RF04:** Indicar os estados de funcionamento utilizando LEDs.
- **RF05:** Disponibilizar os modos de operação automático e manual.
- **RF06:** Receber comandos remotos por meio da API Flask.
- **RF07:** Transmitir informações de telemetria utilizando o protocolo MQTT.
- **RF08:** Armazenar informações de telemetria e eventos no banco de dados SQLite.
- **RF09:** Exibir informações de estado e funcionamento no painel web.
- **RF10:** Permitir a consulta ao histórico de eventos registrados.
- **RF11:** Emitir sinais sonoros por meio de um buzzer em situações programadas.
- **RF12:** Identificar e informar falhas de comunicação quando detectáveis pelos componentes do sistema.

## 4. Requisitos não funcionais

- **RNF01:** Apresentar uma interface web responsiva e de fácil utilização.
- **RNF02:** Manter os tópicos MQTT e formatos de mensagens documentados.
- **RNF03:** Garantir a persistência dos registros no banco de dados.
- **RNF04:** Apresentar mensagens de erro compreensíveis ao usuário.
- **RNF05:** Validar os comandos recebidos antes de encaminhá-los ao hardware.
- **RNF06:** Manter o código organizado e estruturado em módulos.
- **RNF07:** Utilizar tecnologias e protocolos adequados à integração entre hardware e software.

## 5. Regras de negócio

- **RN01:** Somente comandos previamente permitidos pelo sistema podem ser encaminhados ao Arduino.
- **RN02:** No modo automático, a aproximação de um objeto abaixo do limite configurado pode provocar a abertura da cancela.
- **RN03:** No modo manual, a aproximação de objetos não deve provocar a abertura automática.
- **RN04:** Eventos relevantes devem ser registrados com data e hora.
- **RN05:** O recebimento de um comando não representa, por si só, a confirmação de sua execução física.
- **RN06:** O protótipo não realiza identificação de pessoas e não substitui sistemas certificados de controle de acesso e segurança.
- **RN07:** A telemetria deve representar o estado lógico do sistema, sem afirmar que existe confirmação independente da posição física da cancela.

## 6. Premissas e restrições

- A comunicação entre Arduino e MQTT é realizada por meio de um gateway Python executado na Raspberry Pi.
- A Raspberry Pi utiliza conexão USB/serial para comunicação com o Arduino Uno R3.
- O computador hospeda o broker Mosquitto e a API Flask.
- O painel web realiza a comunicação com a API para consulta de informações e envio de comandos.
- A simulação no Tinkercad é utilizada para validar os componentes compatíveis com o ambiente.
- A integração física depende da disponibilidade dos equipamentos e das condições do laboratório.

## 7. Critérios gerais de validação

O sistema será considerado funcional quando demonstrar:

1. Leitura de distância pelo sensor HC-SR04.
2. Acionamento do servo motor nos modos automático e manual.
3. Indicação visual e sonora conforme a programação.
4. Comunicação serial entre Arduino e Raspberry Pi.
5. Troca de mensagens entre gateway e broker MQTT.
6. Recebimento e processamento de comandos pela API.
7. Atualização das informações no painel web.
8. Registro e consulta de eventos no banco SQLite.