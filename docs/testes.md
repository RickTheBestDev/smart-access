# Smart Access — Roteiro e Registro de Testes

## 1. Testes locais — computador

- [x] API Flask inicia sem erros.
- [x] Endpoint `/api/health` retorna resposta válida.
- [x] Painel web carrega pelo Live Server.
- [x] Comunicação entre painel e API verificada.
- [x] Banco SQLite inicializado e acessível.
- [ ] Botão "Simular leitura" atualiza o status.
- [ ] Leitura simulada aparece no histórico.
- [ ] Comando inválido via API retorna HTTP 400.

## 2. Testes de hardware

- [x] Circuito simulado no Tinkercad.
- [x] Sensor HC-SR04 realiza medições de distância.
- [x] Servo motor abre e fecha nos ângulos programados.
- [x] LEDs indicam os estados de funcionamento.
- [x] Buzzer integrado ao funcionamento do circuito.
- [x] Comunicação serial entre Arduino e Raspberry Pi.

## 3. Testes de comunicação e integração

- [x] Gateway Python executado na Raspberry Pi.
- [x] Conexão entre Raspberry Pi e broker Mosquitto.
- [x] Publicação de telemetria no tópico `smartaccess/telemetry`.
- [x] Recebimento de comandos pelo tópico `smartaccess/command`.
- [x] API Flask recebe e processa dados MQTT.
- [x] Informações atualizadas no painel web.
- [x] Comandos enviados pelo painel chegam ao Arduino.
- [x] Abertura e fechamento da cancela em modo manual.
- [x] Acionamento automático por proximidade.
- [x] Atualização da telemetria com intervalo aproximado de três segundos.

## 4. Testes pendentes de validação

- [ ] Verificar se o botão "Simular leitura" atualiza o histórico corretamente.
- [ ] Confirmar resposta HTTP 400 para comandos inválidos.
- [ ] Testar comportamento do sistema durante perda de conexão MQTT.
- [ ] Confirmar alimentação adequada do servo em operação contínua.
- [ ] Verificar se todos os registros são persistidos corretamente no SQLite.

## 5. Cuidados durante a montagem

- Conferir a pinagem antes de ligar o circuito.
- Garantir GND comum entre os componentes.
- Verificar a alimentação necessária do servo motor.
- Não sobrecarregar o pino de 5 V do Arduino caso o servo exija corrente superior à disponível.
- Não utilizar simultaneamente o Monitor Serial e o gateway na mesma porta.
- Confirmar a porta serial correta na Raspberry Pi, como `/dev/ttyACM0`.

## 6. Roteiro para demonstração

1. Apresentar o circuito com Arduino, HC-SR04 e servo motor.
2. Mostrar a leitura de distância no funcionamento do sistema.
3. Demonstrar a abertura e o fechamento automáticos.
4. Demonstrar os comandos de abertura e fechamento pelo painel web.
5. Mostrar a comunicação MQTT entre a Raspberry Pi e o computador.
6. Apresentar o endpoint `/api/status` da API Flask.
7. Mostrar os registros armazenados no SQLite e o histórico no painel.
8. Explicar a arquitetura e o papel de cada componente.

## 7. Resultado geral

Os testes de integração realizados demonstraram o funcionamento dos modos automático e manual, a comunicação entre Arduino e Raspberry Pi, a troca de mensagens MQTT e a integração com a API Flask e o painel web.

Os itens ainda não validados devem ser conferidos antes de serem apresentados como resultados concluídos.

**Observação:** o estado apresentado pelo sistema representa o estado lógico comandado pelo servo motor, não uma confirmação física independente da posição da cancela.