from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Users, Portfolios, GridConfigs, GridLevels
from ..middleware.auth import get_current_user
from ..algorithms.grid_trading import GridTradingEngine, GridConfig

router = APIRouter()

@router.get("/{portfolio_id}")
async def get_grid_configs(
    portfolio_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get grid configurations for a portfolio"""
    
    # Verify portfolio ownership
    portfolio = db.query(Portfolios).filter(
        Portfolios.id == portfolio_id,
        Portfolios.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    grid_configs = db.query(GridConfigs).filter(
        GridConfigs.portfolio_id == portfolio_id
    ).all()
    
    return {"grid_configs": grid_configs}

@router.post("/{portfolio_id}")
async def create_grid_config(
    portfolio_id: str,
    symbol: str,
    base_price: float,
    grid_spacing: float,
    num_grids_up: int,
    num_grids_down: int,
    position_size: float,
    total_investment: float,
    grid_type: str = "percentage",
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new grid configuration"""
    
    # Verify portfolio ownership
    portfolio = db.query(Portfolios).filter(
        Portfolios.id == portfolio_id,
        Portfolios.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Create grid configuration
    grid_config = GridConfigs(
        portfolio_id=portfolio_id,
        symbol=symbol.upper(),
        grid_type=grid_type,
        base_price=base_price,
        grid_spacing=grid_spacing,
        num_grids_up=num_grids_up,
        num_grids_down=num_grids_down,
        position_size=position_size,
        total_investment=total_investment
    )
    
    db.add(grid_config)
    db.flush()
    
    # Generate grid levels using the trading engine
    config = GridConfig(
        symbol=symbol.upper(),
        base_price=base_price,
        grid_spacing=grid_spacing,
        num_grids_up=num_grids_up,
        num_grids_down=num_grids_down,
        position_size=position_size,
        grid_type=grid_type
    )
    
    engine = GridTradingEngine(config)
    
    # Create grid levels in database
    for level in engine.levels:
        grid_level = GridLevels(
            grid_config_id=grid_config.id,
            level_number=level.level_number,
            trigger_price=level.trigger_price,
            target_allocation=level.target_allocation
        )
        db.add(grid_level)
    
    db.commit()
    db.refresh(grid_config)
    
    return {"grid_config_id": grid_config.id}

@router.get("/{portfolio_id}/{grid_config_id}/levels")
async def get_grid_levels(
    portfolio_id: str,
    grid_config_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get grid levels for a specific configuration"""
    
    # Verify portfolio ownership
    portfolio = db.query(Portfolios).filter(
        Portfolios.id == portfolio_id,
        Portfolios.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    grid_config = db.query(GridConfigs).filter(
        GridConfigs.id == grid_config_id,
        GridConfigs.portfolio_id == portfolio_id
    ).first()
    
    if not grid_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grid configuration not found"
        )
    
    grid_levels = db.query(GridLevels).filter(
        GridLevels.grid_config_id == grid_config_id
    ).order_by(GridLevels.level_number).all()
    
    return {
        "grid_config": grid_config,
        "grid_levels": grid_levels
    }

@router.delete("/{portfolio_id}/{grid_config_id}")
async def delete_grid_config(
    portfolio_id: str,
    grid_config_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a grid configuration"""
    
    # Verify portfolio ownership
    portfolio = db.query(Portfolios).filter(
        Portfolios.id == portfolio_id,
        Portfolios.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    grid_config = db.query(GridConfigs).filter(
        GridConfigs.id == grid_config_id,
        GridConfigs.portfolio_id == portfolio_id
    ).first()
    
    if not grid_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grid configuration not found"
        )
    
    # Delete grid levels first (cascade should handle this, but being explicit)
    db.query(GridLevels).filter(GridLevels.grid_config_id == grid_config_id).delete()
    
    # Delete grid configuration
    db.delete(grid_config)
    db.commit()
    
    return {"message": "Grid configuration deleted successfully"}
