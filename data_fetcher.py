import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os
from typing import Dict, List, Tuple
import logging

class ExchangeRateDataFetcher:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        
        # Load configuration
        self.config = self._load_config()
        self.api_key = self.config.get('api_key')
        
        # exchangerate-api.com v6 API endpoints
        # Note: This uses the free tier which provides current rates
        # Historical data simulation is used for educational purposes
        self.latest_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest"
        self.data_file = os.path.join(data_dir, "exchange_rates.csv")
        
        os.makedirs(data_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict:
        """Load configuration from config.json"""
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to example config
            self.logger.warning("config.json not found, using default configuration")
            return {
                "api_key": "your_api_key_here",
                "base_currency": "USD",
                "data_start_date": "2010-01-01"
            }
    
    def fetch_historical_data(self, base_currency: str = "USD", 
                            start_date: str = "2010-01-01", 
                            end_date: str = None,
                            progress_callback=None) -> pd.DataFrame:
        """
        Fetch exchange rate data and generate historical simulation
        
        Note: This project uses exchangerate-api.com for educational purposes.
        The free tier provides current exchange rates for 168+ currencies.
        Historical data is simulated based on current rates with realistic variations.
        
        Supported currencies include: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, 
        INR, KRW, SGD, NZD, MXN, BRL, ZAR, and many more.
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # For demo purposes, we'll fetch current rates and create historical simulation
        try:
            response = requests.get(self.latest_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('result') == 'success':
                    rates = data.get('conversion_rates', {})
                    
                    # Generate simulated historical data
                    all_data = self._generate_simulated_historical_data(
                        base_currency, rates, start_date, end_date, progress_callback
                    )
                    
                    df = pd.DataFrame(all_data)
                    if not df.empty:
                        df['date'] = pd.to_datetime(df['date'])
                        df = df.sort_values('date')
                        
                        # Save to CSV
                        df.to_csv(self.data_file, index=False)
                        self.logger.info(f"Saved {len(df)} records to {self.data_file}")
                    
                    return df
                else:
                    self.logger.error(f"API error: {data.get('error-type', 'Unknown error')}")
                    return pd.DataFrame()
            else:
                self.logger.error(f"HTTP error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Failed to fetch data: {e}")
            return pd.DataFrame()
    
    def _generate_simulated_historical_data(self, base_currency: str, current_rates: Dict, 
                                          start_date: str, end_date: str, 
                                          progress_callback=None) -> List[Dict]:
        """
        Generate simulated historical data based on current rates
        This is for demo purposes - adds random variations to create realistic-looking historical data
        """
        import random
        import numpy as np
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_data = []
        total_days = (end - start).days + 1
        current_date = start
        
        self.logger.info(f"Generating simulated historical data from {start_date} to {end_date}")
        
        # Set random seed for reproducible "historical" data
        random.seed(42)
        np.random.seed(42)
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            row = {
                'date': date_str,
                'base_currency': base_currency
            }
            
            # Add some realistic variation to current rates (±10% over time)
            days_from_start = (current_date - start).days
            time_factor = 1 + 0.1 * np.sin(days_from_start / 365.0 * 2 * np.pi)  # Yearly cycle
            noise_factor = 1 + np.random.normal(0, 0.02)  # Daily noise
            
            for currency, rate in current_rates.items():
                if currency != base_currency:
                    # Apply time-based variation
                    simulated_rate = rate * time_factor * noise_factor
                    row[f'{base_currency}_to_{currency}'] = simulated_rate
            
            all_data.append(row)
            
            if progress_callback:
                progress = ((current_date - start).days + 1) / total_days * 100
                progress_callback(progress)
            
            current_date += timedelta(days=1)
        
        return all_data
        
        df = pd.DataFrame(all_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Save to CSV
            df.to_csv(self.data_file, index=False)
            self.logger.info(f"Saved {len(df)} records to {self.data_file}")
        
        return df
    
    def load_data(self) -> pd.DataFrame:
        """Load exchange rate data from CSV file"""
        if os.path.exists(self.data_file):
            df = pd.read_csv(self.data_file)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()
    
    def get_currency_pairs(self) -> List[str]:
        """Get available currency pairs from the data"""
        df = self.load_data()
        if df.empty:
            # Return some common pairs for initial display
            return [
                'USD_to_EUR', 'USD_to_GBP', 'USD_to_JPY', 'USD_to_AUD', 
                'USD_to_CAD', 'USD_to_CHF', 'USD_to_CNY', 'USD_to_INR',
                'EUR_to_USD', 'EUR_to_GBP', 'EUR_to_JPY', 'GBP_to_USD'
            ]
        
        pairs = []
        for col in df.columns:
            if '_to_' in col:
                pairs.append(col)
        
        return sorted(pairs)
    
    def get_available_currencies(self) -> List[str]:
        """Get list of available currencies from the API"""
        try:
            response = requests.get(self.latest_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    rates = data.get('conversion_rates', {})
                    return sorted(list(rates.keys()))
        except Exception as e:
            self.logger.warning(f"Failed to fetch available currencies: {e}")
        
        # Fallback to common currencies
        return ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'KRW']
    
    def get_rate_data(self, currency_pair: str) -> pd.DataFrame:
        """Get specific currency pair data"""
        df = self.load_data()
        if df.empty or currency_pair not in df.columns:
            return pd.DataFrame()
        
        return df[['date', currency_pair]].copy()
    
    def update_to_latest(self, base_currency: str = "USD", progress_callback=None):
        """Update data to the latest available date"""
        df = self.load_data()
        
        if df.empty:
            # No existing data, fetch all from 2010
            return self.fetch_historical_data(base_currency, "2010-01-01", 
                                            progress_callback=progress_callback)
        
        # Get the latest date in existing data
        latest_date = df['date'].max()
        tomorrow = (latest_date + timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if tomorrow <= today:
            # Fetch missing data
            new_data = self.fetch_historical_data(base_currency, tomorrow, today,
                                                progress_callback=progress_callback)
            if not new_data.empty:
                # Combine with existing data
                combined = pd.concat([df, new_data], ignore_index=True)
                combined = combined.drop_duplicates(subset=['date'])
                combined = combined.sort_values('date')
                combined.to_csv(self.data_file, index=False)
                return combined
        
        return df
    
    def delete_all_data(self):
        """Delete all downloaded data"""
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
            self.logger.info("All data deleted")
    
    def get_date_range(self) -> Tuple[str, str]:
        """Get the date range of available data"""
        df = self.load_data()
        if df.empty:
            return None, None
        
        min_date = df['date'].min().strftime("%Y-%m-%d")
        max_date = df['date'].max().strftime("%Y-%m-%d")
        
        return min_date, max_date