# Smart Access — Projeto SENAI

Protótipo educacional de uma cancela automatizada utilizando Arduino Uno R3, sensor ultrassônico HC-SR04, servo motor, Raspberry Pi, comunicação MQTT, API Flask, banco de dados SQLite e painel web.

## 1. Arquitetura do sistema

O sistema é dividido em quatro partes principais:

1. **Arduino Uno R3:** realiza a leitura da distância por meio do sensor HC-SR04 e controla o servo motor.
2. **Raspberry Pi:** executa o gateway Python, responsável pela comunicação entre o Arduino e o broker MQTT.
3. **Backend Flask:** recebe e processa os dados MQTT, disponibiliza uma API e registra informações no banco SQLite.
4. **Frontend:** painel web utilizado para visualizar o estado da cancela, acompanhar informações e enviar comandos.

O Arduino Uno R3 padrão não possui conexão Wi-Fi. Por isso, a Raspberry Pi funciona como intermediária entre a comunicação serial e o MQTT.

## 2. Tecnologias utilizadas

- Arduino Uno R3
- Sensor ultrassônico HC-SR04
- Servo motor
- Raspberry Pi
- Python
- Flask
- MQTT / Mosquitto
- SQLite
- HTML, CSS e JavaScript
- Visual Studio Code
- Tinkercad

## 3. Estrutura do projeto

```text
smart-access-starter/
│
├── arduino/
│   └── smart_access.ino
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── requirements.txt
│   └── smartaccess.db
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── gateway/
│   └── gateway.py
│
├── database/
├── docs/
├── .venv/
└── README.md
```

## 4. Executar o sistema

### 4.1. Backend no computador

Instale Python 3.11 ou superior e abra o terminal na pasta principal do projeto.

Crie e ative o ambiente virtual:

**Windows:**
```powershell
py -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```powershell
pip install -r backend/requirements.txt
```

Inicie a API:

```powershell
cd backend
python app.py
```

A API ficará disponível em:

`http://127.0.0.1:5000`

### 4.2. Painel web

Com o backend em execução:

1. Abra a pasta `frontend` no VS Code.
2. Abra o arquivo `index.html`.
3. Inicie o Live Server.
4. Acesse o endereço disponibilizado, normalmente:

`http://127.0.0.1:5500/frontend/index.html`

### 4.3. Gateway na Raspberry Pi

A Raspberry Pi deve estar conectada à mesma rede do computador que hospeda o Mosquitto.

Acesse a Raspberry Pi pelo SSH:

```bash
ssh rpi11@rpi11.local
```

Execute o gateway:

```bash
python3 ~/smartaccess/gateway.py
```

O gateway utiliza a porta serial `/dev/ttyACM0` para se comunicar com o Arduino.

## 5. Comunicação MQTT

O sistema utiliza os seguintes tópicos:

- `smartaccess/telemetry`: publicação de informações de telemetria pelo gateway.
- `smartaccess/command`: recebimento de comandos enviados pela API.
- `smartaccess/status`: tópico destinado ao status de conexão, conforme a implementação do gateway.

O broker Mosquitto é executado no computador, na porta `1883`.

## 6. Protocolo de comunicação serial

O Arduino e a Raspberry Pi se comunicam por meio de uma conexão USB/serial, utilizando velocidade de 9600 baud.

**Arduino → Raspberry Pi:**

O Arduino envia mensagens de texto contendo informações sobre a distância medida e o estado do sistema.

Exemplo:

```text
SMART ACCESS INICIADO
Modo AUTOMATICO
Distancia filtrada: 18.5 cm
Cancela aberta
```

**Raspberry Pi → Arduino:**

O gateway envia comandos simples:

| Comando | Função |
|---|---|
| `O` | Abrir cancela |
| `C` | Fechar cancela |
| `A` | Ativar modo automático |
| `M` | Ativar modo manual |

Cada comando é enviado com quebra de linha.

## 7. Funcionamento

O Smart Access possui dois modos de operação:

**Modo automático**
- O sensor ultrassônico identifica a distância de um objeto.
- Quando um objeto se aproxima, a cancela é acionada para abrir.
- Quando o objeto se afasta, a cancela pode ser fechada automaticamente.

**Modo manual**
- O usuário controla a cancela pelo painel web.
- Os botões de abertura e fechamento enviam comandos pela API e pelo MQTT.
- O gateway transmite o comando ao Arduino, que controla o servo motor.

A telemetria é enviada periodicamente, com intervalo aproximado de três segundos para as atualizações de distância.

## 8. Testes realizados

- Simulação inicial do circuito no Tinkercad.
- Leitura de distância pelo sensor HC-SR04.
- Controle do servo motor.
- Comunicação serial entre Arduino e Raspberry Pi.
- Comunicação MQTT entre Raspberry Pi e computador.
- Integração entre API Flask e painel web.
- Teste de abertura e fechamento em modo manual.
- Teste de acionamento automático por proximidade.
- Verificação da atualização das informações no painel.

## 9. Limitações e segurança

- A telemetria registra o estado lógico comandado pelo servo, não uma confirmação independente da posição física da cancela.
- O sistema depende da comunicação entre Arduino, Raspberry Pi, broker MQTT e computador.
- O protótipo possui finalidade educacional e não deve ser utilizado como sistema real de segurança ou controle de acesso.

## 10. Organização da equipe

As atividades podem ser divididas em:

1. Hardware e firmware: montagem, sensores, servo motor e programação Arduino.
2. Gateway e integração: comunicação serial, Raspberry Pi, MQTT e API.
3. Banco de dados, frontend e documentação: SQLite, painel web e documentação técnica.

Todos os integrantes devem compreender o funcionamento geral e conseguir explicar o fluxo de comunicação do sistema.