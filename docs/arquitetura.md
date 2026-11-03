# Arquitetura Smart Access

## 1. Visão geral

O Smart Access é um protótipo de controle automatizado de cancela. Sua arquitetura integra Arduino Uno R3, sensor ultrassônico HC-SR04, servo motor, Raspberry Pi, comunicação MQTT, API Flask, banco de dados SQLite e painel web.

## 2. Fluxo de telemetria

O fluxo de envio das informações ocorre da seguinte maneira:

HC-SR04 → Arduino Uno R3 → USB/Serial → Gateway Python na Raspberry Pi → MQTT Mosquitto → API Flask → SQLite → Painel Web.

O sensor realiza a medição de distância, e o Arduino envia os dados pela comunicação serial. O gateway interpreta as mensagens, organiza as informações em JSON e publica a telemetria no tópico MQTT `smartaccess/telemetry`.

A API Flask recebe os dados, registra os eventos no SQLite e disponibiliza as informações para o painel web.

## 3. Fluxo de comandos

O fluxo de controle da cancela ocorre da seguinte maneira:

Painel Web → API Flask → MQTT `smartaccess/command` → Gateway Python na Raspberry Pi → USB/Serial → Arduino Uno R3 → Servo Motor.

O painel envia uma solicitação à API. A API publica o comando em formato JSON pelo MQTT. O gateway recebe a mensagem e converte a ação em um caractere serial:

| Ação recebida | Comando serial | Função |
|---|---|---|
| OPEN | `O` | Abrir cancela |
| CLOSE | `C` | Fechar cancela |
| MODE_AUTO | `A` | Ativar modo automático |
| MODE_MANUAL | `M` | Ativar modo manual |

## 4. Tópicos MQTT

| Tópico | Finalidade |
|---|---|
| `smartaccess/telemetry` | Receber dados de distância, presença, estado lógico, modo de operação e timestamp. |
| `smartaccess/command` | Transportar comandos da API para o gateway. |
| `smartaccess/status` | Reservado para informações de estado e conexão do gateway. |

O broker MQTT utilizado é o Mosquitto, executado no computador, na porta 1883.

## 5. Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/health` | Verifica a disponibilidade da API e o estado da conexão MQTT. |
| GET | `/api/status` | Consulta o estado e a última telemetria recebida. |
| GET | `/api/events?limit=30` | Consulta o histórico de eventos registrados. |
| POST | `/api/telemetry` | Registra uma leitura simulada para testes locais. |
| POST | `/api/commands` | Recebe e publica comandos MQTT, exigindo conexão com o broker. |

## 6. Banco de dados

O sistema utiliza SQLite para armazenar informações de telemetria e eventos.

O banco permite consultar registros anteriores e acompanhar o histórico de funcionamento do protótipo.

## 7. Limitações conhecidas

- O estado da cancela representa o estado lógico comandado pelo sistema, não uma confirmação física obtida por sensor de posição independente.
- A comunicação depende da disponibilidade da Raspberry Pi, do broker MQTT e da API.
- O endpoint de telemetria simulada é destinado a testes locais e deve ser protegido ou removido em uma implantação real.
- O CORS está configurado de forma permissiva para facilitar o desenvolvimento local e deve ser restringido em uma implantação real.
- O tópico `smartaccess/status` é reservado e não deve ser considerado uma fonte ativa de status sem implementação de publicação correspondente.

## 8. Considerações finais

A arquitetura permite a comunicação entre os componentes físicos e digitais do Smart Access, possibilitando o monitoramento da cancela e o envio de comandos em modos automático e manual.