# monitoring.py

"""
Módulo de Monitoramento e Alertas para o Bot de Opções Binárias

Este módulo contém as classes responsáveis por gerar relatórios
de performance e enviar alertas via e-mail ou Telegram.
"""

import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from code.logger import BotLogger

class PerformanceReporter:
    """Classe para gerar relatórios de performance"""
    
    def __init__(self, config: Dict, logger: Optional[BotLogger] = None):
        self.config = config
        self.logger = logger if logger else BotLogger(log_file="logs/performance.log")
    
    def calculate_metrics(self, trade_history: List[Dict]) -> Dict:
        """Calcula métricas de performance baseado no histórico de trades"""
        if not trade_history:
            return {}
        
        # Converte para DataFrame para facilitar cálculos
        df = pd.DataFrame(trade_history)
        
        # Métricas básicas
        total_trades = len(df)
        wins = len(df[df['result'] > 0])
        losses = len(df[df['result'] <= 0])
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        # Retornos
        total_return = df['result'].sum()
        avg_return_per_trade = df['result'].mean()
        
        # Drawdown
        cumulative_returns = df['result'].cumsum()
        running_max = cumulative_returns.expanding().max()
        drawdown = cumulative_returns - running_max
        max_drawdown = drawdown.min()
        
        # Sharpe Ratio (simplificado)
        returns = df['result']
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Perdas e ganhos consecutivos
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for result in df['result']:
            if result > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_return': total_return,
            'avg_return_per_trade': avg_return_per_trade,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'report_date': datetime.now().isoformat()
        }
    
    def generate_daily_report(self, trade_history: List[Dict], risk_metrics: Dict) -> str:
        """Gera relatório diário de performance"""
        metrics = self.calculate_metrics(trade_history)
        
        report = f"""
RELATÓRIO DIÁRIO DE PERFORMANCE - {datetime.now().strftime('%d/%m/%Y')}
================================================================

RESUMO GERAL:
- Total de Trades: {metrics.get('total_trades', 0)}
- Vitórias: {metrics.get('wins', 0)}
- Derrotas: {metrics.get('losses', 0)}
- Taxa de Acerto: {metrics.get('win_rate', 0):.2%}

PERFORMANCE FINANCEIRA:
- Retorno Total: ${metrics.get('total_return', 0):.2f}
- Retorno Médio por Trade: ${metrics.get('avg_return_per_trade', 0):.2f}
- Drawdown Máximo: ${metrics.get('max_drawdown', 0):.2f}
- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}

SEQUÊNCIAS:
- Máximo de Vitórias Consecutivas: {metrics.get('max_consecutive_wins', 0)}
- Máximo de Derrotas Consecutivas: {metrics.get('max_consecutive_losses', 0)}

GESTÃO DE RISCO:
- Saldo Atual: ${risk_metrics.get('current_balance', 0):.2f}
- Drawdown Atual: {risk_metrics.get('current_drawdown', 0):.2f}%
- Nível de Risco: {risk_metrics.get('risk_level', 'N/A')}
- Perdas Consecutivas Atuais: {risk_metrics.get('consecutive_losses', 0)}

================================================================
Relatório gerado automaticamente pelo Bot de Opções Binárias
        """
        
        return report
    
    def save_report(self, report: str, filename: str = None):
        """Salva o relatório em arquivo"""
        if filename is None:
            filename = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Relatório salvo em: {filename}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {str(e)}")

class AlertManager:
    """Classe para gerenciar alertas via e-mail e Telegram"""
    
    def __init__(self, config: Dict, logger: Optional[BotLogger] = None):
        self.config = config
        self.logger = logger if logger else BotLogger(log_file="logs/alerts.log")
        
        # Configurações de e-mail
        self.email_enabled = config.get("alerts", {}).get("email_enabled", False)
        self.smtp_server = config.get("alerts", {}).get("email_smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("alerts", {}).get("email_port", 587)
        self.email_username = config.get("alerts", {}).get("email_username", "")
        self.email_password = config.get("alerts", {}).get("email_password", "")
        
        # Configurações do Telegram
        self.telegram_enabled = config.get("alerts", {}).get("telegram_enabled", False)
        self.telegram_bot_token = config.get("alerts", {}).get("telegram_bot_token", "")
        self.telegram_chat_id = config.get("alerts", {}).get("telegram_chat_id", "")
    
    def send_email_alert(self, subject: str, message: str, to_email: str = None):
        """Envia alerta por e-mail"""
        if not self.email_enabled:
            self.logger.warning("E-mail não está habilitado nas configurações.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = to_email or self.email_username
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_username, to_email or self.email_username, text)
            server.quit()
            
            self.logger.info(f"E-mail enviado com sucesso: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar e-mail: {str(e)}")
            return False
    
    def send_telegram_alert(self, message: str):
        """Envia alerta via Telegram"""
        if not self.telegram_enabled:
            self.logger.warning("Telegram não está habilitado nas configurações.")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info("Mensagem Telegram enviada com sucesso")
                return True
            else:
                self.logger.error(f"Erro ao enviar mensagem Telegram: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem Telegram: {str(e)}")
            return False
    
    def send_alert(self, subject: str, message: str, alert_type: str = "info"):
        """Envia alerta via todos os canais habilitados"""
        formatted_message = f"[{alert_type.upper()}] {message}"
        
        # Envia por e-mail
        if self.email_enabled:
            self.send_email_alert(subject, formatted_message)
        
        # Envia por Telegram
        if self.telegram_enabled:
            telegram_message = f"<b>{subject}</b>\n\n{formatted_message}"
            self.send_telegram_alert(telegram_message)
    
    def check_and_send_alerts(self, risk_metrics: Dict, trade_result: Dict = None):
        """Verifica condições e envia alertas quando necessário"""
        
        # Alerta de drawdown alto
        if risk_metrics.get('current_drawdown', 0) > 15:
            self.send_alert(
                "⚠️ ALERTA: Drawdown Alto",
                f"Drawdown atual: {risk_metrics.get('current_drawdown', 0):.2f}%\n"
                f"Saldo atual: ${risk_metrics.get('current_balance', 0):.2f}",
                "warning"
            )
        
        # Alerta de perdas consecutivas
        if risk_metrics.get('consecutive_losses', 0) >= 3:
            self.send_alert(
                "🚨 ALERTA: Perdas Consecutivas",
                f"Perdas consecutivas: {risk_metrics.get('consecutive_losses', 0)}\n"
                f"Considere revisar a estratégia ou pausar o trading.",
                "warning"
            )
        
        # Alerta de risco crítico
        if risk_metrics.get('risk_level') == 'CRITICAL':
            self.send_alert(
                "🔴 ALERTA CRÍTICO: Trading Interrompido",
                f"Nível de risco crítico atingido!\n"
                f"Saldo atual: ${risk_metrics.get('current_balance', 0):.2f}\n"
                f"Trading foi automaticamente interrompido.",
                "critical"
            )
        
        # Alerta de trade perdido (opcional)
        if trade_result and trade_result.get('result', 0) < 0:
            loss_amount = abs(trade_result.get('result', 0))
            if loss_amount > 50:  # Alerta para perdas grandes
                self.send_alert(
                    "📉 Trade com Perda Significativa",
                    f"Perda de ${loss_amount:.2f} no trade {trade_result.get('trade_id', 'N/A')}\n"
                    f"Ativo: {trade_result.get('asset', 'N/A')}\n"
                    f"Direção: {trade_result.get('direction', 'N/A')}",
                    "info"
                )

class MonitoringSystem:
    """Sistema principal de monitoramento"""
    
    def __init__(self, config: Dict, logger: Optional[BotLogger] = None):
        self.config = config
        self.logger = logger if logger else BotLogger(log_file="logs/monitoring.log")
        self.performance_reporter = PerformanceReporter(config, logger)
        self.alert_manager = AlertManager(config, logger)
        self.last_report_date = None
    
    def monitor_trading_session(self, risk_metrics: Dict, trade_history: List[Dict], trade_result: Dict = None):
        """Monitora uma sessão de trading"""
        
        # Verifica e envia alertas
        self.alert_manager.check_and_send_alerts(risk_metrics, trade_result)
        
        # Gera relatório diário se necessário
        current_date = datetime.now().date()
        if self.last_report_date != current_date:
            self.generate_daily_report(trade_history, risk_metrics)
            self.last_report_date = current_date
    
    def generate_daily_report(self, trade_history: List[Dict], risk_metrics: Dict):
        """Gera e envia relatório diário"""
        try:
            report = self.performance_reporter.generate_daily_report(trade_history, risk_metrics)
            
            # Salva o relatório
            self.performance_reporter.save_report(report)
            
            # Envia por e-mail/Telegram se habilitado
            self.alert_manager.send_alert(
                "📊 Relatório Diário de Performance",
                report,
                "info"
            )
            
            self.logger.info("Relatório diário gerado e enviado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório diário: {str(e)}")

# Exemplo de uso
if __name__ == "__main__":
    # Configuração de exemplo
    config = {
        "alerts": {
            "email_enabled": False,
            "telegram_enabled": False
        }
    }
    
    # Dados de exemplo
    trade_history = [
        {"result": 10, "asset": "EURUSD", "direction": "CALL"},
        {"result": -10, "asset": "GBPUSD", "direction": "PUT"},
        {"result": 8, "asset": "EURUSD", "direction": "CALL"}
    ]
    
    risk_metrics = {
        "current_balance": 1000,
        "current_drawdown": 5,
        "risk_level": "LOW",
        "consecutive_losses": 1
    }
    
    # Teste do sistema de monitoramento
    monitoring = MonitoringSystem(config)
    monitoring.monitor_trading_session(risk_metrics, trade_history)

