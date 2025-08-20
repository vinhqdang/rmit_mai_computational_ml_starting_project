import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple
import logging

class ExchangeRateDataFetcher:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, "exchange_rates.csv")
        
        os.makedirs(data_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Common currency pairs available on Yahoo Finance
        self.currency_pairs = {
            # Major pairs
            'USD_to_EUR': 'EURUSD=X',
            'USD_to_GBP': 'GBPUSD=X', 
            'USD_to_JPY': 'USDJPY=X',
            'USD_to_CHF': 'USDCHF=X',
            'USD_to_CAD': 'USDCAD=X',
            'USD_to_AUD': 'AUDUSD=X',
            'USD_to_NZD': 'NZDUSD=X',
            
            # Cross pairs
            'EUR_to_GBP': 'EURGBP=X',
            'EUR_to_JPY': 'EURJPY=X',
            'EUR_to_CHF': 'EURCHF=X',
            'GBP_to_JPY': 'GBPJPY=X',
            'GBP_to_CHF': 'GBPCHF=X',
            'CHF_to_JPY': 'CHFJPY=X',
            
            # Asian currencies
            'USD_to_CNY': 'USDCNY=X',
            'USD_to_INR': 'USDINR=X',
            'USD_to_KRW': 'USDKRW=X',
            'USD_to_SGD': 'USDSGD=X',
            'USD_to_THB': 'USDTHB=X',
            'USD_to_VND': 'USDVND=X',
            
            # Other pairs
            'USD_to_BRL': 'USDBRL=X',
            'USD_to_MXN': 'USDMXN=X',
            'USD_to_ZAR': 'USDZAR=X',
            'USD_to_RUB': 'USDRUB=X'
        }
        
        # Add reverse pairs
        reverse_pairs = {}
        for pair, symbol in self.currency_pairs.items():
            from_curr, to_curr = pair.split('_to_')
            reverse_pair = f'{to_curr}_to_{from_curr}'
            reverse_pairs[reverse_pair] = symbol  # Same symbol, will invert the rate
            
        self.currency_pairs.update(reverse_pairs)
        
        self.logger.info(f"Initialized with {len(self.currency_pairs)} currency pairs")
    
    def fetch_historical_data(self, base_currency: str = "USD", 
                            start_date: str = "2020-01-01", 
                            end_date: str = None,
                            progress_callback=None) -> pd.DataFrame:
        """
        Fetch real historical exchange rate data from Yahoo Finance
        
        Yahoo Finance provides reliable, free historical currency data going back years.
        Data is fetched efficiently in bulk rather than day-by-day API calls.
        
        Supported currency pairs: 30+ major and cross currency pairs
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        self.logger.info(f"Fetching historical data from Yahoo Finance: {start_date} to {end_date}")
        
        all_data = []
        total_pairs = len(self.currency_pairs)
        processed_pairs = 0
        
        # Group by unique Yahoo Finance symbols to avoid duplicate requests
        symbol_to_pairs = {}
        for pair, symbol in self.currency_pairs.items():
            if symbol not in symbol_to_pairs:
                symbol_to_pairs[symbol] = []
            symbol_to_pairs[symbol].append(pair)
        
        self.logger.info(f"Fetching data for {len(symbol_to_pairs)} unique currency symbols")
        
        for symbol, pairs in symbol_to_pairs.items():
            try:
                self.logger.info(f"Fetching {symbol} for pairs: {pairs}")
                
                # Fetch data from Yahoo Finance
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(start=start_date, end=end_date)
                
                if not hist_data.empty:
                    self.logger.info(f"Retrieved {len(hist_data)} records for {symbol}")
                    
                    # Process each date
                    for date, row in hist_data.iterrows():
                        date_str = date.strftime('%Y-%m-%d')
                        close_price = row['Close']
                        
                        # Find or create date row
                        date_row = None
                        for data_row in all_data:
                            if data_row['date'] == date_str:
                                date_row = data_row
                                break
                        
                        if date_row is None:
                            date_row = {'date': date_str, 'base_currency': base_currency}
                            all_data.append(date_row)
                        
                        # Add rates for all pairs using this symbol
                        for pair in pairs:
                            from_curr, to_curr = pair.split('_to_')
                            
                            # Determine if we need to invert the rate
                            if symbol.startswith(from_curr):
                                # Direct rate (e.g., USD/JPY for USD_to_JPY)
                                rate = close_price
                            else:
                                # Inverse rate (e.g., EUR/USD for USD_to_EUR)
                                rate = 1.0 / close_price if close_price != 0 else 0
                            
                            date_row[pair] = rate
                
                else:
                    self.logger.warning(f"No data retrieved for {symbol}")
                
                processed_pairs += len(pairs)
                if progress_callback:
                    progress = (processed_pairs / total_pairs) * 100
                    progress_callback(progress, f"Fetched {symbol}")
                
            except Exception as e:
                self.logger.error(f"Failed to fetch {symbol}: {e}")
                processed_pairs += len(pairs)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Save to CSV
            df.to_csv(self.data_file, index=False)
            self.logger.info(f"Saved {len(df)} records to {self.data_file}")
            
            # Log sample of available currency pairs
            sample_pairs = [col for col in df.columns if '_to_' in col][:5]
            self.logger.info(f"Currency pairs available: {sample_pairs}")
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
        """Get available currency pairs"""
        return sorted(list(self.currency_pairs.keys()))
    
    def get_available_currencies(self) -> List[str]:
        """Get list of available currencies"""
        currencies = set()
        for pair in self.currency_pairs.keys():
            from_curr, to_curr = pair.split('_to_')
            currencies.add(from_curr)
            currencies.add(to_curr)
        return sorted(list(currencies))
    
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
            # No existing data, fetch from 2020
            return self.fetch_historical_data(base_currency, "2020-01-01", 
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