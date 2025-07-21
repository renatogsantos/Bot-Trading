## Tarefas para o Bot de Negociação de Opções Binárias

### Fase 1: Análise do documento e levantamento de requisitos
- [x] Ler e analisar o documento 'pasted_content.txt'.
- [x] Consolidar os requisitos em um formato estruturado.

### Fase 2: Pesquisa de APIs e ferramentas de trading
- [x] Pesquisar corretoras de opções binárias com APIs formais (ex: Deriv).
- [x] Investigar bibliotecas Python para indicadores técnicos (ta-lib, pandas-ta).
- [x] Pesquisar ferramentas de backtesting (Backtesting.py, Zipline).

### Fase 3: Desenvolvimento da arquitetura e estrutura do bot
- [x] Definir a estrutura de pastas do projeto (dados, logs, config, código).
- [x] Configurar o ambiente de desenvolvimento (Python 3.8+, pip/virtualenv).
- [x] Esboçar a arquitetura do bot (módulos para estratégia, execução, risco, log).

### Fase 4: Implementação das estratégias de trading
- [x] Implementar a lógica de entrada (RSI, MACD, médias móveis).
- [x] Implementar regras de saída, stop-loss, stop diário.
- [x] Considerar a implementação de martingale ou outras lógicas de gestão de posição.
- [x] Documentar a lógica de forma clara (sinal CALL/PUT, evitar operar, pós-perdas).

### Fase 5: Desenvolvimento do sistema de backtesting
- [x] Obter dados históricos (2-3 anos ou mais) para o timeframe de interesse.
- [x] Implementar o framework de backtesting (Backtesting.py, Zipline ou customizado).
- [x] Simular custos reais (comissões, slippage, latência, falhas de ordem).

### Fase 6: Implementação da gestão de risco
- [x] Implementar limites de perda/ganho por sessão (stop-loss diário, meta de lucro).
- [x] Implementar regras de dimensionamento de aposta (percentual fixo do saldo ou lotes dinâmicos).
- [x] Implementar contagem de perdas consecutivas para interromper operações.
- [x] Adicionar lógica para pausar o bot durante notícias ou mercados voláteis.

### Fase 7: Sistema de monitoramento e alertas
- [x] Implementar registro detalhado de logs para cada operação.
- [x] Gerar relatórios periódicos com métricas de performance (drawdown, taxa de acerto, retorno, sharp ratio).
- [x] Configurar monitoramento em tempo real ou alertas (e-mail, Telegram) para erros/limites.

### Fase 8: Documentação e entrega dos resultados
- [x] Documentar todo o código e a arquitetura do bot.
- [x] Preparar um relatório final com os requisitos, design e exemplos de código.
- [ ] Entregar os arquivos e a documentação ao usuário.

