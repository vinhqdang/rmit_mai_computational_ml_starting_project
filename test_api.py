#!/usr/bin/env python3
"""
Test script to verify API integration and data fetching
"""

import sys
import json
from data_fetcher import ExchangeRateDataFetcher
from predictor import ExchangeRatePredictor

def test_yahoo_finance():
    """Test Yahoo Finance data fetching"""
    print("🌐 Testing Yahoo Finance connection...")
    try:
        fetcher = ExchangeRateDataFetcher()
        
        # Test getting available currencies
        currencies = fetcher.get_available_currencies()
        print(f"✅ Available currencies: {len(currencies)} found")
        print(f"   Sample: {currencies[:10]}")
        
        # Test getting available currency pairs
        pairs = fetcher.get_currency_pairs()
        print(f"✅ Available currency pairs: {len(pairs)} found")
        print(f"   Sample: {pairs[:10]}")
        
        # Test fetching small amount of historical data
        print("\n📊 Testing historical data fetch...")
        data = fetcher.fetch_historical_data("USD", "2024-01-01", "2024-01-05")
        
        if not data.empty:
            print(f"✅ Historical data fetched successfully: {len(data)} records")
            
            # Show available currency pairs
            pairs = [col for col in data.columns if '_to_' in col]
            print(f"✅ Currency pairs available: {len(pairs)}")
            print(f"   Sample pairs: {pairs[:5]}")
            
            # Test specific pair
            if 'USD_to_EUR' in pairs:
                print(f"✅ USD_to_EUR data available")
                sample_data = data[['date', 'USD_to_EUR']].head()
                print(f"   Sample data:\n{sample_data}")
            else:
                print("❌ USD_to_EUR not found in data")
                
            return True
        else:
            print("❌ No data returned from API")
            return False
            
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_prediction():
    """Test prediction functionality"""
    print("\n🔮 Testing prediction functionality...")
    try:
        fetcher = ExchangeRateDataFetcher()
        predictor = ExchangeRatePredictor()
        
        # Ensure we have some data
        data = fetcher.fetch_historical_data("USD", "2024-01-01", "2024-01-10")
        
        if data.empty:
            print("❌ No data available for prediction test")
            return False
        
        # Test training
        currency_pair = "USD_to_EUR"
        if currency_pair not in data.columns:
            print(f"❌ {currency_pair} not available")
            return False
            
        pair_data = data[['date', currency_pair]].copy()
        train_result = predictor.train(pair_data, currency_pair)
        
        if train_result['status'] == 'success':
            print(f"✅ Model trained successfully for {currency_pair}")
            
            # Test prediction
            pred_result = predictor.predict(currency_pair, "2024-01-11", 5)
            print(f"✅ Prediction made for 5 days")
            print(f"   Predicted rate: {pred_result['predictions'][0]['predicted_rate']:.4f}")
            
            return True
        else:
            print("❌ Model training failed")
            return False
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 RMIT ML Exchange Rate Predictor - Yahoo Finance Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test Yahoo Finance connection
    if not test_yahoo_finance():
        all_passed = False
    
    # Test prediction
    if not test_prediction():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("💡 You can now run: python app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("💡 Make sure:")
        print("   1. Internet connection is available")
        print("   2. All dependencies are installed (pip install -r requirements.txt)")
        print("   3. Yahoo Finance is accessible")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())