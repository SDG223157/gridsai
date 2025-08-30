from typing import List, Dict, Any
from dataclasses import dataclass
from decimal import Decimal
import numpy as np

@dataclass
class GridLevel:
    level_number: int
    trigger_price: float
    action: str  # 'BUY' or 'SELL'
    target_allocation: float
    is_filled: bool = False

@dataclass
class GridAction:
    level_id: str
    action: str
    quantity: float
    price: float

@dataclass
class GridConfig:
    symbol: str
    base_price: float
    grid_spacing: float  # percentage
    num_grids_up: int
    num_grids_down: int
    position_size: float
    grid_type: str = "percentage"

class GridTradingEngine:
    def __init__(self, config: GridConfig):
        self.config = config
        self.levels = self._generate_grid_levels()
    
    def _generate_grid_levels(self) -> List[GridLevel]:
        levels = []
        base_price = self.config.base_price
        spacing = self.config.grid_spacing
        
        # Generate buy levels (below base price)
        for i in range(1, self.config.num_grids_down + 1):
            price = base_price * (1 - spacing * i / 100)
            levels.append(GridLevel(
                level_number=-i,
                trigger_price=price,
                action='BUY',
                target_allocation=self.config.position_size
            ))
        
        # Generate sell levels (above base price)  
        for i in range(1, self.config.num_grids_up + 1):
            price = base_price * (1 + spacing * i / 100)
            levels.append(GridLevel(
                level_number=i,
                trigger_price=price,
                action='SELL',
                target_allocation=self.config.position_size
            ))
        
        return levels
    
    def check_triggers(self, current_price: float) -> List[GridAction]:
        actions = []
        
        for level in self.levels:
            if not level.is_filled:
                if level.action == 'BUY' and current_price <= level.trigger_price:
                    actions.append(GridAction(
                        level_id=str(level.level_number),
                        action='BUY',
                        quantity=level.target_allocation,
                        price=current_price
                    ))
                elif level.action == 'SELL' and current_price >= level.trigger_price:
                    actions.append(GridAction(
                        level_id=str(level.level_number),
                        action='SELL',
                        quantity=level.target_allocation,
                        price=current_price
                    ))
        
        return actions
    
    def update_grid_spacing(self, volatility: float):
        """Dynamically adjust grid spacing based on volatility"""
        base_spacing = self.config.grid_spacing
        volatility_multiplier = min(max(volatility / 0.02, 0.5), 2.0)  # Clamp between 0.5x and 2.0x
        new_spacing = base_spacing * volatility_multiplier
        
        self.config.grid_spacing = new_spacing
        self.levels = self._generate_grid_levels()
    
    def get_grid_statistics(self) -> Dict[str, Any]:
        filled_levels = [l for l in self.levels if l.is_filled]
        total_levels = len(self.levels)
        
        return {
            'total_levels': total_levels,
            'filled_levels': len(filled_levels),
            'utilization_rate': len(filled_levels) / total_levels if total_levels > 0 else 0,
            'buy_levels_filled': len([l for l in filled_levels if l.action == 'BUY']),
            'sell_levels_filled': len([l for l in filled_levels if l.action == 'SELL']),
            'price_range': {
                'min': min([l.trigger_price for l in self.levels]),
                'max': max([l.trigger_price for l in self.levels])
            }
        }
