# Relatório Final: Bot de Negociação de Opções Binárias

**Autor:** Manus AI
**Data:** 21 de Julho de 2025

## 1. Introdução

Este relatório detalha o levantamento de requisitos, o design da arquitetura e os exemplos de código para um bot de negociação automatizado focado em opções binárias. O objetivo principal é fornecer uma solução robusta e modular que permita a execução de estratégias de trading, gestão de risco eficaz, backtesting e monitoramento em tempo real.

## 2. Requisitos do Sistema

Os requisitos para o bot foram levantados a partir da análise do documento fornecido e das melhores práticas de desenvolvimento de sistemas de trading. Eles podem ser categorizados da seguinte forma:

### 2.1. Requisitos Funcionais

*   **Conectividade com Corretora**: O bot deve ser capaz de se conectar e autenticar com a API de uma corretora de opções binárias (e.g., Deriv.com) para enviar e receber dados de mercado e ordens de negociação.
*   **Obtenção de Dados de Mercado**: Deve ser capaz de obter dados de mercado em tempo real (ticks, velas) para os ativos de interesse.
*   **Geração de Sinais de Trading**: Deve implementar lógicas de estratégia baseadas em indicadores técnicos (RSI, MACD, Bandas de Bollinger, Médias Móveis) para gerar sinais de compra (CALL) ou venda (PUT).
*   **Execução de Ordens**: Deve ser capaz de enviar ordens de compra/venda para a corretora com base nos sinais gerados, especificando o ativo, direção, valor da aposta e tempo de expiração.
*   **Gestão de Posições**: Deve monitorar o status dos trades ativos até a expiração e registrar seus resultados.
*   **Gestão de Risco**: Deve incorporar regras de gestão de risco, incluindo:
    *   Limites de perda diária (stop-loss diário).
    *   Meta de lucro diária (take-profit diário).
    *   Controle de perdas consecutivas para pausar as operações.
    *   Dimensionamento de aposta (stake) baseado em percentual do saldo ou lotes dinâmicos.
    *   Capacidade de pausar o trading durante condições de mercado desfavoráveis (e.g., notícias de alto impacto, alta volatilidade).
*   **Backtesting**: Deve permitir a simulação de estratégias com dados históricos, incluindo a simulação de custos reais (comissões, slippage, latência).
*   **Logging**: Deve registrar todas as operações, eventos e erros em arquivos de log detalhados.
*   **Monitoramento e Alertas**: Deve gerar relatórios periódicos de performance (taxa de acerto, retorno, drawdown, Sharpe Ratio) e enviar alertas em tempo real (e-mail, Telegram) para eventos críticos ou limites atingidos.

### 2.2. Requisitos Não Funcionais

*   **Performance**: O bot deve ser responsivo e capaz de processar dados de mercado e executar trades em tempo hábil para aproveitar as oportunidades.
*   **Confiabilidade**: Deve ser robusto a falhas de conexão e erros da API, com mecanismos de retry e tratamento de exceções.
*   **Segurança**: As credenciais da API e outras informações sensíveis devem ser armazenadas e utilizadas de forma segura.
*   **Modularidade**: O código deve ser bem organizado em módulos distintos para facilitar a manutenção, teste e expansão.
*   **Configurabilidade**: As configurações do bot (parâmetros de estratégia, limites de risco, credenciais) devem ser facilmente ajustáveis via arquivo de configuração.
*   **Escalabilidade**: A arquitetura deve permitir a adição de novas estratégias, indicadores ou corretoras no futuro.
*   **Usabilidade**: Embora seja um bot, a configuração e o monitoramento devem ser o mais intuitivos possível.

## 3. Design da Arquitetura

A arquitetura do bot é baseada em um design modular, onde cada componente tem uma responsabilidade clara. Isso facilita o desenvolvimento, a depuração e a manutenção do sistema.

```mermaid
graph TD
    A[main.py - Orquestrador] --> B(strategy.py - Lógica de Estratégia)
    A --> C(execution.py - Execução de Trades)
    A --> D(risk_management.py - Gestão de Risco)
    A --> E(logger.py - Logging)
    A --> F(monitoring.py - Monitoramento e Alertas)
    A --> G(config/settings.json - Configuração)
    C --> H(Deriv API - Conexão Externa)
    F --> I(E-mail/Telegram - Alertas)
    B --> J(Indicadores Técnicos)
    A --> K(backtesting_module.py - Backtesting)
    K --> L(Dados Históricos)
    D --> M(Regras de Capital)
    D --> N(Controle de Perdas)
    F --> O(Relatórios de Performance)
```

### 3.1. Componentes Principais

*   **`main.py` (Orquestrador)**: O ponto de entrada principal do bot. Ele carrega as configurações, inicializa todos os módulos e coordena o fluxo de execução, chamando as funções apropriadas de cada módulo em um loop contínuo.
*   **`strategy.py` (Lógica de Estratégia)**: Contém a implementação das estratégias de negociação. Recebe dados de mercado, calcula indicadores técnicos e gera sinais de compra/venda com base em regras predefinidas. É independente da corretora e da execução.
*   **`execution.py` (Execução de Trades)**: Responsável pela comunicação com a corretora (Deriv.com via WebSocket API). Envia ordens de negociação, gerencia trades ativos e lida com as respostas da API. Inclui uma classe `MockTradeExecutor` para simulação e testes.
*   **`risk_management.py` (Gestão de Risco)**: Implementa todas as regras de gestão de capital e risco. Decide se um trade pode ser executado com base em limites de perda, perdas consecutivas, saldo disponível e condições de mercado. Também calcula o stake ideal para cada operação.
*   **`logger.py` (Logging)**: Um módulo utilitário que fornece um sistema de logging centralizado. Permite registrar informações, avisos, erros e eventos de trade de forma estruturada em arquivos de log.
*   **`monitoring.py` (Monitoramento e Alertas)**: Responsável por calcular métricas de performance, gerar relatórios diários e enviar alertas. Integra-se com serviços de e-mail e Telegram para notificar o usuário sobre eventos importantes ou anomalias.
*   **`backtesting_module.py` (Backtesting)**: Utiliza a biblioteca `Backtesting.py` para simular o desempenho das estratégias com dados históricos. Permite avaliar a viabilidade da estratégia e otimizar seus parâmetros antes de operar em tempo real.
*   **`config/settings.json` (Configuração)**: Um arquivo JSON que armazena todas as configurações do bot, incluindo credenciais da API, parâmetros de estratégia, limites de risco, configurações de logging e alertas.

## 4. Exemplos de Código

Os exemplos de código abaixo ilustram a implementação de alguns dos módulos chave do bot. O código completo está disponível na estrutura de diretórios do projeto.

### 4.1. Exemplo de `strategy.py` (Geração de Sinal)

```python
# code/strategy.py

import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    CALL = "CALL"
    PUT = "PUT"

@dataclass
class TradingSignal:
    signal_type: SignalType
    asset: str
    confidence: float
    expiry_time: int # Em minutos
    indicators: Dict # Valores dos indicadores no momento do sinal

class TradingStrategy:
    def __init__(self, config: Dict):
        self.config = config.get("strategy", {})
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.min_confidence = self.config.get("min_confidence", 0.7)
        self.use_macd = self.config.get("use_macd", True)
        self.use_bollinger_bands = self.config.get("use_bollinger_bands", True)
        self.use_moving_averages = self.config.get("use_moving_averages", True)

    def generate_signal(self, market_data: pd.DataFrame, asset: str) -> Optional[TradingSignal]:
        if market_data.empty:
            return None

        # Certifica-se de que os dados estão no formato correto
        df = market_data.copy()
        
        # Calcula indicadores técnicos
        df["RSI"] = ta.rsi(df["Close"], length=14)
        
        if self.use_macd:
            macd = ta.macd(df["Close"])
            df["MACD"] = macd["MACD_12_26_9"]
            df["MACD_SIGNAL"] = macd["MACDs_12_26_9"]
        
        if self.use_bollinger_bands:
            bbands = ta.bbands(df["Close"])
            df["BBL"] = bbands["BBL_5_2.0"]
            df["BBM"] = bbands["BBM_5_2.0"]
            df["BBU"] = bbands["BBU_5_2.0"]

        if self.use_moving_averages:
            df["SMA_20"] = ta.sma(df["Close"], length=20)
            df["EMA_50"] = ta.ema(df["Close"], length=50)

        # Pega a última linha de dados para análise
        latest_data = df.iloc[-1]
        current_price = latest_data["Close"]
        
        signal_type = None
        confidence = 0.0

        # Lógica de sinal baseada em RSI
        if latest_data["RSI"] < self.rsi_oversold: # RSI sobrevendido
            signal_type = SignalType.CALL
            confidence += (self.rsi_oversold - latest_data["RSI"]) / self.rsi_oversold # Quanto mais baixo, maior a confiança
        elif latest_data["RSI"] > self.rsi_overbought: # RSI sobrecomprado
            signal_type = SignalType.PUT
            confidence += (latest_data["RSI"] - self.rsi_overbought) / (100 - self.rsi_overbought) # Quanto mais alto, maior a confiança

        # Lógica adicional com MACD
        if self.use_macd and signal_type:
            if latest_data["MACD"] > latest_data["MACD_SIGNAL"] and df.iloc[-2]["MACD"] <= df.iloc[-2]["MACD_SIGNAL"]: # Cruzamento de alta
                if signal_type == SignalType.CALL: confidence += 0.2
                else: confidence -= 0.1 # Penaliza sinal contrário
            elif latest_data["MACD"] < latest_data["MACD_SIGNAL"] and df.iloc[-2]["MACD"] >= df.iloc[-2]["MACD_SIGNAL"]: # Cruzamento de baixa
                if signal_type == SignalType.PUT: confidence += 0.2
                else: confidence -= 0.1 # Penaliza sinal contrário

        # Lógica adicional com Bandas de Bollinger
        if self.use_bollinger_bands and signal_type:
            if current_price < latest_data["BBL"] and signal_type == SignalType.CALL: confidence += 0.15
            elif current_price > latest_data["BBU"] and signal_type == SignalType.PUT: confidence += 0.15

        # Lógica adicional com Médias Móveis (cruzamento simples)
        if self.use_moving_averages and signal_type:
            if latest_data["SMA_20"] > latest_data["EMA_50"] and df.iloc[-2]["SMA_20"] <= df.iloc[-2]["EMA_50"]: # Cruzamento de alta
                if signal_type == SignalType.CALL: confidence += 0.1
                else: confidence -= 0.05
            elif latest_data["SMA_20"] < latest_data["EMA_50"] and df.iloc[-2]["SMA_20"] >= df.iloc[-2]["EMA_50"]: # Cruzamento de baixa
                if signal_type == SignalType.PUT: confidence += 0.1
                else: confidence -= 0.05

        # Normaliza a confiança para estar entre 0 e 1
        confidence = max(0.0, min(1.0, confidence))

        if signal_type and confidence >= self.min_confidence:
            return TradingSignal(
                signal_type=signal_type,
                asset=asset,
                confidence=confidence,
                expiry_time=5, # Exemplo: 5 minutos de expiração
                indicators={
                    "RSI": latest_data["RSI"],
                    "MACD": latest_data.get("MACD"),
                    "MACD_SIGNAL": latest_data.get("MACD_SIGNAL"),
                    "BBL": latest_data.get("BBL"),
                    "BBM": latest_data.get("BBM"),
                    "BBU": latest_data.get("BBU"),
                    "SMA_20": latest_data.get("SMA_20"),
                    "EMA_50": latest_data.get("EMA_50"),
                    "current_price": current_price
                }
            )
        return None

```

### 4.2. Exemplo de `risk_management.py` (Verificação de Trade)

```python
# code/risk_management.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskMetrics:
    daily_loss: float
    daily_profit: float
    consecutive_losses: int
    consecutive_wins: int
    total_trades_today: int
    current_drawdown: float
    max_drawdown: float
    win_rate: float
    risk_level: RiskLevel

class RiskManager:
    def __init__(self, config: Dict):
        self.config = config.get("risk_management", {})
        self.daily_stats = self._initialize_daily_stats()
        self.trade_history = []
        self.current_balance = self.config.get("initial_balance", 1000.0)
        self.initial_balance = self.current_balance
        self.max_balance = self.current_balance
        
        self.max_daily_loss = self.config.get("max_daily_loss", 100.0)
        self.max_daily_trades = self.config.get("max_daily_trades", 50)
        self.max_consecutive_losses = self.config.get("max_consecutive_losses", 5)
        self.max_drawdown_percent = self.config.get("max_drawdown_percent", 20.0)
        self.min_balance = self.config.get("min_balance", 100.0)
        
        self.base_stake_percent = self.config.get("base_stake_percent", 2.0)
        self.max_stake_percent = self.config.get("max_stake_percent", 5.0)
        self.min_stake = self.config.get("min_stake", 1.0)
        self.max_stake = self.config.get("max_stake", 100.0)
    
    def _initialize_daily_stats(self) -> Dict:
        return {
            "date": datetime.now().date(),
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0.0,
            "loss": 0.0,
            "consecutive_losses": 0,
            "consecutive_wins": 0,
            "last_trade_result": None
        }
    
    def can_execute_trade(self, signal, proposed_stake: float = None) -> bool:
        self._check_new_day()
        
        if proposed_stake is None:
            proposed_stake = self.calculate_optimal_stake()
        
        checks = [
            self._check_daily_loss_limit(),
            self._check_daily_trade_limit(),
            self._check_consecutive_losses(),
            self._check_balance_limits(),
            self._check_drawdown_limit(),
            self._check_stake_limits(proposed_stake),
            self._check_market_conditions()
        ]
        
        failed_checks = []
        for i, (passed, reason) in enumerate(checks):
            if not passed:
                failed_checks.append(reason)
        
        if failed_checks:
            # print(f"Trade bloqueado pelos seguintes motivos: {", ".join(failed_checks)}")
            return False
        
        return True
    
    def _check_new_day(self):
        current_date = datetime.now().date()
        if self.daily_stats["date"] != current_date:
            self.daily_stats = self._initialize_daily_stats()
    
    def _check_daily_loss_limit(self) -> tuple[bool, str]:
        if self.daily_stats["loss"] >= self.max_daily_loss:
            return False, "Limite de perda diária atingido"
        return True, ""
    
    def _check_daily_trade_limit(self) -> tuple[bool, str]:
        if self.daily_stats["trades"] >= self.max_daily_trades:
            return False, "Limite de trades diários atingido"
        return True, ""
    
    def _check_consecutive_losses(self) -> tuple[bool, str]:
        if self.daily_stats["consecutive_losses"] >= self.max_consecutive_losses:
            return False, "Muitas perdas consecutivas"
        return True, ""
    
    def _check_balance_limits(self) -> tuple[bool, str]:
        if self.current_balance <= self.min_balance:
            return False, "Saldo abaixo do mínimo permitido"
        return True, ""
    
    def _check_drawdown_limit(self) -> tuple[bool, str]:
        current_drawdown = ((self.max_balance - self.current_balance) / self.max_balance) * 100
        if current_drawdown >= self.max_drawdown_percent:
            return False, f"Drawdown máximo atingido ({current_drawdown:.1f}%)"
        return True, ""
    
    def _check_stake_limits(self, stake: float) -> tuple[bool, str]:
        if stake < self.min_stake:
            return False, f"Stake abaixo do mínimo ({self.min_stake})"
        if stake > self.max_stake:
            return False, f"Stake acima do máximo ({self.max_stake})"
        
        stake_percent = (stake / self.current_balance) * 100
        if stake_percent > self.max_stake_percent:
            return False, f"Stake representa mais que {self.max_stake_percent}% do saldo"
        
        return True, ""
    
    def _check_market_conditions(self) -> tuple[bool, str]:
        # Implementar verificações específicas de mercado (e.g., notícias)
        return True, ""
    
    def calculate_optimal_stake(self) -> float:
        base_stake = (self.current_balance * self.base_stake_percent) / 100
        win_rate = self.calculate_win_rate()
        
        multiplier = 1.0
        if win_rate > 0.7: multiplier = 1.2
        elif win_rate < 0.5: multiplier = 0.8
        
        if self.daily_stats["consecutive_losses"] > 2: multiplier *= 0.5
        
        optimal_stake = base_stake * multiplier
        return round(max(self.min_stake, min(optimal_stake, self.max_stake)), 2)
    
    def update_trade_result(self, trade_result: Dict):
        self._check_new_day()
        result = trade_result.get("result", 0)
        
        self.current_balance += result
        if self.current_balance > self.max_balance: self.max_balance = self.current_balance
        
        self.daily_stats["trades"] += 1
        
        if result > 0:
            self.daily_stats["wins"] += 1
            self.daily_stats["profit"] += result
            self.daily_stats["consecutive_wins"] += 1
            self.daily_stats["consecutive_losses"] = 0
            self.daily_stats["last_trade_result"] = "win"
        else:
            self.daily_stats["losses"] += 1
            self.daily_stats["loss"] += abs(result)
            self.daily_stats["consecutive_losses"] += 1
            self.daily_stats["consecutive_wins"] = 0
            self.daily_stats["last_trade_result"] = "loss"
        
        self.trade_history.append({
            "timestamp": datetime.now(),
            "result": result,
            "stake": trade_result.get("stake", 0),
            "balance_after": self.current_balance
        })
    
    def calculate_win_rate(self) -> float:
        total_trades = self.daily_stats["wins"] + self.daily_stats["losses"]
        return self.daily_stats["wins"] / total_trades if total_trades > 0 else 0.0
    
    def get_risk_metrics(self) -> RiskMetrics:
        current_drawdown = ((self.max_balance - self.current_balance) / self.max_balance) * 100
        max_drawdown = max(current_drawdown, self.config.get("historical_max_drawdown", 0))
        
        risk_level = RiskLevel.LOW
        if current_drawdown > 15 or self.daily_stats["consecutive_losses"] > 3: risk_level = RiskLevel.HIGH
        elif current_drawdown > 10 or self.daily_stats["consecutive_losses"] > 2: risk_level = RiskLevel.MEDIUM
        if self.current_balance <= self.min_balance: risk_level = RiskLevel.CRITICAL
        
        return RiskMetrics(
            daily_loss=self.daily_stats["loss"],
            daily_profit=self.daily_stats["profit"],
            consecutive_losses=self.daily_stats["consecutive_losses"],
            consecutive_wins=self.daily_stats["consecutive_wins"],
            total_trades_today=self.daily_stats["trades"],
            current_drawdown=current_drawdown,
            max_drawdown=max_drawdown,
            win_rate=self.calculate_win_rate(),
            risk_level=risk_level
        )
    
    def should_stop_trading(self) -> bool:
        metrics = self.get_risk_metrics()
        stop_conditions = [
            metrics.risk_level == RiskLevel.CRITICAL,
            metrics.daily_loss >= self.max_daily_loss,
            metrics.consecutive_losses >= self.max_consecutive_losses,
            metrics.current_drawdown >= self.max_drawdown_percent,
            self.current_balance <= self.min_balance
        ]
        return any(stop_conditions)

```

### 4.3. Exemplo de `main.py` (Loop Principal)

```python
# main.py

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime, timedelta

# Adiciona o diretório raiz do projeto ao PATH para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code.strategy import TradingStrategy, SignalType
from code.execution import TradeExecutor, MockTradeExecutor, OrderStatus
from code.risk_management import RiskManager
from code.logger import BotLogger
from code.monitoring import MonitoringSystem

def load_config(config_path: str) -> dict:
    """Carrega as configurações do arquivo JSON."""
    with open(config_path, "r") as f:
        return json.load(f)

def main():
    config_path = "config/settings.json"
    config = load_config(config_path)

    # Inicializa o logger
    log_file = config.get("logging", {}).get("log_file", "logs/bot_activity.log")
    log_level = config.get("logging", {}).get("level", "INFO").upper()
    logger = BotLogger(log_file=log_file, level=getattr(BotLogger, log_level, BotLogger.INFO))
    
    logger.info("Iniciando o Bot de Negociação de Opções Binárias...")
    
    # Inicializa os módulos
    strategy = TradingStrategy(config)
    
    # Escolhe entre executor real ou mock
    if config.get("broker", {}).get("demo_mode", True):
        executor = MockTradeExecutor(config, logger)
    else:
        executor = TradeExecutor(config, logger)
        
    risk_manager = RiskManager(config)
    monitoring_system = MonitoringSystem(config, logger)
    
    # Conecta à corretora
    try:
        app_id = config.get("broker", {}).get("app_id")
        api_token = config.get("broker", {}).get("api_token")
        executor.connect_to_broker(app_id, api_token)
    except Exception as e:
        logger.error(f"Não foi possível conectar à corretora: {e}. Encerrando o bot.")
        return

    # Loop principal de negociação
    check_interval = config.get("trading", {}).get("check_interval", 30)
    assets_to_trade = config.get("trading", {}).get("assets", [])

    if not assets_to_trade:
        logger.warning("Nenhum ativo configurado para negociação. Encerrando o bot.")
        return

    while True:
        try:
            # Obter dados de mercado (simulados para teste)
            # Em um cenário real, você obteria dados de ticks ou velas da API da corretora
            # Para simulação, vamos gerar dados aleatórios ou carregar de um arquivo
            # TODO: Implementar a obtenção de dados reais da API da Deriv
            
            # Exemplo de dados simulados para teste
            data_points = 50
            mock_data = {
                "open": [100 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "high": [101 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "low": [99 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "close": [100.5 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "volume": [1000 + i * 10 for i in range(data_points)]
            }
            index = pd.to_datetime([datetime.now() - timedelta(minutes=data_points - 1 - i) for i in range(data_points)])
            market_data = pd.DataFrame(mock_data, index=index)

            for asset in assets_to_trade:
                signal = strategy.generate_signal(market_data, asset)

                if signal:
                    if risk_manager.can_execute_trade(signal):
                        trade = executor.execute_trade(signal)
                        if trade:
                            simulated_result = trade.amount * 0.8 if trade.direction == "CALL" else -trade.amount
                            risk_manager.update_trade_result({
                                "result": simulated_result,
                                "stake": trade.amount,
                                "trade_id": trade.trade_id
                            })
                            logger.info(f"Trade {trade.trade_id} simulado com resultado: {simulated_result:.2f}")
                    else:
                        logger.warning(f"Trade para {asset} bloqueado por gestão de risco.")
                else:
                    logger.info(f"Nenhum sinal gerado para {asset}.")
            
            executor.check_active_trades()
            current_risk_metrics = risk_manager.get_risk_metrics()
            monitoring_system.monitor_trading_session(current_risk_metrics, risk_manager.trade_history)

            if risk_manager.should_stop_trading():
                logger.warning("Condições de risco atingidas. Parando o bot.")
                break

            time.sleep(check_interval)

        except Exception as e:
            logger.error(f"Erro inesperado no loop principal: {e}")
            time.sleep(check_interval)

    logger.info("Bot de Negociação de Opções Binárias encerrado.")

if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("reports"):
        os.makedirs("reports")
    main()
```

## 5. Conclusão

Este relatório apresenta uma visão abrangente do bot de negociação de opções binárias, desde o levantamento de requisitos até o design da arquitetura e exemplos de implementação. A estrutura modular e a inclusão de funcionalidades como gestão de risco, backtesting e monitoramento tornam este bot uma base sólida para operações automatizadas no mercado de opções binárias. O projeto está pronto para ser testado e refinado com dados reais e em ambientes de simulação.

---

**Fim do Relatório**


