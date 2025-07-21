# main.py

# Este será o ponto de entrada principal para o bot de negociação de opções binárias.
# Ele orquestrará os diferentes módulos: estratégia, execução, gestão de risco, log e monitoramento.

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
            # Em um cenário real, você teria um fluxo contínuo de dados
            # Para fins de demonstração, vamos simular um DataFrame de 50 barras
            data_points = 50
            mock_data = {
                "open": [100 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "high": [101 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "low": [99 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "close": [100.5 + i * 0.1 + (time.time() % 10) for i in range(data_points)],
                "volume": [1000 + i * 10 for i in range(data_points)]
            }
            # Criar um DataFrame com um índice de tempo
            index = pd.to_datetime([datetime.now() - timedelta(minutes=data_points - 1 - i) for i in range(data_points)])
            market_data = pd.DataFrame(mock_data, index=index)

            for asset in assets_to_trade:
                # Gera sinal de trading
                signal = strategy.generate_signal(market_data, asset)

                if signal:
                    # Verifica regras de risco antes de executar o trade
                    if risk_manager.can_execute_trade(signal):
                        trade = executor.execute_trade(signal)
                        if trade:
                            # Simula o resultado do trade para o gerenciador de risco
                            # Em um cenário real, o resultado viria da corretora
                            simulated_result = trade.amount * 0.8 if trade.direction == "CALL" else -trade.amount # Simplificado
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
            
            # Verifica trades ativos e atualiza métricas de risco
            executor.check_active_trades()
            current_risk_metrics = risk_manager.get_risk_metrics()
            monitoring_system.monitor_trading_session(current_risk_metrics, risk_manager.trade_history)

            # Verifica se o bot deve parar de operar
            if risk_manager.should_stop_trading():
                logger.warning("Condições de risco atingidas. Parando o bot.")
                break

            time.sleep(check_interval)

        except Exception as e:
            logger.error(f"Erro inesperado no loop principal: {e}")
            time.sleep(check_interval) # Espera antes de tentar novamente

    logger.info("Bot de Negociação de Opções Binárias encerrado.")

if __name__ == "__main__":
    # Garante que o diretório de logs exista antes de iniciar o logger
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("reports"):
        os.makedirs("reports")
    main()


