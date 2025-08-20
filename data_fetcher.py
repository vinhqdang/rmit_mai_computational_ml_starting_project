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
        self.latest_api_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest"
        self.history_api_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/history"
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
                "data_start_date": "2025-01-01"
            }
    
    def fetch_historical_data(self, base_currency: str = "USD", 
                            start_date: str = "2025-01-01", 
                            end_date: str = None,
                            progress_callback=None) -> pd.DataFrame:
        """
        Fetch real historical exchange rate data from exchangerate-api.com
        
        API Format: GET https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY
        
        Note: This project fetches real historical data from 2025-01-01 onward.
        For educational purposes, we limit the date range to keep API usage reasonable.
        
        Supported currencies include: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, 
        INR, KRW, SGD, NZD, MXN, BRL, ZAR, and many more.
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Ensure we don't go before 2025-01-01
        start = datetime.strptime(start_date, "%Y-%m-%d")
        earliest_date = datetime(2025, 1, 1)
        if start < earliest_date:
            start = earliest_date
            start_date = "2025-01-01"
            self.logger.info(f"Adjusted start date to {start_date} - historical data available from 2025 onward")
        
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_data = []
        total_days = (end - start).days + 1
        current_date = start
        
        self.logger.info(f"Fetching historical data from {start_date} to {end_date}")
        self.logger.info(f"Total days to fetch: {total_days}")
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            try:
                # API format: /history/BASE_CURRENCY/YEAR/MONTH/DAY
                history_url = f"{self.history_api_url}/{base_currency}/{year}/{month}/{day}"
                self.logger.debug(f"Fetching: {history_url}")
                
                response = requests.get(history_url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('result') == 'success':
                        rates = data.get('conversion_rates', {})
                        
                        row = {
                            'date': date_str,
                            'base_currency': base_currency
                        }
                        
                        # Add forward rates (USD_to_EUR, USD_to_GBP, etc.)
                        for currency, rate in rates.items():
                            if currency != base_currency:
                                row[f'{base_currency}_to_{currency}'] = rate
                        
                        # Add reverse rates (EUR_to_USD, GBP_to_USD, etc.)
                        for currency, rate in rates.items():
                            if currency != base_currency and rate > 0:
                                row[f'{currency}_to_{base_currency}'] = 1.0 / rate
                        
                        all_data.append(row)
                        
                        if progress_callback:
                            progress = ((current_date - start).days + 1) / total_days * 100
                            progress_callback(progress, f"Fetched data for {date_str}")
                    
                    else:
                        error_type = data.get('error-type', 'Unknown error')
                        self.logger.warning(f"API error for {date_str}: {error_type}")
                        
                        # If it's just missing data for a specific date, continue
                        if 'no-data' in error_type.lower() or 'unsupported-date' in error_type.lower():
                            pass
                        else:
                            self.logger.error(f"API error: {error_type}")
                            if 'invalid-key' in error_type.lower():
                                self.logger.error("Please check your API key in config.json")
                                break
                
                elif response.status_code == 404:
                    self.logger.warning(f"No data available for {date_str}")
                
                else:
                    self.logger.warning(f"HTTP error for {date_str}: {response.status_code}")
                
                # Rate limiting - be respectful to the API
                time.sleep(0.2)
                
            except Exception as e:
                self.logger.warning(f"Failed to fetch data for {date_str}: {e}")
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(all_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Save to CSV
            df.to_csv(self.data_file, index=False)
            self.logger.info(f"Saved {len(df)} records to {self.data_file}")
            
            # Log sample of available currency pairs
            sample_pairs = [col for col in df.columns if '_to_' in col][:5]
            self.logger.info(f"Sample currency pairs available: {sample_pairs}")
        else:
            self.logger.error("No historical data was successfully fetched")
        
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
            # Use USD as base to get all available currencies
            latest_url = f"{self.latest_api_url}/USD"
            response = requests.get(latest_url, timeout=10)
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
            # No existing data, fetch from multiple base currencies for comprehensive coverage
            return self.fetch_comprehensive_data(progress_callback=progress_callback)
        
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
    
    def fetch_comprehensive_data(self, progress_callback=None):
        """Fetch data from multiple base currencies to ensure comprehensive coverage"""
        # Fetch from USD as primary base (gives us all other currencies)
        data = self.fetch_historical_data("USD", "2025-01-01", 
                                         progress_callback=progress_callback)
        
        if not data.empty:
            self.logger.info(f"Fetched comprehensive data with {len(data)} records")
            return data
        else:
            self.logger.error("Failed to fetch comprehensive data")
            return pd.DataFrame()
    
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