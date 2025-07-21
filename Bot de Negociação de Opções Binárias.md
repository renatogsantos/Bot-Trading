# Bot de Negociação de Opções Binárias

Este projeto implementa um bot de negociação automatizado para opções binárias, com foco em estratégias personalizáveis, gestão de risco robusta e capacidade de backtesting.

## Sumário

1.  [Visão Geral](#visão-geral)
2.  [Requisitos](#requisitos)
3.  [Estrutura do Projeto](#estrutura-do-projeto)
4.  [Configuração do Ambiente](#configuração-do-ambiente)
5.  [Módulos Principais](#módulos-principais)
    *   [Estratégia (`strategy.py`)](#estratégia-strategypy)
    *   [Execução (`execution.py`)](#execução-executionpy)
    *   [Gestão de Risco (`risk_management.py`)](#gestão-de-risco-risk_managementpy)
    *   [Logger (`logger.py`)](#logger-loggerpy)
    *   [Monitoramento (`monitoring.py`)](#monitoramento-monitoringpy)
    *   [Backtesting (`backtesting_module.py`)](#backtesting-backtesting_modulepy)
6.  [Configuração (`config/settings.json`)](#configuração-configsettingsjson)
7.  [Como Usar](#como-usar)
8.  [Backtesting](#backtesting)
9.  [Alertas e Monitoramento](#alertas-e-monitoramento)
10. [Desenvolvimento Futuro](#desenvolvimento-futuro)
11. [Licença](#licença)

## Visão Geral

O Bot de Negociação de Opções Binárias é uma ferramenta automatizada projetada para operar no mercado de opções binárias. Ele integra diversas funcionalidades essenciais para um trading sistemático e seguro:

*   **Estratégias Flexíveis**: Permite a implementação de múltiplas estratégias de negociação baseadas em indicadores técnicos.
*   **Gestão de Risco Avançada**: Inclui limites de perda diária, gestão de perdas consecutivas e dimensionamento de aposta para proteger o capital.
*   **Backtesting Robusto**: Capacidade de testar estratégias com dados históricos para avaliar seu desempenho antes de operar em tempo real.
*   **Monitoramento e Alertas**: Geração de logs detalhados, relatórios de performance e alertas em tempo real para eventos críticos.
*   **Modularidade**: Arquitetura modular que facilita a manutenção, expansão e adição de novas funcionalidades.

O bot foi desenvolvido para ser compatível com a API da Deriv.com, utilizando WebSockets para comunicação em tempo real.

## Requisitos

Para executar este bot, você precisará ter instalado:

*   Python 3.8 ou superior
*   `pip` (gerenciador de pacotes Python)

As dependências Python específicas estão listadas no arquivo `requirements.txt`.

## Estrutura do Projeto

A estrutura de diretórios do projeto é organizada da seguinte forma:

```
binary_options_bot/
├── code/                     # Contém o código-fonte principal do bot
│   ├── __init__.py
│   ├── main.py               # Ponto de entrada principal do bot
│   ├── strategy.py           # Lógica das estratégias de negociação
│   ├── execution.py          # Conexão com a corretora e execução de trades
│   ├── risk_management.py    # Regras de gestão de risco e capital
│   ├── logger.py             # Configuração e funções de logging
│   ├── monitoring.py         # Geração de relatórios e envio de alertas
│   └── backtesting_module.py # Módulo para simulação de backtesting
├── config/                   # Arquivos de configuração
│   └── settings.json         # Configurações do bot (API, estratégias, risco)
├── data/                     # Armazenamento de dados históricos (opcional)
├── logs/                     # Arquivos de log gerados pelo bot
├── reports/                  # Relatórios de performance gerados
├── venv/                     # Ambiente virtual Python
└── requirements.txt          # Dependências do projeto
```

## Configuração do Ambiente

Siga os passos abaixo para configurar e preparar o ambiente para executar o bot:

1.  **Clone o Repositório (se aplicável)**:

    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd binary_options_bot
    ```

2.  **Crie e Ative o Ambiente Virtual**:

    É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate  # No Windows: .\venv\Scripts\activate
    ```

3.  **Instale as Dependências**:

    ```bash
    pip install -r requirements.txt
    ```

    *Nota: Se houver problemas com `ta-lib`, certifique-se de ter as dependências de sistema instaladas (e.g., `libta-lib-dev` no Ubuntu).* No nosso caso, usamos `pandas-ta` que é uma alternativa em Python puro.

4.  **Configuração do `settings.json`**:

    Edite o arquivo `config/settings.json` com suas credenciais da API da Deriv e as configurações desejadas para as estratégias, gestão de risco e alertas. Um exemplo de estrutura é fornecido no arquivo.

    ```json
    {
      "broker": {
        "app_id": "SEU_APP_ID_DERIV",
        "api_token": "SEU_API_TOKEN_DERIV",
        "demo_mode": true
      },
      "strategy": {
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "min_confidence": 0.7,
        "use_macd": true,
        "use_bollinger_bands": true,
        "use_moving_averages": true
      },
      "trading": {
        "default_stake": 10,
        "check_interval": 30,
        "assets": ["R_50", "R_75"]
      },
      "risk_management": {
        "initial_balance": 1000.0,
        "max_daily_loss": 100.0,
        "max_daily_trades": 50,
        "max_consecutive_losses": 5,
        "max_drawdown_percent": 20.0,
        "min_balance": 100.0,
        "base_stake_percent": 2.0,
        "max_stake_percent": 5.0,
        "min_stake": 1.0,
        "max_stake": 100.0
      },
      "logging": {
        "log_file": "logs/bot_activity.log",
        "level": "INFO"
      },
      "alerts": {
        "email_enabled": false,
        "email_smtp_server": "smtp.gmail.com",
        "email_port": 587,
        "email_username": "seu_email@example.com",
        "email_password": "sua_senha_email",
        "telegram_enabled": false,
        "telegram_bot_token": "SEU_BOT_TOKEN_TELEGRAM",
        "telegram_chat_id": "SEU_CHAT_ID_TELEGRAM"
      },
      "backtesting": {
        "commission": 0.0
      }
    }
    ```

## Módulos Principais

### Estratégia (`strategy.py`)

Este módulo define a lógica de negociação do bot. Ele é responsável por:

*   Calcular indicadores técnicos (RSI, MACD, Bandas de Bollinger, Médias Móveis).
*   Gerar sinais de compra (CALL) ou venda (PUT) com base em regras predefinidas e na análise dos indicadores.
*   Determinar a confiança do sinal e o tempo de expiração da opção.

### Execução (`execution.py`)

Responsável pela interação com a corretora Deriv.com via API WebSocket. Suas funções incluem:

*   Conexão e autenticação com a API da Deriv.
*   Envio de requisições para obter propostas de contrato e executar ordens de compra.
*   Gerenciamento de trades ativos e atualização de seus status.
*   Contém uma `MockTradeExecutor` para simulação e testes sem conexão real.

### Gestão de Risco (`risk_management.py`)

Implementa as regras de gestão de capital e risco para proteger o saldo do trader. As funcionalidades incluem:

*   Definição de limites de perda diária e meta de lucro.
*   Controle de perdas consecutivas para pausar as operações.
*   Dimensionamento dinâmico do stake (valor da aposta) com base no saldo e performance.
*   Verificação de condições de mercado (notícias, volatilidade) para evitar operar em momentos de alto risco.

### Logger (`logger.py`)

Fornece um sistema de logging centralizado para registrar todas as atividades do bot, incluindo:

*   Logs informativos sobre o funcionamento geral.
*   Logs de erro para depuração.
*   Logs específicos de trades para análise posterior.
*   Suporta diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).

### Monitoramento (`monitoring.py`)

Este módulo é responsável por monitorar o desempenho do bot e enviar alertas:

*   **PerformanceReporter**: Calcula métricas de performance como taxa de acerto, retorno total, drawdown e Sharpe Ratio.
*   **AlertManager**: Envia alertas via e-mail ou Telegram para eventos importantes (e.g., drawdown alto, perdas consecutivas, nível de risco crítico).
*   Geração de relatórios diários de performance.

### Backtesting (`backtesting_module.py`)

Permite testar a estratégia de negociação com dados históricos para avaliar sua viabilidade e otimizar parâmetros. Utiliza a biblioteca `Backtesting.py` para simular trades e gerar estatísticas detalhadas de desempenho, incluindo a simulação de custos reais como comissões.

## Configuração (`config/settings.json`)

O arquivo `settings.json` é o coração da configuração do bot. Ele permite ajustar:

*   **`broker`**: Credenciais da API da Deriv e modo de operação (demo/real).
*   **`strategy`**: Parâmetros para os indicadores técnicos e regras da estratégia.
*   **`trading`**: Valor padrão da aposta, intervalo de verificação de sinais e ativos a serem negociados.
*   **`risk_management`**: Limites de perda/ganho, saldo inicial, limites de stake e regras de perdas consecutivas.
*   **`logging`**: Caminho do arquivo de log e nível de detalhe.
*   **`alerts`**: Configurações para envio de alertas via e-mail e Telegram.
*   **`backtesting`**: Parâmetros específicos para o módulo de backtesting, como comissões.

Certifique-se de preencher todas as informações relevantes antes de iniciar o bot.

## Como Usar

Após configurar o ambiente e o arquivo `settings.json`:

1.  **Ative o ambiente virtual**:

    ```bash
    source venv/bin/activate
    ```

2.  **Execute o bot**:

    ```bash
    python binary_options_bot/code/main.py
    ```

O bot começará a operar de acordo com as configurações definidas, registrando as atividades nos arquivos de log e enviando alertas conforme configurado.

## Backtesting

Para executar um backtest de sua estratégia:

1.  **Obtenha dados históricos**: O módulo de backtesting espera dados no formato OHLCV (Open, High, Low, Close, Volume). Você precisará carregar seus próprios dados históricos no formato de um DataFrame Pandas.

2.  **Execute o módulo de backtesting**: Você pode executar o `backtesting_module.py` diretamente para testar, ou integrá-lo a um script de análise. O exemplo de uso no `if __name__ == "__main__":` do `backtesting_module.py` demonstra como carregar dados fictícios e executar um backtest.

    ```python
    # Exemplo de uso no backtesting_module.py
    if __name__ == "__main__":
        # ... (código para carregar dados e configuração)
        run_backtest(data, test_config)
    ```

    Ajuste os parâmetros da estratégia no `settings.json` e no `BinaryOptionsStrategy` dentro de `backtesting_module.py` para otimizar o desempenho.

## Alertas e Monitoramento

O sistema de monitoramento gera relatórios diários e envia alertas para ajudar a acompanhar o desempenho do bot e identificar problemas rapidamente.

*   **Logs**: Verifique a pasta `logs/` para logs detalhados das operações.
*   **Relatórios**: Relatórios diários de performance são salvos na pasta `reports/`.
*   **Alertas**: Configure as seções `email_enabled` e `telegram_enabled` no `settings.json` para receber alertas em tempo real.

## Desenvolvimento Futuro

Possíveis melhorias e funcionalidades a serem adicionadas:

*   Integração com outras corretoras de opções binárias.
*   Implementação de mais indicadores técnicos e estratégias de trading.
*   Interface de usuário (UI) para monitoramento e controle do bot.
*   Otimização de parâmetros de estratégia usando algoritmos genéticos ou outras técnicas de otimização.
*   Suporte a diferentes tipos de opções binárias (e.g., One Touch, No Touch).
*   Análise de sentimento de mercado.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes. (Se aplicável, crie um arquivo LICENSE no diretório raiz do projeto).

---

**Autor:** Manus AI
**Data:** 21 de Julho de 2025


