# backtesting_module.py

"""
Módulo de Backtesting para o Bot de Opções Binárias

Este módulo integra a biblioteca Backtesting.py para simular
o desempenho das estratégias de trading com dados históricos,
considerando custos reais como comissões e slippage.
"""

import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from typing import Dict

# Importa a estratégia de trading desenvolvida
from code.strategy import TradingStrategy, SignalType

class BinaryOptionsStrategy(Strategy):
    """Adaptação da TradingStrategy para o framework Backtesting.py"""
    
    # Define parâmetros da estratégia que podem ser otimizados no backtest
    # Estes serão passados para a TradingStrategy
    rsi_oversold = 30
    rsi_overbought = 70
    min_confidence = 0.7
    default_expiry = 5
    
    def init(self):
        """Inicializa a estratégia, criando instâncias dos indicadores e da lógica de trading"""
        # Configuração para a TradingStrategy
        config = {
            "strategy": {
                "rsi_oversold": self.rsi_oversold,
                "rsi_overbought": self.rsi_overbought,
                "min_confidence": self.min_confidence,
                "use_macd": True, # Exemplo: pode ser parametrizado também
                "use_bollinger_bands": True,
                "use_moving_averages": True
            },
            "trading": {
                "default_expiry": self.default_expiry
            }
        }
        self.trading_strategy = TradingStrategy(config)
        
        # Prepara os dados para a TradingStrategy
        # O Backtesting.py passa o self.data como um objeto numpy recarregável
        # Precisamos convertê-lo para um DataFrame pandas para nossa TradingStrategy
        self.df_data = pd.DataFrame({
            'Open': self.data.Open,
            'High': self.data.High,
            'Low': self.data.Low,
            'Close': self.data.Close,
            'Volume': self.data.Volume
        }, index=self.data.index)

    def next(self):
        """Define a lógica de trading para cada nova barra de dados"""
        # Atualiza o DataFrame com os dados mais recentes
        current_data = pd.DataFrame({
            'Open': self.data.Open,
            'High': self.data.High,
            'Low': self.data.Low,
            'Close': self.data.Close,
            'Volume': self.data.Volume
        }, index=self.data.index)
        
        # Gera um sinal usando nossa TradingStrategy
        signal = self.trading_strategy.generate_signal(current_data, asset="SimulatedAsset")
        
        if signal:
            if signal.signal_type == SignalType.CALL:
                # Para opções binárias, a compra é imediata e o resultado é fixo
                # O Backtesting.py não simula opções binárias diretamente, então adaptamos.
                # Uma compra de CALL significa que esperamos que o preço suba.
                # No backtesting, isso se traduz em uma posição de compra.
                self.buy()
            elif signal.signal_type == SignalType.PUT:
                # Uma compra de PUT significa que esperamos que o preço caia.
                # No backtesting, isso se traduz em uma posição de venda.
                self.sell()

def run_backtest(data: pd.DataFrame, config: Dict) -> Dict:
    """Executa o backtest da estratégia"""
    
    # Adapta o DataFrame para o formato esperado pelo Backtesting.py
    # Ele espera colunas Open, High, Low, Close, Volume
    data.columns = [col.capitalize() for col in data.columns]
    
    bt = Backtest(data, BinaryOptionsStrategy, 
                  cash=config.get("risk_management", {}).get("initial_balance", 10000),
                  commission=config.get("backtesting", {}).get("commission", 0.0),
                  exclusive_orders=True)
    
    # Otimização de parâmetros (exemplo)
    # stats = bt.run(maximize=\'Equity Final [$]\')
    
    stats = bt.run()
    
    print(stats)
    
    # Retorna as estatísticas do backtest
    return stats

# Exemplo de uso (para testes)
if __name__ == "__main__":
    # Gerar dados fictícios para teste
    import numpy as np
    dates = pd.date_range("2023-01-01", periods=100, freq="H")
    data = pd.DataFrame({
        "open": np.random.rand(100) * 100,
        "high": np.random.rand(100) * 100 + 5,
        "low": np.random.rand(100) * 100 - 5,
        "close": np.random.rand(100) * 100,
        "volume": np.random.randint(100, 1000, 100)
    }, index=dates)
    
    # Carregar configuração (exemplo)
    import json
    with open("../config/settings.json", "r") as f:
        test_config = json.load(f)
        
    run_backtest(data, test_config)


