from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import json
import os
import threading
from data_fetcher import ExchangeRateDataFetcher
from predictor import ExchangeRatePredictor
import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.utils

app = Flask(__name__)
app.secret_key = 'rmit_ml_course_demo_key_2025'

# Initialize components
data_fetcher = ExchangeRateDataFetcher()
predictor = ExchangeRatePredictor()

# Demo credentials (displayed on homepage)
DEMO_USERS = {
    'student': 'ml2025',
    'demo': 'password123',
    'admin': 'rmit2025'
}

# Global progress tracking
progress_data = {'current': 0, 'status': 'idle', 'message': ''}

def update_progress(progress, message):
    """Update global progress"""
    global progress_data
    progress_data['current'] = progress
    progress_data['message'] = message

@app.route('/')
def home():
    """Homepage with login form and demo credentials"""
    return render_template('index.html', demo_users=DEMO_USERS)

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    username = request.form['username']
    password = request.form['password']
    
    if username in DEMO_USERS and DEMO_USERS[username] == password:
        session['logged_in'] = True
        session['username'] = username
        flash(f'Welcome, {username}!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    # Get available currency pairs
    currency_pairs = data_fetcher.get_currency_pairs()
    
    # Get available currencies for selection
    currencies = data_fetcher.get_available_currencies()
    
    # Get data date range
    min_date, max_date = data_fetcher.get_date_range()
    
    return render_template('dashboard.html', 
                         currency_pairs=currency_pairs,
                         currencies=currencies,
                         min_date=min_date,
                         max_date=max_date,
                         username=session['username'])

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        currency_pair = request.json['currency_pair']
        prediction_date = request.json['prediction_date']
        days_ahead = int(request.json['days_ahead'])
        
        # Check if we have a trained model
        if not predictor.load_model(currency_pair):
            # Train model first
            data = data_fetcher.get_rate_data(currency_pair)
            if data.empty:
                return jsonify({'error': f'No data available for {currency_pair}'}), 400
            
            train_result = predictor.train(data, currency_pair)
            if train_result['status'] != 'success':
                return jsonify({'error': 'Failed to train model'}), 500
        
        # Make prediction
        result = predictor.predict(currency_pair, prediction_date, days_ahead)
        
        # Check if we can calculate RMSE (if prediction date is in the past)
        pred_date = datetime.strptime(prediction_date, '%Y-%m-%d')
        end_date = pred_date + timedelta(days=days_ahead-1)
        today = datetime.now()
        
        rmse = None
        if end_date < today:
            # We can calculate RMSE
            data = data_fetcher.get_rate_data(currency_pair)
            if not data.empty:
                eval_result = predictor.evaluate_model(
                    data, currency_pair, 
                    prediction_date, 
                    end_date.strftime('%Y-%m-%d')
                )
                if 'rmse' in eval_result:
                    rmse = eval_result['rmse']
        
        result['rmse'] = rmse
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    """Retrain model"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        currency_pair = request.json['currency_pair']
        
        data = data_fetcher.get_rate_data(currency_pair)
        if data.empty:
            return jsonify({'error': f'No data available for {currency_pair}'}), 400
        
        result = predictor.retrain_model(data, currency_pair)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    """Fetch latest exchange rate data"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    def fetch_in_background():
        global progress_data
        progress_data['status'] = 'fetching'
        progress_data['current'] = 0
        progress_data['message'] = 'Fetching exchange rate data...'
        
        try:
            data_fetcher.update_to_latest(progress_callback=update_progress)
            progress_data['status'] = 'completed'
            progress_data['message'] = 'Data fetching completed'
        except Exception as e:
            progress_data['status'] = 'error'
            progress_data['message'] = f'Error: {str(e)}'
    
    # Start background task
    thread = threading.Thread(target=fetch_in_background)
    thread.start()
    
    return jsonify({'status': 'started', 'message': 'Data fetching started'})

@app.route('/delete_data', methods=['POST'])
def delete_data():
    """Delete all downloaded data"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data_fetcher.delete_all_data()
        return jsonify({'status': 'success', 'message': 'All data deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress')
def get_progress():
    """Get current progress"""
    return jsonify(progress_data)

@app.route('/chart_data')
def chart_data():
    """Get data for charts"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    currency_pair = request.args.get('currency_pair')
    if not currency_pair:
        return jsonify({'error': 'Currency pair required'}), 400
    
    data = data_fetcher.get_rate_data(currency_pair)
    if data.empty:
        return jsonify({'error': 'No data available'}), 400
    
    # Prepare data for chart
    chart_data = {
        'dates': data['date'].dt.strftime('%Y-%m-%d').tolist(),
        'rates': data[currency_pair].tolist(),
        'currency_pair': currency_pair
    }
    
    return jsonify(chart_data)

@app.route('/prediction_logs')
def prediction_logs():
    """Get prediction logs"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    logs = predictor.get_prediction_logs()
    return jsonify({'logs': logs})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    """Clear prediction logs"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    predictor.clear_prediction_logs()
    return jsonify({'status': 'success', 'message': 'Logs cleared'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)