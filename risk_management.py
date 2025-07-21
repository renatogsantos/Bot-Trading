# risk_management.py

"""
Módulo de Gestão de Risco para Opções Binárias

Este módulo contém as classes responsáveis por gerenciar o risco
das operações, incluindo limites de perda, gestão de capital e
controles operacionais.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskMetrics:
    """Métricas de risco"""
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
    """Classe principal para gestão de risco"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.daily_stats = self._initialize_daily_stats()
        self.trade_history = []
        self.current_balance = config.get('initial_balance', 1000.0)
        self.initial_balance = self.current_balance
        self.max_balance = self.current_balance
        
        # Limites de risco
        self.max_daily_loss = config.get('max_daily_loss', 100.0)
        self.max_daily_trades = config.get('max_daily_trades', 50)
        self.max_consecutive_losses = config.get('max_consecutive_losses', 5)
        self.max_drawdown_percent = config.get('max_drawdown_percent', 20.0)
        self.min_balance = config.get('min_balance', 100.0)
        
        # Gestão de capital
        self.base_stake_percent = config.get('base_stake_percent', 2.0)  # % do saldo
        self.max_stake_percent = config.get('max_stake_percent', 5.0)
        self.min_stake = config.get('min_stake', 1.0)
        self.max_stake = config.get('max_stake', 100.0)
    
    def _initialize_daily_stats(self) -> Dict:
        """Inicializa as estatísticas diárias"""
        return {
            'date': datetime.now().date(),
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'profit': 0.0,
            'loss': 0.0,
            'consecutive_losses': 0,
            'consecutive_wins': 0,
            'last_trade_result': None
        }
    
    def can_execute_trade(self, signal, proposed_stake: float = None) -> bool:
        """Determina se um trade pode ser executado baseado nas regras de risco"""
        
        # Verifica se é um novo dia e reseta estatísticas se necessário
        self._check_new_day()
        
        # Calcula o stake se não foi fornecido
        if proposed_stake is None:
            proposed_stake = self.calculate_optimal_stake()
        
        # Verificações de risco
        checks = [
            self._check_daily_loss_limit(),
            self._check_daily_trade_limit(),
            self._check_consecutive_losses(),
            self._check_balance_limits(),
            self._check_drawdown_limit(),
            self._check_stake_limits(proposed_stake),
            self._check_market_conditions()
        ]
        
        # Registra motivos de bloqueio
        failed_checks = []
        for i, (passed, reason) in enumerate(checks):
            if not passed:
                failed_checks.append(reason)
        
        if failed_checks:
            print(f"Trade bloqueado pelos seguintes motivos: {', '.join(failed_checks)}")
            return False
        
        return True
    
    def _check_new_day(self):
        """Verifica se é um novo dia e reseta estatísticas se necessário"""
        current_date = datetime.now().date()
        if self.daily_stats['date'] != current_date:
            self.daily_stats = self._initialize_daily_stats()
    
    def _check_daily_loss_limit(self) -> tuple[bool, str]:
        """Verifica limite de perda diária"""
        if self.daily_stats['loss'] >= self.max_daily_loss:
            return False, "Limite de perda diária atingido"
        return True, ""
    
    def _check_daily_trade_limit(self) -> tuple[bool, str]:
        """Verifica limite de trades diários"""
        if self.daily_stats['trades'] >= self.max_daily_trades:
            return False, "Limite de trades diários atingido"
        return True, ""
    
    def _check_consecutive_losses(self) -> tuple[bool, str]:
        """Verifica limite de perdas consecutivas"""
        if self.daily_stats['consecutive_losses'] >= self.max_consecutive_losses:
            return False, "Muitas perdas consecutivas"
        return True, ""
    
    def _check_balance_limits(self) -> tuple[bool, str]:
        """Verifica limites de saldo"""
        if self.current_balance <= self.min_balance:
            return False, "Saldo abaixo do mínimo permitido"
        return True, ""
    
    def _check_drawdown_limit(self) -> tuple[bool, str]:
        """Verifica limite de drawdown"""
        current_drawdown = ((self.max_balance - self.current_balance) / self.max_balance) * 100
        if current_drawdown >= self.max_drawdown_percent:
            return False, f"Drawdown máximo atingido ({current_drawdown:.1f}%)"
        return True, ""
    
    def _check_stake_limits(self, stake: float) -> tuple[bool, str]:
        """Verifica limites do stake"""
        if stake < self.min_stake:
            return False, f"Stake abaixo do mínimo ({self.min_stake})"
        if stake > self.max_stake:
            return False, f"Stake acima do máximo ({self.max_stake})"
        
        stake_percent = (stake / self.current_balance) * 100
        if stake_percent > self.max_stake_percent:
            return False, f"Stake representa mais que {self.max_stake_percent}% do saldo"
        
        return True, ""
    
    def _check_market_conditions(self) -> tuple[bool, str]:
        """Verifica condições de mercado"""
        # Implementar verificações específicas de mercado
        # Por exemplo: alta volatilidade, notícias importantes, etc.
        return True, ""
    
    def calculate_optimal_stake(self) -> float:
        """Calcula o stake ótimo baseado na gestão de capital"""
        
        # Stake base como percentual do saldo
        base_stake = (self.current_balance * self.base_stake_percent) / 100
        
        # Ajusta baseado na performance recente
        win_rate = self.calculate_win_rate()
        
        if win_rate > 0.7:  # Performance boa
            multiplier = 1.2
        elif win_rate > 0.5:  # Performance média
            multiplier = 1.0
        else:  # Performance ruim
            multiplier = 0.8
        
        # Ajusta baseado em perdas consecutivas
        if self.daily_stats['consecutive_losses'] > 2:
            multiplier *= 0.5  # Reduz stake após perdas consecutivas
        
        optimal_stake = base_stake * multiplier
        
        # Aplica limites
        optimal_stake = max(self.min_stake, min(optimal_stake, self.max_stake))
        
        return round(optimal_stake, 2)
    
    def update_trade_result(self, trade_result: Dict):
        """Atualiza estatísticas baseado no resultado do trade"""
        
        self._check_new_day()
        
        result = trade_result.get('result', 0)
        stake = trade_result.get('stake', 0)
        
        # Atualiza saldo
        self.current_balance += result
        
        # Atualiza máximo se necessário
        if self.current_balance > self.max_balance:
            self.max_balance = self.current_balance
        
        # Atualiza estatísticas diárias
        self.daily_stats['trades'] += 1
        
        if result > 0:  # Ganho
            self.daily_stats['wins'] += 1
            self.daily_stats['profit'] += result
            self.daily_stats['consecutive_wins'] += 1
            self.daily_stats['consecutive_losses'] = 0
            self.daily_stats['last_trade_result'] = 'win'
        else:  # Perda
            self.daily_stats['losses'] += 1
            self.daily_stats['loss'] += abs(result)
            self.daily_stats['consecutive_losses'] += 1
            self.daily_stats['consecutive_wins'] = 0
            self.daily_stats['last_trade_result'] = 'loss'
        
        # Adiciona ao histórico
        self.trade_history.append({
            'timestamp': datetime.now(),
            'result': result,
            'stake': stake,
            'balance_after': self.current_balance
        })
    
    def calculate_win_rate(self) -> float:
        """Calcula a taxa de acerto"""
        total_trades = self.daily_stats['wins'] + self.daily_stats['losses']
        if total_trades == 0:
            return 0.0
        return self.daily_stats['wins'] / total_trades
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Retorna métricas de risco atuais"""
        
        current_drawdown = ((self.max_balance - self.current_balance) / self.max_balance) * 100
        max_drawdown = max(current_drawdown, self.config.get('historical_max_drawdown', 0))
        
        # Determina nível de risco
        risk_level = RiskLevel.LOW
        if current_drawdown > 15 or self.daily_stats['consecutive_losses'] > 3:
            risk_level = RiskLevel.HIGH
        elif current_drawdown > 10 or self.daily_stats['consecutive_losses'] > 2:
            risk_level = RiskLevel.MEDIUM
        
        if self.current_balance <= self.min_balance:
            risk_level = RiskLevel.CRITICAL
        
        return RiskMetrics(
            daily_loss=self.daily_stats['loss'],
            daily_profit=self.daily_stats['profit'],
            consecutive_losses=self.daily_stats['consecutive_losses'],
            consecutive_wins=self.daily_stats['consecutive_wins'],
            total_trades_today=self.daily_stats['trades'],
            current_drawdown=current_drawdown,
            max_drawdown=max_drawdown,
            win_rate=self.calculate_win_rate(),
            risk_level=risk_level
        )
    
    def should_stop_trading(self) -> bool:
        """Determina se o trading deve ser interrompido"""
        metrics = self.get_risk_metrics()
        
        stop_conditions = [
            metrics.risk_level == RiskLevel.CRITICAL,
            metrics.daily_loss >= self.max_daily_loss,
            metrics.consecutive_losses >= self.max_consecutive_losses,
            metrics.current_drawdown >= self.max_drawdown_percent,
            self.current_balance <= self.min_balance
        ]
        
        return any(stop_conditions)
    
    def get_daily_summary(self) -> Dict:
        """Retorna resumo das atividades do dia"""
        return {
            'date': self.daily_stats['date'].isoformat(),
            'total_trades': self.daily_stats['trades'],
            'wins': self.daily_stats['wins'],
            'losses': self.daily_stats['losses'],
            'win_rate': self.calculate_win_rate(),
            'profit': self.daily_stats['profit'],
            'loss': self.daily_stats['loss'],
            'net_result': self.daily_stats['profit'] - self.daily_stats['loss'],
            'current_balance': self.current_balance,
            'consecutive_losses': self.daily_stats['consecutive_losses'],
            'consecutive_wins': self.daily_stats['consecutive_wins']
        }
    
    def save_state(self, filepath: str):
        """Salva o estado atual do gerenciador de risco"""
        state = {
            'current_balance': self.current_balance,
            'max_balance': self.max_balance,
            'daily_stats': {
                **self.daily_stats,
                'date': self.daily_stats['date'].isoformat()
            },
            'trade_history': [
                {
                    **trade,
                    'timestamp': trade['timestamp'].isoformat()
                }
                for trade in self.trade_history[-100:]  # Salva apenas os últimos 100 trades
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Carrega o estado do gerenciador de risco"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.current_balance = state.get('current_balance', self.initial_balance)
            self.max_balance = state.get('max_balance', self.current_balance)
            
            # Carrega estatísticas diárias se for do mesmo dia
            daily_stats = state.get('daily_stats', {})
            if daily_stats.get('date') == datetime.now().date().isoformat():
                self.daily_stats = {
                    **daily_stats,
                    'date': datetime.fromisoformat(daily_stats['date']).date()
                }
            
            # Carrega histórico de trades
            trade_history = state.get('trade_history', [])
            self.trade_history = [
                {
                    **trade,
                    'timestamp': datetime.fromisoformat(trade['timestamp'])
                }
                for trade in trade_history
            ]
            
        except FileNotFoundError:
            print(f"Arquivo de estado não encontrado: {filepath}")
        except Exception as e:
            print(f"Erro ao carregar estado: {str(e)}")

class NewsFilter:
    """Filtro para evitar trading durante notícias importantes"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.high_impact_times = []  # Lista de horários de notícias importantes
    
    def is_news_time(self, timestamp: datetime = None) -> bool:
        """Verifica se é horário de notícias importantes"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Implementar lógica para verificar calendário econômico
        # Por enquanto, retorna False (sem notícias)
        return False
    
    def add_news_event(self, start_time: datetime, duration_minutes: int):
        """Adiciona um evento de notícia ao filtro"""
        end_time = start_time + timedelta(minutes=duration_minutes)
        self.high_impact_times.append((start_time, end_time))
    
    def should_avoid_trading(self, timestamp: datetime = None) -> bool:
        """Determina se deve evitar trading devido a notícias"""
        if timestamp is None:
            timestamp = datetime.now()
        
        for start_time, end_time in self.high_impact_times:
            if start_time <= timestamp <= end_time:
                return True
        
        return False

