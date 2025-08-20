# Exchange Rate Predictor - RMIT Machine Learning Course Starting Project

A comprehensive machine learning web application for exchange rate prediction designed for educational purposes. This project demonstrates fundamental ML concepts including data fetching, model training, prediction, and evaluation.

## 🎯 Project Overview

This starting project includes:

- **Exchange Rate Prediction**: Simple averaging model for educational demonstration
- **Web Interface**: Flask-based web application with user authentication
- **Data Management**: Automated data fetching and management system
- **Visualization**: Interactive charts showing historical rates and predictions
- **Model Evaluation**: RMSE calculation for prediction accuracy assessment
- **Logging System**: Comprehensive prediction logging and monitoring

## 🏗️ Architecture

### Core Components

1. **ExchangeRatePredictor**: Machine learning model class with train/predict methods
2. **ExchangeRateDataFetcher**: Data acquisition and management system
3. **Flask Web App**: User interface with authentication and controls
4. **Visualization Engine**: Plotly-based interactive charts

### Model Details

- **Algorithm**: Simple Moving Average (10-day window)
- **Purpose**: Educational demonstration of ML workflow
- **Data Source**: exchangerate-api.com (168+ currencies supported)
- **Historical Data**: Real historical data from 2025-01-01 onward

## 🚀 Quick Start

### Prerequisites

- Python 3.10 (conda environment recommended)
- exchangerate-api.com API key (free tier available)

### One-Command Setup and Run

```bash
# Setup and run everything
conda activate py310 && pip install -r requirements.txt && python app.py
```

### Test API Integration

```bash
# Test if everything is working
python test_api.py
```

### Step-by-Step Setup

1. **Environment Setup**:
   ```bash
   conda activate py310  # Use existing py310 environment
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   - Copy `config.json.example` to `config.json`
   - Add your exchangerate-api.com API key to `config.json`
   ```json
   {
       "api_key": "your_exchangerate_api_key_here",
       "base_currency": "USD",
       "data_start_date": "2025-01-01"
   }
   ```

4. **Run Application**:
   ```bash
   python app.py
   ```

5. **Access Web Interface**:
   - Open http://localhost:5000
   - Use demo credentials displayed on homepage

## 📊 Usage Guide

### Demo Credentials

The application displays demo credentials on the homepage:
- **student** / ml2025
- **demo** / password123  
- **admin** / rmit2025

### Basic Workflow

1. **Login** using demo credentials
2. **Fetch Data**: Click "Fetch Latest Data" to download exchange rate data
3. **Select Currency Pair**: Choose any two currencies (e.g., USD → EUR)
4. **Set Prediction Parameters**:
   - Prediction date (past dates show RMSE evaluation)
   - Number of days ahead (1-30)
5. **Make Prediction**: View results and charts
6. **Evaluate Model**: See RMSE scores for historical predictions

### Available Currencies

The system supports 168+ currencies including:
- **Major**: USD, EUR, GBP, JPY, AUD, CAD, CHF
- **Asian**: CNY, INR, KRW, SGD, THB, HKD
- **Others**: BRL, MXN, ZAR, RUB, and many more

## 🔧 Technical Details

### File Structure

```
rmit_mai_computational_ml_starting_project/
├── app.py                 # Flask web application
├── predictor.py          # ML model implementation
├── data_fetcher.py       # Data acquisition system
├── config.json           # API configuration (not in git)
├── config.json.example   # Configuration template
├── requirements.txt      # Python dependencies
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
├── static/             # CSS/JS assets (auto-created)
├── data/              # Exchange rate data (auto-created)
├── logs/              # Prediction logs (auto-created)
└── models/            # Trained models (auto-created)
```

### API Integration

- **Service**: exchangerate-api.com
- **Tier**: Free (1,500 requests/month)  
- **Features**: Real-time and historical rates, 168+ currencies
- **Date Range**: Historical data from 2025-01-01 onward

### Machine Learning Model

**Algorithm**: Simple Moving Average
```python
def predict(self, currency_pair, prediction_date, days_ahead):
    # Use average of last 10 exchange rates
    predicted_rate = np.mean(last_10_rates)
    return predictions
```

**Evaluation Metrics**:
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)

## 🧪 Educational Features

### Learning Objectives

1. **Data Pipeline**: Understand data fetching, cleaning, and storage
2. **Model Training**: Learn basic ML model structure and training
3. **Prediction**: Implement prediction logic and evaluation
4. **Web Development**: Build user interfaces for ML applications
5. **Evaluation**: Calculate and interpret model performance metrics

### Extension Ideas for Students

1. **Advanced Models**: Implement LSTM, ARIMA, or Prophet models
2. **Feature Engineering**: Add technical indicators, moving averages
3. **Real-time Updates**: Implement live data streaming
4. **Multiple Models**: Compare different prediction algorithms
5. **Risk Analysis**: Add volatility and confidence intervals

## 🔧 Development

### Running Tests

```bash
conda activate py310
pytest
```

### Development Mode

```bash
# Enable Flask debug mode
export FLASK_ENV=development
python app.py
```

### Adding New Features

1. **New Models**: Extend `ExchangeRatePredictor` class
2. **Additional Data**: Modify `ExchangeRateDataFetcher`
3. **UI Changes**: Update templates in `templates/`
4. **API Endpoints**: Add routes in `app.py`

## 📈 Model Performance

### Current Model (Simple Average)

- **Type**: Baseline model for educational purposes
- **Accuracy**: Limited (intended as starting point)
- **Training Time**: < 1 second
- **Prediction Time**: < 0.1 seconds

### Expected Results

- **RMSE**: Varies by currency pair (typically 0.01-0.1)
- **Trend**: May not capture market trends effectively
- **Use Case**: Demonstrates ML workflow concepts

## 🛠️ Troubleshooting

### Common Issues

1. **"No data available for USD_to_EUR" Error**:
   - Run `python test_api.py` to diagnose the issue
   - Click "Fetch Latest Data" button in the web interface first
   - Ensure your API key is valid in `config.json`

2. **API Key Error**: 
   - Ensure valid key in `config.json`
   - Get free key from https://www.exchangerate-api.com/
   - Check key format: should be 24 characters

3. **Missing Dependencies**: Run `pip install -r requirements.txt`

4. **Port Conflicts**: Change port in `app.py` if needed

5. **Data Fetching Fails**: 
   - Check internet connection and API limits
   - Free tier allows 1,500 requests/month

### Logs Location

- **Application Logs**: Console output
- **Prediction Logs**: `logs/predictions.log`
- **Data Files**: `data/exchange_rates.csv`

## 📚 Further Reading

### Machine Learning Concepts

- Time Series Forecasting
- Model Evaluation Metrics
- Cross-validation Techniques
- Feature Engineering

### Technical Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Plotly Documentation](https://plotly.com/python/)

## 🤝 Contributing

This is an educational project. Students are encouraged to:

1. Fork the repository
2. Implement improvements
3. Add new features
4. Share learning experiences

## 📄 License

Educational use only. Not intended for production trading or financial decisions.

## 🙋‍♂️ Support

For course-related questions, contact your RMIT instructor or use the course forum.

---

**Built for RMIT Machine Learning Course**  
*Demonstrating ML workflow fundamentals through practical application*