import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import logging
from typing import List, Tuple, Dict
from sklearn.metrics import mean_squared_error

class ExchangeRatePredictor:
    def __init__(self, model_dir: str = "models", log_dir: str = "logs"):
        self.model_dir = model_dir
        self.log_dir = log_dir
        self.window_size = 10  # Use last 10 days for prediction
        self.model_params = {}
        self.is_trained = False
        
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup prediction logging
        self.prediction_log_file = os.path.join(log_dir, "predictions.log")
        self.prediction_logger = logging.getLogger("predictions")
        prediction_handler = logging.FileHandler(self.prediction_log_file)
        prediction_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.prediction_logger.addHandler(prediction_handler)
        self.prediction_logger.setLevel(logging.INFO)
    
    def train(self, data: pd.DataFrame, currency_pair: str) -> Dict:
        """
        Train the simple averaging model
        This is a demo model that uses the average of the last 10 exchange rates
        """
        if data.empty or currency_pair not in data.columns:
            raise ValueError(f"No data available for currency pair: {currency_pair}")
        
        # Sort by date
        data = data.sort_values('date').copy()
        
        # Remove any NaN values
        data = data.dropna(subset=[currency_pair])
        
        if len(data) < self.window_size:
            raise ValueError(f"Insufficient data. Need at least {self.window_size} records, got {len(data)}")
        
        # Calculate simple statistics for the model
        rates = data[currency_pair].values
        
        self.model_params = {
            'currency_pair': currency_pair,
            'mean_rate': np.mean(rates),
            'std_rate': np.std(rates),
            'last_rates': rates[-self.window_size:].tolist(),
            'training_data_points': len(data),
            'training_date_range': (data['date'].min().strftime('%Y-%m-%d'), 
                                  data['date'].max().strftime('%Y-%m-%d'))
        }
        
        self.is_trained = True
        
        # Save model
        model_file = os.path.join(self.model_dir, f"{currency_pair}_model.joblib")
        joblib.dump(self.model_params, model_file)
        
        self.logger.info(f"Model trained for {currency_pair} with {len(data)} data points")
        
        return {
            'status': 'success',
            'message': f"Model trained successfully for {currency_pair}",
            'data_points': len(data),
            'date_range': self.model_params['training_date_range']
        }
    
    def predict(self, currency_pair: str, prediction_date: str, days_ahead: int = 1) -> Dict:
        """
        Make predictions using the simple averaging model
        """
        # Load model if not in memory
        if not self.is_trained or self.model_params.get('currency_pair') != currency_pair:
            self.load_model(currency_pair)
        
        if not self.is_trained:
            raise ValueError(f"No trained model found for {currency_pair}")
        
        # Simple prediction: average of last 10 rates
        last_rates = np.array(self.model_params['last_rates'])
        predicted_rate = np.mean(last_rates)
        
        # Generate predictions for multiple days (same value since it's a simple model)
        predictions = []
        base_date = datetime.strptime(prediction_date, '%Y-%m-%d')
        
        for i in range(days_ahead):
            pred_date = base_date + timedelta(days=i)
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_rate': predicted_rate,
                'confidence': 0.7  # Fixed confidence for demo
            })
        
        # Log the prediction
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'currency_pair': currency_pair,
            'prediction_date': prediction_date,
            'days_ahead': days_ahead,
            'predicted_rate': predicted_rate,
            'model_type': 'simple_average'
        }
        
        self.prediction_logger.info(f"PREDICTION: {log_entry}")
        
        return {
            'currency_pair': currency_pair,
            'model_type': 'Simple Average (Last 10 days)',
            'predictions': predictions,
            'model_info': {
                'training_points': self.model_params['training_data_points'],
                'training_range': self.model_params['training_date_range'],
                'window_size': self.window_size
            }
        }
    
    def evaluate_model(self, test_data: pd.DataFrame, currency_pair: str, 
                      start_date: str, end_date: str) -> Dict:
        """
        Evaluate model performance on historical data
        """
        if not self.is_trained or self.model_params.get('currency_pair') != currency_pair:
            self.load_model(currency_pair)
        
        if not self.is_trained:
            raise ValueError(f"No trained model found for {currency_pair}")
        
        # Filter test data
        test_data = test_data[
            (test_data['date'] >= start_date) & 
            (test_data['date'] <= end_date)
        ].copy()
        
        if test_data.empty:
            return {'error': 'No test data available for the specified date range'}
        
        # Make predictions for each date
        actual_rates = []
        predicted_rates = []
        
        for _, row in test_data.iterrows():
            actual_rate = row[currency_pair]
            
            # Simple prediction (same as predict method)
            predicted_rate = np.mean(self.model_params['last_rates'])
            
            actual_rates.append(actual_rate)
            predicted_rates.append(predicted_rate)
        
        # Calculate RMSE
        rmse = np.sqrt(mean_squared_error(actual_rates, predicted_rates))
        mae = np.mean(np.abs(np.array(actual_rates) - np.array(predicted_rates)))
        
        return {
            'rmse': rmse,
            'mae': mae,
            'predictions_count': len(actual_rates),
            'date_range': (start_date, end_date),
            'actual_rates': actual_rates,
            'predicted_rates': predicted_rates
        }
    
    def load_model(self, currency_pair: str) -> bool:
        """Load a trained model"""
        model_file = os.path.join(self.model_dir, f"{currency_pair}_model.joblib")
        
        if os.path.exists(model_file):
            self.model_params = joblib.load(model_file)
            self.is_trained = True
            return True
        
        return False
    
    def get_model_info(self, currency_pair: str) -> Dict:
        """Get information about the trained model"""
        if not self.load_model(currency_pair):
            return {'error': f'No model found for {currency_pair}'}
        
        return {
            'currency_pair': self.model_params['currency_pair'],
            'training_data_points': self.model_params['training_data_points'],
            'training_date_range': self.model_params['training_date_range'],
            'window_size': self.window_size,
            'model_type': 'Simple Average',
            'mean_rate': self.model_params['mean_rate'],
            'std_rate': self.model_params['std_rate']
        }
    
    def retrain_model(self, data: pd.DataFrame, currency_pair: str) -> Dict:
        """Retrain the model with new data"""
        self.logger.info(f"Retraining model for {currency_pair}")
        return self.train(data, currency_pair)
    
    def get_prediction_logs(self) -> List[str]:
        """Get recent prediction logs"""
        if not os.path.exists(self.prediction_log_file):
            return []
        
        with open(self.prediction_log_file, 'r') as f:
            lines = f.readlines()
        
        # Return last 50 lines
        return lines[-50:] if len(lines) > 50 else lines
    
    def clear_prediction_logs(self):
        """Clear all prediction logs"""
        if os.path.exists(self.prediction_log_file):
            open(self.prediction_log_file, 'w').close()
            self.logger.info("Prediction logs cleared")