import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import asyncio
import os

from app.data_provider import YFinanceDataProvider

st.set_page_config(
    page_title="GridTrader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "https://gridsai.app/api/v1")

def authenticate_with_token(token: str):
    """Authenticate user with JWT token"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            user_data = response.json()
            st.session_state.authenticated = True
            st.session_state.user_info = user_data
            st.session_state.access_token = token
            return True
    except Exception as e:
        st.error(f"Authentication failed: {e}")
    return False

def main():
    st.title("📈 GridTrader Pro")
    st.markdown("*Systematic Investment Management Platform*")
    
    # Check for token in URL parameters (from OAuth callback)
    query_params = st.experimental_get_query_params()
    if 'token' in query_params and not st.session_state.authenticated:
        token = query_params['token'][0]
        if authenticate_with_token(token):
            st.experimental_set_query_params()
            st.rerun()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Show user info in sidebar
    if st.session_state.user_info:
        user = st.session_state.user_info['user']
        profile = st.session_state.user_info.get('profile', {})
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Welcome back!**")
        if profile.get('avatar_url'):
            st.sidebar.image(profile['avatar_url'], width=60)
        st.sidebar.markdown(f"**{profile.get('display_name', user['email'])}**")
        st.sidebar.markdown(f"*{user['subscription_tier'].title()} Plan*")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.access_token = None
            st.rerun()
        st.sidebar.markdown("---")
    
    # Main navigation
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Grid Trading", "Portfolio", "Market Analysis", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Grid Trading":
        show_grid_trading()
    elif page == "Portfolio":
        show_portfolio()
    elif page == "Market Analysis":
        show_market_analysis()
    elif page == "Settings":
        show_settings()

def show_login():
    """Enhanced login with Google OAuth"""
    st.header("Sign in to GridTrader Pro")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔐 Google Sign-In")
        st.markdown("Quick and secure authentication")
        
        google_auth_url = f"{API_BASE_URL}/auth/google"
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{google_auth_url}" target="_self" 
               style="display: inline-block; padding: 12px 24px; 
                      background-color: #4285f4; color: white; 
                      text-decoration: none; border-radius: 8px;
                      font-weight: bold; text-align: center;">
                <img src="https://developers.google.com/identity/images/g-logo.png" 
                     width="20" style="vertical-align: middle; margin-right: 8px;">
                Continue with Google
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("🔒 We only access your email and basic profile information")
    
    with col2:
        st.subheader("📧 Email & Password")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            col_login, col_register = st.columns(2)
            
            with col_login:
                login_submitted = st.form_submit_button("Sign In", use_container_width=True)
            with col_register:
                register_submitted = st.form_submit_button("Create Account", use_container_width=True, type="secondary")
            
            if login_submitted and email and password:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={"email": email, "password": password}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if authenticate_with_token(data['access_token']):
                            st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                except Exception as e:
                    st.error(f"Login failed: {e}")
            
            if register_submitted and email and password:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/register",
                        json={
                            "email": email, 
                            "password": password,
                            "display_name": email.split('@')[0]
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if authenticate_with_token(data['access_token']):
                            st.success("Account created successfully!")
                            st.rerun()
                    else:
                        error_data = response.json()
                        st.error(f"Registration failed: {error_data.get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Registration failed: {e}")

def show_dashboard():
    """Enhanced dashboard with user-specific data"""
    st.header("Portfolio Dashboard")
    
    # Portfolio summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Portfolio Value",
            value="$125,430.50",
            delta="$2,340.20 (1.9%)"
        )
    
    with col2:
        st.metric(
            label="Today's P&L",
            value="$1,245.30",
            delta="0.99%"
        )
    
    with col3:
        st.metric(
            label="Active Grids",
            value="5",
            delta="2 new"
        )
    
    with col4:
        user_info = st.session_state.user_info
        subscription = user_info['user']['subscription_tier'] if user_info else 'free'
        st.metric(
            label="Account Status",
            value=subscription.title(),
            delta="✓ Verified" if user_info and user_info['user']['is_email_verified'] else "Pending"
        )
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Create Portfolio", use_container_width=True):
            st.session_state.show_create_portfolio = True
    
    with col2:
        if st.button("⚡ Setup Grid", use_container_width=True):
            st.session_state.page = "Grid Trading"
    
    with col3:
        if st.button("📈 Market Scan", use_container_width=True):
            st.session_state.page = "Market Analysis"
    
    with col4:
        if st.button("⚠️ View Alerts", use_container_width=True):
            st.session_state.show_alerts = True

def show_grid_trading():
    """Grid trading page"""
    st.header("Grid Trading Management")
    
    if not st.session_state.access_token:
        st.warning("Please log in to access grid trading features.")
        return
    
    st.info("Grid trading features coming soon!")

def show_portfolio():
    """Portfolio management page"""
    st.header("Portfolio Management")
    
    if not st.session_state.access_token:
        st.warning("Please log in to access portfolio features.")
        return
    
    st.info("Portfolio management features coming soon!")

def show_market_analysis():
    """Market analysis page with yfinance integration"""
    st.header("Market Analysis")
    
    symbol = st.text_input("Enter Symbol for Analysis", value="AAPL")
    
    if symbol:
        data_provider = YFinanceDataProvider()
        
        with st.spinner(f"Loading data for {symbol}..."):
            try:
                info = asyncio.run(data_provider.get_stock_info(symbol))
                hist_data = asyncio.run(data_provider.get_historical_data(symbol, period="1y"))
                
                if info and not hist_data.empty:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        fig = go.Figure(data=go.Candlestick(
                            x=hist_data['date'],
                            open=hist_data['open_price'],
                            high=hist_data['high_price'],
                            low=hist_data['low_price'],
                            close=hist_data['close_price']
                        ))
                        
                        fig.update_layout(
                            title=f"{symbol} Price Chart",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            xaxis_rangeslider_visible=False,
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.subheader("Company Info")
                        st.write(f"**Name:** {info['name']}")
                        st.write(f"**Sector:** {info['sector']}")
                        st.write(f"**Industry:** {info['industry']}")
                        st.write(f"**Exchange:** {info['exchange']}")
                        st.write(f"**Country:** {info['country']}")
                        
                        if info['market_cap']:
                            st.write(f"**Market Cap:** ${info['market_cap']:,.0f}")
                        if info['pe_ratio']:
                            st.write(f"**P/E Ratio:** {info['pe_ratio']:.2f}")
                        if info['beta']:
                            st.write(f"**Beta:** {info['beta']:.2f}")
                        if info['dividend_yield']:
                            st.write(f"**Dividend Yield:** {info['dividend_yield']:.2%}")
                
                else:
                    st.error(f"Could not load data for {symbol}")
                    
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")

def show_settings():
    """User settings page"""
    st.header("Settings")
    
    if not st.session_state.access_token:
        st.warning("Please log in to access settings.")
        return
    
    if st.session_state.user_info:
        user = st.session_state.user_info['user']
        profile = st.session_state.user_info.get('profile', {})
        
        st.subheader("Account Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Auth Provider:** {user['auth_provider'].title()}")
            st.write(f"**Account Created:** {user['created_at'][:10]}")
        
        with col2:
            st.write(f"**Subscription:** {user['subscription_tier'].title()}")
            st.write(f"**Email Verified:** {'✅' if user['is_email_verified'] else '❌'}")
            st.write(f"**User ID:** {user['id'][:8]}...")

if __name__ == "__main__":
    main()
