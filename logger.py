# logger.py

"""
Módulo de Logging para o Bot de Opções Binárias

Este módulo fornece uma interface centralizada para o registro de eventos,
erros e informações de trading.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class BotLogger:
    """Classe para gerenciar o logging do bot"""
    
    def __init__(self, log_file: str = "bot.log", level=logging.INFO, max_bytes: int = 5*1024*1024, backup_count: int = 5):
        self.logger = logging.getLogger("BinaryOptionsBot")
        self.logger.setLevel(level)
        
        # Garante que o diretório de logs exista
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Handler para arquivo rotativo
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(file_handler)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)
        
        self.logger.info("Logger inicializado.")
        
    def _get_formatter(self):
        """Retorna o formato do log"""
        return logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    def info(self, message: str):
        """Registra uma mensagem informativa"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """Registra uma mensagem de aviso"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """Registra uma mensagem de erro"""
        self.logger.error(message)
        
    def debug(self, message: str):
        """Registra uma mensagem de depuração"""
        self.logger.debug(message)
        
    def trade_log(self, trade_info: dict):
        """Registra informações detalhadas de um trade"""
        log_message = f"TRADE - Asset: {trade_info.get("asset")}, Direction: {trade_info.get("direction")}, " \
                      f"Amount: {trade_info.get("amount")}, Result: {trade_info.get("result")}, " \
                      f"Balance: {trade_info.get("balance_after")}, Status: {trade_info.get("status")}"
        self.logger.info(log_message)

# Exemplo de uso (para testes)
if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "bot_activity.log")
    bot_logger = BotLogger(log_file=log_path, level=logging.DEBUG)
    
    bot_logger.info("Iniciando a simulação de logs.")
    bot_logger.debug("Esta é uma mensagem de depuração.")
    bot_logger.warning("Atenção: Saldo baixo.")
    bot_logger.error("Erro crítico: Conexão com a API perdida.")
    
    trade_data = {
        "asset": "EURUSD",
        "direction": "CALL",
        "amount": 10.0,
        "result": 8.5,
        "balance_after": 1008.5,
        "status": "WON"
    }
    bot_logger.trade_log(trade_data)
    
    trade_data_loss = {
        "asset": "GBPUSD",
        "direction": "PUT",
        "amount": 10.0,
        "result": -10.0,
        "balance_after": 998.5,
        "status": "LOST"
    }
    bot_logger.trade_log(trade_data_loss)
    
    bot_logger.info("Simulação de logs concluída.")


