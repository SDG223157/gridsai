from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta

from ..database import get_db
from ..models import Users, Portfolios, Positions, PriceData
from ..middleware.auth import get_current_user
from ..algorithms.portfolio_rebalancing import PortfolioRebalancer, Portfolio

router = APIRouter()

@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(
    portfolio_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio performance analytics"""
    
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
    
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    positions = db.query(Positions).filter(
        Positions.portfolio_id == portfolio_id
    ).all()
    
    # Calculate basic performance metrics
    total_value = float(portfolio.total_value)
    total_cost = sum(float(pos.quantity * pos.avg_cost) for pos in positions)
    total_pnl = sum(float(pos.unrealized_pnl) for pos in positions)
    
    performance_data = {
        "portfolio_id": portfolio_id,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "current_value": total_value,
        "total_cost": total_cost,
        "total_pnl": total_pnl,
        "total_return_pct": (total_pnl / total_cost * 100) if total_cost > 0 else 0,
        "cash_balance": float(portfolio.cash_balance),
        "positions_count": len(positions)
    }
    
    return performance_data

@router.get("/{portfolio_id}/allocation")
async def get_portfolio_allocation(
    portfolio_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current portfolio allocation breakdown"""
    
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
    
    positions = db.query(Positions).filter(
        Positions.portfolio_id == portfolio_id
    ).all()
    
    total_value = float(portfolio.total_value)
    cash_balance = float(portfolio.cash_balance)
    
    # Calculate allocations
    allocations = []
    for position in positions:
        market_value = float(position.market_value)
        allocation_pct = (market_value / total_value * 100) if total_value > 0 else 0
        
        allocations.append({
            "symbol": position.symbol,
            "asset_type": position.asset_type,
            "quantity": float(position.quantity),
            "avg_cost": float(position.avg_cost),
            "current_price": float(position.current_price),
            "market_value": market_value,
            "allocation_pct": allocation_pct,
            "unrealized_pnl": float(position.unrealized_pnl),
            "unrealized_pnl_pct": (float(position.unrealized_pnl) / (float(position.quantity) * float(position.avg_cost)) * 100) if position.quantity and position.avg_cost else 0
        })
    
    # Add cash as allocation
    cash_allocation_pct = (cash_balance / total_value * 100) if total_value > 0 else 0
    
    return {
        "portfolio_id": portfolio_id,
        "total_value": total_value,
        "cash_balance": cash_balance,
        "cash_allocation_pct": cash_allocation_pct,
        "positions": allocations,
        "summary": {
            "total_positions": len(positions),
            "largest_position_pct": max([a["allocation_pct"] for a in allocations], default=0),
            "total_equity_pct": 100 - cash_allocation_pct
        }
    }

@router.get("/{portfolio_id}/rebalance")
async def get_rebalance_recommendations(
    portfolio_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio rebalancing recommendations"""
    
    # Verify portfolio ownership
    portfolio_db = db.query(Portfolios).filter(
        Portfolios.id == portfolio_id,
        Portfolios.user_id == current_user.id
    ).first()
    
    if not portfolio_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    positions = db.query(Positions).filter(
        Positions.portfolio_id == portfolio_id
    ).all()
    
    # Build portfolio data for rebalancer
    total_value = float(portfolio_db.total_value)
    current_positions = {pos.symbol: float(pos.market_value) for pos in positions}
    
    # Get target allocations from portfolio configuration
    target_allocation = portfolio_db.target_allocation or {}
    rebalance_bands = {symbol: 5.0 for symbol in target_allocation.keys()}  # Default 5% bands
    
    if not target_allocation:
        return {
            "portfolio_id": portfolio_id,
            "message": "No target allocation configured",
            "recommendations": []
        }
    
    # Create portfolio object for rebalancer
    portfolio_obj = Portfolio(
        total_value=total_value,
        positions=current_positions,
        allocation_targets=target_allocation,
        rebalance_bands=rebalance_bands
    )
    
    rebalancer = PortfolioRebalancer(portfolio_obj)
    actions = rebalancer.calculate_rebalance_actions()
    metrics = rebalancer.calculate_portfolio_metrics()
    
    return {
        "portfolio_id": portfolio_id,
        "total_value": total_value,
        "rebalance_actions": [
            {
                "symbol": action.symbol,
                "action": action.action,
                "value": action.value,
                "reason": action.reason
            }
            for action in actions
        ],
        "portfolio_metrics": metrics,
        "needs_rebalancing": len(actions) > 0
    }

@router.get("/{portfolio_id}/risk")
async def get_risk_metrics(
    portfolio_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio risk metrics"""
    
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
    
    positions = db.query(Positions).filter(
        Positions.portfolio_id == portfolio_id
    ).all()
    
    total_value = float(portfolio.total_value)
    
    # Calculate concentration risk
    concentrations = []
    for position in positions:
        market_value = float(position.market_value)
        concentration_pct = (market_value / total_value * 100) if total_value > 0 else 0
        concentrations.append({
            "symbol": position.symbol,
            "concentration_pct": concentration_pct,
            "market_value": market_value
        })
    
    # Sort by concentration
    concentrations.sort(key=lambda x: x["concentration_pct"], reverse=True)
    
    # Calculate risk metrics
    max_concentration = max([c["concentration_pct"] for c in concentrations], default=0)
    num_positions = len([c for c in concentrations if c["concentration_pct"] > 1.0])  # Positions > 1%
    
    # Simple risk score (0-100, higher is riskier)
    risk_score = min(100, max_concentration + (10 - min(num_positions, 10)) * 2)
    
    risk_level = "Low"
    if risk_score > 70:
        risk_level = "High"
    elif risk_score > 40:
        risk_level = "Medium"
    
    return {
        "portfolio_id": portfolio_id,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "max_concentration": round(max_concentration, 2),
        "num_significant_positions": num_positions,
        "top_concentrations": concentrations[:5],  # Top 5 positions
        "recommendations": [
            "Consider diversifying if any position exceeds 20% allocation",
            "Maintain at least 10-15 different positions for proper diversification",
            "Regular rebalancing helps maintain target allocations"
        ]
    }
