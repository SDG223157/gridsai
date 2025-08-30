from typing import List, Dict, Any
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class RebalanceAction:
    symbol: str
    action: str  # 'BUY' or 'SELL'
    value: float
    reason: str

@dataclass
class Portfolio:
    total_value: float
    positions: Dict[str, float]  # symbol -> current_value
    allocation_targets: Dict[str, float]  # symbol -> target_percentage
    rebalance_bands: Dict[str, float]  # symbol -> band_percentage

class PortfolioRebalancer:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
    
    def calculate_rebalance_actions(self) -> List[RebalanceAction]:
        actions = []
        total_value = self.portfolio.total_value
        
        for symbol, target_pct in self.portfolio.allocation_targets.items():
            current_value = self.portfolio.positions.get(symbol, 0)
            current_pct = current_value / total_value if total_value > 0 else 0
            
            target_allocation = target_pct / 100
            deviation = abs(current_pct - target_allocation)
            rebalance_band = self.portfolio.rebalance_bands.get(symbol, 5.0) / 100
            
            if deviation > rebalance_band:
                target_value = total_value * target_allocation
                trade_value = target_value - current_value
                
                if trade_value > 0:
                    action = 'BUY'
                else:
                    action = 'SELL'
                    trade_value = abs(trade_value)
                
                actions.append(RebalanceAction(
                    symbol=symbol,
                    action=action,
                    value=trade_value,
                    reason=f'Outside rebalance band by {deviation:.2%}'
                ))
        
        return self._optimize_trades(actions)
    
    def _optimize_trades(self, actions: List[RebalanceAction]) -> List[RebalanceAction]:
        """Optimize trades to minimize transaction costs"""
        buys = [a for a in actions if a.action == 'BUY']
        sells = [a for a in actions if a.action == 'SELL']
        
        # Sort by value to prioritize larger trades
        buys.sort(key=lambda x: x.value, reverse=True)
        sells.sort(key=lambda x: x.value, reverse=True)
        
        # Net out positions where possible
        optimized_actions = []
        
        for buy_action in buys:
            remaining_buy_value = buy_action.value
            
            for sell_action in sells:
                if sell_action.value > 0 and remaining_buy_value > 0:
                    net_amount = min(sell_action.value, remaining_buy_value)
                    sell_action.value -= net_amount
                    remaining_buy_value -= net_amount
            
            if remaining_buy_value > 0:
                optimized_actions.append(RebalanceAction(
                    symbol=buy_action.symbol,
                    action='BUY',
                    value=remaining_buy_value,
                    reason=buy_action.reason
                ))
        
        # Add remaining sells
        for sell_action in sells:
            if sell_action.value > 0:
                optimized_actions.append(sell_action)
        
        return optimized_actions
    
    def calculate_portfolio_metrics(self) -> Dict[str, Any]:
        """Calculate portfolio risk and performance metrics"""
        total_value = self.portfolio.total_value
        positions = self.portfolio.positions
        
        if total_value <= 0:
            return {}
        
        # Calculate concentration metrics
        concentrations = {symbol: value/total_value for symbol, value in positions.items()}
        max_concentration = max(concentrations.values()) if concentrations else 0
        
        # Calculate diversification metrics
        num_positions = len([v for v in positions.values() if v > 0])
        herfindahl_index = sum(c**2 for c in concentrations.values())
        
        return {
            'total_positions': num_positions,
            'max_concentration': max_concentration,
            'herfindahl_index': herfindahl_index,
            'diversification_ratio': 1/herfindahl_index if herfindahl_index > 0 else 0,
            'concentrations': concentrations
        }
