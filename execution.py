# execution.py

"""
Módulo de Execução de Trades para Opções Binárias

Este módulo contém as classes responsáveis por executar trades,
conectar-se à corretora e gerenciar posições.
"""

import json
import time
import asyncio
import websocket
import requests
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from enum import Enum

from code.logger import BotLogger # Importa o BotLogger

class OrderStatus(Enum):
    """Status das ordens"""
    PENDING = "pending"
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"

@dataclass
class Trade:
    """Estrutura de dados para trades"""
    trade_id: str
    asset: str
    direction: str  # CALL ou PUT
    amount: float
    entry_price: float
    expiry_time: datetime
    status: OrderStatus
    result: Optional[float] = None
    exit_price: Optional[float] = None

class DerivAPI:
    """Cliente para a API da Deriv"""
    
    def __init__(self, app_id: str, api_token: str = None, logger: Optional[BotLogger] = None):
        self.app_id = app_id
        self.api_token = api_token
        self.ws_url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
        self.ws = None
        self.is_connected = False
        self.message_handlers = {}
        self.request_id = 1
        self.logger = logger if logger else BotLogger(log_file="logs/deriv_api.log")
        
    def connect(self):
        """Conecta ao WebSocket da Deriv"""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Inicia a conexão em uma thread separada
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Aguarda a conexão
            timeout = 10
            while not self.is_connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
                
            if not self.is_connected:
                raise Exception("Falha ao conectar com a API da Deriv")
                
        except Exception as e:
            self.logger.error(f"Erro ao conectar: {str(e)}")
            raise Exception(f"Erro ao conectar: {str(e)}")
    
    def _on_open(self, ws):
        """Callback chamado quando a conexão é aberta"""
        self.is_connected = True
        self.logger.info("Conectado à API da Deriv")
        
        # Autentica se token foi fornecido
        if self.api_token:
            self.authorize()
    
    def _on_message(self, ws, message):
        """Callback chamado quando uma mensagem é recebida"""
        try:
            data = json.loads(message)
            msg_type = data.get("msg_type")
            req_id = data.get("req_id")
            
            # Chama o handler específico se existir
            if req_id in self.message_handlers:
                self.message_handlers[req_id](data)
                del self.message_handlers[req_id]
            
            # Handlers para mensagens específicas
            if msg_type == "tick":
                self._handle_tick(data)
            elif msg_type == "proposal":
                self._handle_proposal(data)
            elif msg_type == "buy":
                self._handle_buy_response(data)
                
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar mensagem: {message}")
    
    def _on_error(self, ws, error):
        """Callback chamado quando ocorre um erro"""
        self.logger.error(f"Erro na conexão WebSocket: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback chamado quando a conexão é fechada"""
        self.is_connected = False
        self.logger.info("Conexão com a API da Deriv fechada")
    
    def send_request(self, request: Dict, handler: Callable = None) -> int:
        """Envia uma requisição via WebSocket"""
        req_id = self.request_id
        self.request_id += 1
        
        request["req_id"] = req_id
        
        if handler:
            self.message_handlers[req_id] = handler
        
        if self.ws and self.is_connected:
            self.ws.send(json.dumps(request))
        else:
            self.logger.error("WebSocket não conectado ao tentar enviar requisição.")
            raise Exception("WebSocket não conectado")
        
        return req_id
    
    def authorize(self):
        """Autentica com a API usando o token"""
        request = {
            "authorize": self.api_token
        }
        self.send_request(request)
        self.logger.info("Requisição de autorização enviada.")
    
    def get_account_balance(self) -> Dict:
        """Obtém o saldo da conta"""
        request = {"balance": 1}
        return self.send_request(request)
    
    def subscribe_to_ticks(self, symbol: str):
        """Subscreve aos ticks de um ativo"""
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        self.send_request(request)
        self.logger.info(f"Subscrito aos ticks do ativo: {symbol}")
    
    def get_proposal(self, contract_type: str, symbol: str, amount: float, duration: int):
        """Obtém uma proposta de contrato"""
        request = {
            "proposal": 1,
            "amount": amount,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": duration,
            "duration_unit": "m",
            "symbol": symbol
        }
        self.logger.info(f"Solicitando proposta para {contract_type} em {symbol} com {amount} por {duration} minutos.")
        return self.send_request(request)
    
    def buy_contract(self, proposal_id: str, price: float):
        """Compra um contrato baseado na proposta"""
        request = {
            "buy": proposal_id,
            "price": price
        }
        self.logger.info(f"Enviando ordem de compra para proposal_id: {proposal_id} com preço: {price}")
        return self.send_request(request)
    
    def _handle_tick(self, data):
        """Processa dados de tick recebidos"""
        # self.logger.debug(f"Tick recebido: {data}")
        pass
    
    def _handle_proposal(self, data):
        """Processa resposta de proposta"""
        # self.logger.info(f"Proposta recebida: {data}")
        pass
    
    def _handle_buy_response(self, data):
        """Processa resposta de compra"""
        # self.logger.info(f"Resposta de compra recebida: {data}")
        pass

class TradeExecutor:
    """Classe principal para execução de trades"""
    
    def __init__(self, config: Dict, logger: Optional[BotLogger] = None):
        self.config = config
        self.logger = logger if logger else BotLogger(log_file="logs/trade_executor.log")
        self.api = None
        self.active_trades = {}
        self.trade_history = []
        self.is_trading_enabled = True
        
    def connect_to_broker(self, app_id: str, api_token: str = None):
        """Conecta à corretora"""
        try:
            self.api = DerivAPI(app_id, api_token, logger=self.logger)
            self.api.connect()
            self.logger.info("Conectado à corretora com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao conectar à corretora: {str(e)}")
            raise
    
    def execute_trade(self, signal) -> Optional[Trade]:
        """Executa um trade baseado no sinal"""
        if not self.is_trading_enabled:
            self.logger.warning("Trading desabilitado. Não foi possível executar o trade.")
            return None
        
        if not self.api or not self.api.is_connected:
            self.logger.error("API não conectada. Não foi possível executar o trade.")
            return None
        
        try:
            # Mapeia o tipo de sinal para o tipo de contrato da Deriv
            contract_type = "CALL" if signal.signal_type.value == "CALL" else "PUT"
            
            # Obtém proposta de contrato
            proposal_req_id = self.api.get_proposal(
                contract_type=contract_type,
                symbol=signal.asset,
                amount=self.config.get("trading", {}).get("default_stake", 10),
                duration=signal.expiry_time
            )
            
            # Aguarda resposta da proposta (implementação simplificada)
            time.sleep(1) # Em uma implementação real, usaria um handler assíncrono
            
            # Em uma implementação real, você processaria a resposta da proposta
            # e então executaria a compra
            
            trade = Trade(
                trade_id=f"trade_{int(time.time())}",
                asset=signal.asset,
                direction=signal.signal_type.value,
                amount=self.config.get("trading", {}).get("default_stake", 10),
                entry_price=signal.indicators["current_price"],
                expiry_time=datetime.now() + timedelta(minutes=signal.expiry_time),
                status=OrderStatus.ACTIVE
            )
            
            self.active_trades[trade.trade_id] = trade
            self.trade_history.append(trade)
            
            self.logger.trade_log({
                "asset": trade.asset,
                "direction": trade.direction,
                "amount": trade.amount,
                "status": trade.status.value,
                "trade_id": trade.trade_id
            })
            self.logger.info(f"Trade executado: {trade.trade_id} - {trade.direction} {trade.asset}")
            return trade
            
        except Exception as e:
            self.logger.error(f"Erro ao executar trade: {str(e)}")
            return None
    
    def get_market_data(self, symbol: str) -> Dict:
        """Obtém dados de mercado para um ativo"""
        # Implementação simplificada
        # Em uma implementação real, você obteria dados reais da API
        self.logger.debug(f"Obtendo dados de mercado para {symbol} (simulado).")
        return {
            "symbol": symbol,
            "price": 100.0,  # Preço fictício
            "timestamp": datetime.now()
        }
    
    def check_active_trades(self):
        """Verifica o status dos trades ativos"""
        current_time = datetime.now()
        
        for trade_id, trade in list(self.active_trades.items()):
            if current_time >= trade.expiry_time:
                # Trade expirou, determina resultado
                # Em uma implementação real, você obteria o resultado da API
                trade.status = OrderStatus.WON  # Simplificado
                trade.result = trade.amount * 0.8 if trade.status == OrderStatus.WON else -trade.amount
                
                del self.active_trades[trade_id]
                self.logger.trade_log({
                    "asset": trade.asset,
                    "direction": trade.direction,
                    "amount": trade.amount,
                    "result": trade.result,
                    "status": trade.status.value,
                    "trade_id": trade.trade_id
                })
                self.logger.info(f"Trade {trade_id} finalizado: {trade.status.value}")
    
    def get_account_balance(self) -> float:
        """Obtém o saldo atual da conta"""
        if self.api and self.api.is_connected:
            # Implementação real obteria da API
            balance = 1000.0  # Valor fictício
            self.logger.info(f"Saldo da conta: {balance}")
            return balance
        self.logger.warning("API não conectada. Não foi possível obter o saldo da conta.")
        return 0.0
    
    def cancel_trade(self, trade_id: str) -> bool:
        """Cancela um trade ativo"""
        if trade_id in self.active_trades:
            trade = self.active_trades[trade_id]
            trade.status = OrderStatus.CANCELLED
            del self.active_trades[trade_id]
            self.logger.info(f"Trade {trade_id} cancelado")
            return True
        self.logger.warning(f"Tentativa de cancelar trade {trade_id} que não está ativo.")
        return False
    
    def enable_trading(self):
        """Habilita a execução de trades"""
        self.is_trading_enabled = True
        self.logger.info("Trading habilitado")
    
    def disable_trading(self):
        """Desabilita a execução de trades"""
        self.is_trading_enabled = False
        self.logger.info("Trading desabilitado")
    
    def get_trade_history(self) -> List[Trade]:
        """Retorna o histórico de trades"""
        return self.trade_history.copy()
    
    def get_active_trades(self) -> Dict[str, Trade]:
        """Retorna os trades ativos"""
        return self.active_trades.copy()

class MockTradeExecutor(TradeExecutor):
    """Versão mock do executor para testes"""
    
    def __init__(self, config: Dict, logger: Optional[BotLogger] = None):
        super().__init__(config, logger)
        self.mock_balance = config.get("risk_management", {}).get("initial_balance", 1000.0)
        self.mock_prices = {}
    
    def connect_to_broker(self, app_id: str, api_token: str = None):
        """Simula conexão à corretora"""
        self.logger.info("Conectado à corretora (modo simulação)")
        self.api = type("MockAPI", (), {"is_connected": True})()
    
    def execute_trade(self, signal) -> Optional[Trade]:
        """Simula execução de trade"""
        if not self.is_trading_enabled:
            self.logger.warning("Trading desabilitado (simulação). Não foi possível executar o trade.")
            return None
        
        trade = Trade(
            trade_id=f"mock_trade_{int(time.time())}",
            asset=signal.asset,
            direction=signal.signal_type.value,
            amount=self.config.get("trading", {}).get("default_stake", 10),
            entry_price=signal.indicators["current_price"],
            expiry_time=datetime.now() + timedelta(minutes=signal.expiry_time),
            status=OrderStatus.ACTIVE
        )
        
        self.active_trades[trade.trade_id] = trade
        self.trade_history.append(trade)
        
        self.logger.trade_log({
            "asset": trade.asset,
            "direction": trade.direction,
            "amount": trade.amount,
            "status": trade.status.value,
            "trade_id": trade.trade_id
        })
        self.logger.info(f"Trade simulado: {trade.trade_id} - {trade.direction} {trade.asset}")
        return trade
    
    def get_account_balance(self) -> float:
        """Retorna saldo simulado"""
        self.logger.info(f"Saldo da conta (simulado): {self.mock_balance}")
        return self.mock_balance



