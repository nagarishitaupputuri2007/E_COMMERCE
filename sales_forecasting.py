import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Set style for visualizations
plt.style.use('seaborn')
sns.set_palette("husl")

def load_processed_data():
    """
    Load the processed time series data
    """
    print("Loading processed time series data...")
    daily_sales = pd.read_csv('daily_sales_processed.csv', parse_dates=['order_date'], index_col='order_date')
    return daily_sales

def prepare_data_for_models(daily_sales, test_size=0.2):
    """
    Prepare data for different forecasting models
    """
    print("Preparing data for forecasting models...")
    
    # Calculate split point
    split_point = int(len(daily_sales) * (1 - test_size))
    
    # Split data
    train_data = daily_sales.iloc[:split_point]
    test_data = daily_sales.iloc[split_point:]
    
    # Prepare data for Prophet
    prophet_train = pd.DataFrame({
        'ds': train_data.index,
        'y': train_data['amount']
    })
    prophet_test = pd.DataFrame({
        'ds': test_data.index,
        'y': test_data['amount']
    })
    
    # Prepare data for LSTM
    def create_sequences(data, seq_length=7):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)
    
    # Scale data for LSTM
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(daily_sales[['amount']])
    
    # Create sequences for LSTM
    X, y = create_sequences(scaled_data)
    X_train = X[:split_point-7]
    y_train = y[:split_point-7]
    X_test = X[split_point-7:]
    y_test = y[split_point-7:]
    
    return {
        'original': (train_data, test_data),
        'prophet': (prophet_train, prophet_test),
        'lstm': (X_train, y_train, X_test, y_test, scaler)
    }

def train_holt_winters(train_data):
    """
    Train Holt-Winters model
    """
    print("Training Holt-Winters model...")
    
    model = ExponentialSmoothing(
        train_data['amount'],
        seasonal_periods=7,
        trend='add',
        seasonal='add'
    ).fit()
    
    return model

def train_arima(train_data):
    """
    Train ARIMA model
    """
    print("Training ARIMA model...")
    
    model = ARIMA(train_data['amount'], order=(1, 1, 1)).fit()
    return model

def train_prophet(prophet_train):
    """
    Train Prophet model
    """
    print("Training Prophet model...")
    
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='additive'
    )
    model.fit(prophet_train)
    return model

def train_lstm(X_train, y_train):
    """
    Train LSTM model
    """
    print("Training LSTM model...")
    
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(X_train.shape[1], 1), return_sequences=True),
        Dropout(0.2),
        LSTM(50, activation='relu'),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)
    
    return model

def evaluate_models(models, data, test_periods=30):
    """
    Evaluate different forecasting models
    """
    print("Evaluating model performance...")
    
    results = {}
    train_data, test_data = data['original']
    
    # Evaluate Holt-Winters
    hw_forecast = models['holt_winters'].forecast(test_periods)
    hw_rmse = np.sqrt(mean_squared_error(test_data['amount'][:test_periods], hw_forecast))
    hw_mape = mean_absolute_percentage_error(test_data['amount'][:test_periods], hw_forecast)
    results['Holt-Winters'] = {'rmse': hw_rmse, 'mape': hw_mape}
    
    # Evaluate ARIMA
    arima_forecast = models['arima'].forecast(test_periods)
    arima_rmse = np.sqrt(mean_squared_error(test_data['amount'][:test_periods], arima_forecast))
    arima_mape = mean_absolute_percentage_error(test_data['amount'][:test_periods], arima_forecast)
    results['ARIMA'] = {'rmse': arima_rmse, 'mape': arima_mape}
    
    # Evaluate Prophet
    future_dates = models['prophet'].make_future_dataframe(periods=test_periods)
    prophet_forecast = models['prophet'].predict(future_dates)
    prophet_rmse = np.sqrt(mean_squared_error(
        test_data['amount'][:test_periods],
        prophet_forecast.tail(test_periods)['yhat']
    ))
    prophet_mape = mean_absolute_percentage_error(
        test_data['amount'][:test_periods],
        prophet_forecast.tail(test_periods)['yhat']
    )
    results['Prophet'] = {'rmse': prophet_rmse, 'mape': prophet_mape}
    
    # Evaluate LSTM
    X_train, y_train, X_test, y_test, scaler = data['lstm']
    lstm_pred = models['lstm'].predict(X_test[:test_periods])
    lstm_pred = scaler.inverse_transform(lstm_pred)
    lstm_actual = scaler.inverse_transform(y_test[:test_periods].reshape(-1, 1))
    lstm_rmse = np.sqrt(mean_squared_error(lstm_actual, lstm_pred))
    lstm_mape = mean_absolute_percentage_error(lstm_actual, lstm_pred)
    results['LSTM'] = {'rmse': lstm_rmse, 'mape': lstm_mape}
    
    return results

def generate_forecasts(models, data, forecast_periods=180):
    """
    Generate forecasts for future periods
    """
    print("Generating forecasts...")
    
    forecasts = {}
    
    # Generate Holt-Winters forecast
    hw_forecast = models['holt_winters'].forecast(forecast_periods)
    forecasts['Holt-Winters'] = hw_forecast
    
    # Generate ARIMA forecast
    arima_forecast = models['arima'].forecast(forecast_periods)
    forecasts['ARIMA'] = arima_forecast
    
    # Generate Prophet forecast
    future_dates = models['prophet'].make_future_dataframe(periods=forecast_periods)
    prophet_forecast = models['prophet'].predict(future_dates)
    forecasts['Prophet'] = prophet_forecast.tail(forecast_periods)['yhat']
    
    # Generate LSTM forecast
    X_train, y_train, X_test, y_test, scaler = data['lstm']
    lstm_forecast = []
    last_sequence = X_test[-1]
    
    for _ in range(forecast_periods):
        next_pred = models['lstm'].predict(last_sequence.reshape(1, 7, 1))
        lstm_forecast.append(next_pred[0, 0])
        last_sequence = np.roll(last_sequence, -1)
        last_sequence[-1] = next_pred
    
    lstm_forecast = scaler.inverse_transform(np.array(lstm_forecast).reshape(-1, 1))
    forecasts['LSTM'] = pd.Series(lstm_forecast.flatten())
    
    return forecasts

def create_forecast_visualizations(daily_sales, forecasts, evaluation_results):
    """
    Create visualizations for forecasting results
    """
    print("Creating forecast visualizations...")
    
    # Plot historical data with forecasts
    plt.figure(figsize=(15, 8))
    plt.plot(daily_sales.index, daily_sales['amount'], label='Historical Data', alpha=0.7)
    
    future_dates = pd.date_range(
        start=daily_sales.index[-1] + timedelta(days=1),
        periods=len(next(iter(forecasts.values()))),
        freq='D'
    )
    
    for model_name, forecast in forecasts.items():
        plt.plot(future_dates, forecast, label=f'{model_name} Forecast', alpha=0.7)
    
    plt.title('Sales Forecasts Comparison')
    plt.xlabel('Date')
    plt.ylabel('Sales Amount')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('sales_forecasts_comparison.png')
    plt.close()
    
    # Create evaluation metrics comparison
    plt.figure(figsize=(10, 6))
    models = list(evaluation_results.keys())
    rmse_values = [results['rmse'] for results in evaluation_results.values()]
    mape_values = [results['mape'] * 100 for results in evaluation_results.values()]
    
    x = np.arange(len(models))
    width = 0.35
    
    plt.bar(x - width/2, rmse_values, width, label='RMSE')
    plt.bar(x + width/2, mape_values, width, label='MAPE (%)')
    
    plt.xlabel('Models')
    plt.ylabel('Error Metrics')
    plt.title('Model Performance Comparison')
    plt.xticks(x, models, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('forecast_model_comparison.png')
    plt.close()

def generate_forecast_report(evaluation_results, best_model):
    """
    Generate a report summarizing the forecasting results
    """
    print("Generating forecasting report...")
    
    report_content = """# Sales Forecasting Analysis Report

## Model Evaluation Results

### Performance Metrics
{}

### Best Performing Model
The {} model showed the best performance with:
- RMSE: {:.2f}
- MAPE: {:.2f}%

## Model Comparisons
1. Holt-Winters Exponential Smoothing
   - Strengths: Handles both trend and seasonality
   - Best for: Short to medium-term forecasting
   - Performance: RMSE = {:.2f}, MAPE = {:.2f}%

2. ARIMA
   - Strengths: Captures complex time series patterns
   - Best for: Stationary time series data
   - Performance: RMSE = {:.2f}, MAPE = {:.2f}%

3. Facebook Prophet
   - Strengths: Handles holidays and special events
   - Best for: Business forecasting with multiple seasonalities
   - Performance: RMSE = {:.2f}, MAPE = {:.2f}%

4. LSTM Neural Network
   - Strengths: Captures complex non-linear patterns
   - Best for: Large datasets with long-term dependencies
   - Performance: RMSE = {:.2f}, MAPE = {:.2f}%

## Recommendations
1. Primary Model Selection:
   - Use {} for production forecasting
   - Regular retraining schedule: Monthly
   - Monitor accuracy metrics for potential drift

2. Backup Models:
   - Keep {} as a backup model
   - Use ensemble approach for critical periods

3. Model Usage Guidelines:
   - Short-term forecasts (1-7 days): High confidence
   - Medium-term forecasts (8-30 days): Moderate confidence
   - Long-term forecasts (31+ days): Use with caution

## Visualizations
1. sales_forecasts_comparison.png - Comparison of different model forecasts
2. forecast_model_comparison.png - Performance metrics comparison

## Next Steps
1. Implement the {} model in production
2. Set up automated retraining pipeline
3. Create monitoring dashboard for forecast accuracy
4. Develop ensemble approach for peak seasons
""".format(
    pd.DataFrame(evaluation_results).to_string(),
    best_model,
    evaluation_results[best_model]['rmse'],
    evaluation_results[best_model]['mape'] * 100,
    evaluation_results['Holt-Winters']['rmse'],
    evaluation_results['Holt-Winters']['mape'] * 100,
    evaluation_results['ARIMA']['rmse'],
    evaluation_results['ARIMA']['mape'] * 100,
    evaluation_results['Prophet']['rmse'],
    evaluation_results['Prophet']['mape'] * 100,
    evaluation_results['LSTM']['rmse'],
    evaluation_results['LSTM']['mape'] * 100,
    best_model,
    sorted(evaluation_results.items(), key=lambda x: x[1]['rmse'])[1][0],
    best_model
)
    
    with open('sales_forecasting_report.md', 'w') as f:
        f.write(report_content)

def main():
    """
    Main function to run the sales forecasting analysis
    """
    try:
        # Load processed data
        daily_sales = load_processed_data()
        
        # Prepare data for different models
        data = prepare_data_for_models(daily_sales)
        
        # Train models
        models = {
            'holt_winters': train_holt_winters(data['original'][0]),
            'arima': train_arima(data['original'][0]),
            'prophet': train_prophet(data['prophet'][0]),
            'lstm': train_lstm(data['lstm'][0], data['lstm'][1])
        }
        
        # Evaluate models
        evaluation_results = evaluate_models(models, data)
        
        # Generate forecasts
        forecasts = generate_forecasts(models, data)
        
        # Create visualizations
        create_forecast_visualizations(daily_sales, forecasts, evaluation_results)
        
        # Determine best model
        best_model = min(evaluation_results.items(), key=lambda x: x[1]['rmse'])[0]
        
        # Generate report
        generate_forecast_report(evaluation_results, best_model)
        
        print("Sales forecasting analysis completed successfully!")
        
    except Exception as e:
        print(f"Error occurred during sales forecasting: {str(e)}")

if __name__ == "__main__":
    main() 