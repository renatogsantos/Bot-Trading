# strategy.py

"""
Módulo de Estratégia de Trading para Opções Binárias

Este módulo contém as classes e funções responsáveis por implementar
as estratégias de negociação baseadas em indicadores técnicos.

Classes:
    SignalType: Enumeração para os tipos de sinais de trading (CALL, PUT, HOLD).
    TradingSignal: Estrutura de dados para representar um sinal de trading gerado.
    TechnicalIndicators: Classe estática para calcular diversos indicadores técnicos (RSI, MACD, SMA, EMA, Bollinger Bands).
    TradingStrategy: Classe principal que define a lógica de entrada e saída baseada em indicadores e configurações.
    MartingaleStrategy: Implementa a lógica da estratégia Martingale para gestão de stake após perdas.

Funcionalidades:
    - Análise de dados de mercado para cálculo de indicadores.
    - Geração de sinais de CALL/PUT com base em múltiplos indicadores (RSI, MACD, Bandas de Bollinger).
    - Avaliação da confiança do sinal.
    - Lógica para evitar trading em condições de mercado desfavoráveis (a ser expandida).
    - Cálculo dinâmico do stake para a estratégia Martingale.
"""

import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    """Tipos de sinais de trading"""
    CALL = "CALL"
    PUT = "PUT"
    HOLD = "HOLD"

@dataclass
class TradingSignal:
    """Estrutura de dados para sinais de trading"""
    signal_type: SignalType
    asset: str
    timestamp: pd.Timestamp
    confidence: float
    indicators: Dict[str, float]
    expiry_time: int  # em minutos

class TechnicalIndicators:
    """Classe para cálculo de indicadores técnicos"""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calcula o RSI (Relative Strength Index)"""
        return ta.rsi(data, length=period)
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calcula o MACD (Moving Average Convergence Divergence)"""
        return ta.macd(data, fast=fast, slow=slow, signal=signal)
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
        """Calcula a Média Móvel Simples"""
        return ta.sma(data, length=period)
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int = 20) -> pd.Series:
        """Calcula a Média Móvel Exponencial"""
        return ta.ema(data, length=period)
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std: float = 2) -> pd.DataFrame:
        """Calcula as Bandas de Bollinger"""
        return ta.bbands(data, length=period, std=std)

class TradingStrategy:
    """Classe principal para estratégias de trading

    Esta classe implementa a lógica de geração de sinais de compra (CALL) ou venda (PUT)
    com base na análise de indicadores técnicos como RSI, MACD e Bandas de Bollinger.
    As condições para a geração de sinais são configuráveis e a confiança do sinal
    é avaliada com base no número de condições atendidas.

    Atributos:
        config (Dict): Dicionário de configuração do bot.
        indicators (TechnicalIndicators): Instância da classe de indicadores técnicos.
        min_confidence (float): Nível mínimo de confiança para um sinal ser considerado válido.
        rsi_oversold (int): Limite inferior do RSI para identificar sobrevenda.
        rsi_overbought (int): Limite superior do RSI para identificar sobrecompra.
        use_macd (bool): Flag para ativar/desativar o uso do MACD na estratégia.
        use_bollinger_bands (bool): Flag para ativar/desativar o uso das Bandas de Bollinger.
        use_moving_averages (bool): Flag para ativar/desativar o uso de médias móveis.
        default_expiry (int): Tempo de expiração padrão para as opções em minutos.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.indicators = TechnicalIndicators()
        self.min_confidence = config.get("strategy", {}).get("min_confidence", 0.7)
        self.rsi_oversold = config.get("strategy", {}).get("rsi_oversold", 30)
        self.rsi_overbought = config.get("strategy", {}).get("rsi_overbought", 70)
        self.use_macd = config.get("strategy", {}).get("use_macd", True)
        self.use_bollinger_bands = config.get("strategy", {}).get("use_bollinger_bands", True)
        self.use_moving_averages = config.get("strategy", {}).get("use_moving_averages", True)
        self.default_expiry = config.get("trading", {}).get("default_expiry", 5)

    def analyze_market_data(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analisa os dados de mercado e calcula indicadores"""
        close_prices = data["close"]
        
        calculated_indicators = {}
        
        # Calcula RSI
        rsi = self.indicators.calculate_rsi(close_prices).iloc[-1]
        calculated_indicators["rsi"] = rsi
        
        # Calcula MACD se ativado
        if self.use_macd:
            macd_data = self.indicators.calculate_macd(close_prices)
            calculated_indicators["macd"] = macd_data["MACD_12_26_9"].iloc[-1] if "MACD_12_26_9" in macd_data.columns else 0
            calculated_indicators["macd_signal"] = macd_data["MACDs_12_26_9"].iloc[-1] if "MACDs_12_26_9" in macd_data.columns else 0
        
        # Calcula Bandas de Bollinger se ativado
        if self.use_bollinger_bands:
            bb_data = self.indicators.calculate_bollinger_bands(close_prices)
            calculated_indicators["bb_upper"] = bb_data["BBU_20_2.0"].iloc[-1] if "BBU_20_2.0" in bb_data.columns else 0
            calculated_indicators["bb_lower"] = bb_data["BBL_20_2.0"].iloc[-1] if "BBL_20_2.0" in bb_data.columns else 0
            
        # Calcula Médias Móveis se ativado
        if self.use_moving_averages:
            calculated_indicators["sma_20"] = self.indicators.calculate_sma(close_prices, 20).iloc[-1]
            calculated_indicators["ema_20"] = self.indicators.calculate_ema(close_prices, 20).iloc[-1]
        
        calculated_indicators["current_price"] = close_prices.iloc[-1]
        
        return calculated_indicators
    
    def generate_signal(self, data: pd.DataFrame, asset: str) -> Optional[TradingSignal]:
        """Gera sinal de trading baseado na análise dos dados"""
        if len(data) < 50:  # Dados insuficientes para indicadores
            return None
        
        indicators = self.analyze_market_data(data)
        
        signal_type = SignalType.HOLD
        confidence = 0.0
        
        # Regras para CALL
        call_conditions = []
        if indicators["rsi"] < self.rsi_oversold: call_conditions.append(True)
        if self.use_macd and indicators["macd"] > indicators["macd_signal"]: call_conditions.append(True)
        if self.use_bollinger_bands and indicators["current_price"] < indicators["bb_lower"]: call_conditions.append(True)
        
        # Regras para PUT
        put_conditions = []
        if indicators["rsi"] > self.rsi_overbought: put_conditions.append(True)
        if self.use_macd and indicators["macd"] < indicators["macd_signal"]: put_conditions.append(True)
        if self.use_bollinger_bands and indicators["current_price"] > indicators["bb_upper"]: put_conditions.append(True)
        
        # Avalia a confiança do sinal
        if len(call_conditions) > 0 and sum(call_conditions) / len(call_conditions) >= self.min_confidence:
            signal_type = SignalType.CALL
            confidence = sum(call_conditions) / len(call_conditions)
        elif len(put_conditions) > 0 and sum(put_conditions) / len(put_conditions) >= self.min_confidence:
            signal_type = SignalType.PUT
            confidence = sum(put_conditions) / len(put_conditions)
        
        if signal_type != SignalType.HOLD:
            return TradingSignal(
                signal_type=signal_type,
                asset=asset,
                timestamp=pd.Timestamp.now(),
                confidence=confidence,
                indicators=indicators,
                expiry_time=self.default_expiry
            )
        
        return None
    
    def should_avoid_trading(self, market_conditions: Dict) -> bool:
        """Determina se deve evitar negociar baseado nas condições de mercado"""
        # Exemplo: Evitar negociar durante alta volatilidade ou notícias importantes
        # market_conditions pode vir de um módulo de notícias ou análise de volatilidade
        
        # if market_conditions.get("volatility_index", 0) > self.config.get("max_volatility_threshold", 0.05):
        #     return True
        # if market_conditions.get("major_news_event", False):
        #     return True
        
        return False

class MartingaleStrategy:
    """Implementação da estratégia Martingale (opcional)

    Esta classe gerencia o stake das operações com base na estratégia Martingale.
    Após uma perda, o stake é dobrado até um limite máximo de multiplicador ou
    um número máximo de perdas consecutivas. Após uma vitória, o stake é resetado.

    Atributos:
        initial_stake (float): Valor inicial da aposta.
        max_multiplier (int): Multiplicador máximo permitido para o stake.
        max_consecutive_losses_martingale (int): Número máximo de perdas consecutivas antes de resetar o Martingale.
        current_multiplier (int): Multiplicador atual do stake.
        consecutive_losses (int): Contador de perdas consecutivas.
    """
    
    def __init__(self, initial_stake: float, max_multiplier: int = 4, max_consecutive_losses_martingale: int = 3):
        self.initial_stake = initial_stake
        self.max_multiplier = max_multiplier
        self.max_consecutive_losses_martingale = max_consecutive_losses_martingale
        self.current_multiplier = 1
        self.consecutive_losses = 0
    
    def calculate_next_stake(self, last_trade_result: str) -> float:
        """Calcula o próximo valor da aposta baseado no resultado anterior"""
        if last_trade_result == "win":
            self.current_multiplier = 1
            self.consecutive_losses = 0
        elif last_trade_result == "loss":
            self.consecutive_losses += 1
            if self.consecutive_losses <= self.max_consecutive_losses_martingale:
                self.current_multiplier *= 2
            else:
                self.current_multiplier = 1 # Reseta se exceder o limite de perdas consecutivas
        
        return self.initial_stake * self.current_multiplier
    
    def should_stop_martingale(self) -> bool:
        """Determina se deve parar a estratégia Martingale"""
        return self.consecutive_losses >= self.max_consecutive_losses_martingale or self.current_multiplier >= self.max_multiplier



