from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Users, Portfolios, Positions
from ..middleware.auth import get_current_user

router = APIRouter()

@router.get("")
async def get_portfolios(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's portfolios"""
    portfolios = db.query(Portfolios).filter(
        Portfolios.user_id == current_user.id
    ).all()
    
    return {"portfolios": portfolios}

@router.post("")
async def create_portfolio(
    name: str,
    strategy_type: str,
    initial_cash: float,
    base_currency: str = "USD",
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new portfolio"""
    
    portfolio = Portfolios(
        user_id=current_user.id,
        name=name,
        strategy_type=strategy_type,
        cash_balance=initial_cash,
        total_value=initial_cash,
        base_currency=base_currency
    )
    
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    
    return {"portfolio_id": portfolio.id}

@router.get("/{portfolio_id}")
async def get_portfolio(
    portfolio_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio details"""
    
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
    
    return {
        "portfolio": portfolio,
        "positions": positions
    }
