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
from statsmodels.tsa.statespace.sarimax import SARIMAX
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def train_sarima_model(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    """
    Train a SARIMA model on the provided time series data
    """
    print("Training SARIMA model...")
    
    model = SARIMAX(data['amount'],
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False)
    
    results = model.fit()
    return results

def generate_future_dates(last_date, periods):
    """
    Generate future dates for forecasting
    """
    date_list = []
    current_date = last_date
    
    for _ in range(periods):
        current_date += timedelta(days=1)
        date_list.append(current_date)
    
    return pd.DatetimeIndex(date_list)

def make_future_predictions(model, last_date, periods=180):
    """
    Generate sales predictions for future dates
    """
    print(f"Generating predictions for next {periods} days...")
    
    # Generate forecast
    forecast = model.get_forecast(steps=periods)
    
    # Get confidence intervals
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()
    
    # Create future dates
    future_dates = generate_future_dates(last_date, periods)
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'predicted_sales': forecast_mean,
        'lower_ci': conf_int.iloc[:, 0],
        'upper_ci': conf_int.iloc[:, 1]
    })
    
    forecast_df.set_index('date', inplace=True)
    return forecast_df

def evaluate_forecast(actual, predicted):
    """
    Calculate forecast accuracy metrics
    """
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = mean_absolute_percentage_error(actual, predicted) * 100
    
    return {
        'RMSE': rmse,
        'MAPE': mape
    }

def visualize_forecast(historical_data, forecast_data):
    """
    Create visualizations for historical and forecasted sales
    """
    print("Creating forecast visualizations...")
    
    # Create interactive plot using plotly
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Sales Forecast with Confidence Intervals',
                                      'Historical vs Forecasted Sales Pattern'))
    
    # Plot 1: Historical + Forecast with CI
    fig.add_trace(
        go.Scatter(x=historical_data.index, y=historical_data['amount'],
                  name='Historical Sales',
                  line=dict(color='blue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=forecast_data.index, y=forecast_data['predicted_sales'],
                  name='Forecasted Sales',
                  line=dict(color='red', dash='dash')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=forecast_data.index, y=forecast_data['upper_ci'],
                  fill=None,
                  line=dict(color='rgba(255,0,0,0.2)'),
                  name='Upper CI'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=forecast_data.index, y=forecast_data['lower_ci'],
                  fill='tonexty',
                  line=dict(color='rgba(255,0,0,0.2)'),
                  name='Lower CI'),
        row=1, col=1
    )
    
    # Plot 2: Sales Pattern Comparison
    historical_pattern = historical_data.groupby(historical_data.index.dayofweek)['amount'].mean()
    forecast_pattern = forecast_data.groupby(forecast_data.index.dayofweek)['predicted_sales'].mean()
    
    fig.add_trace(
        go.Scatter(x=list(range(7)), y=historical_pattern,
                  name='Historical Pattern',
                  line=dict(color='blue')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=list(range(7)), y=forecast_pattern,
                  name='Forecasted Pattern',
                  line=dict(color='red', dash='dash')),
        row=2, col=1
    )
    
    fig.update_layout(height=800, title_text="Sales Forecast Analysis")
    fig.write_html('sales_forecast_analysis.html')

def generate_forecast_report(historical_data, forecast_data, metrics):
    """
    Generate a detailed forecast report with insights and recommendations
    """
    print("Generating forecast report...")
    
    # Calculate key metrics
    avg_historical = historical_data['amount'].mean()
    avg_forecast = forecast_data['predicted_sales'].mean()
    growth_rate = ((avg_forecast - avg_historical) / avg_historical) * 100
    
    peak_forecast_date = forecast_data['predicted_sales'].idxmax()
    peak_forecast_value = forecast_data['predicted_sales'].max()
    
    report_content = """# Sales Forecast Analysis Report

## Forecast Overview
- Forecast Period: {} to {}
- Number of Days Forecasted: {}
- Average Historical Daily Sales: ₹{:,.2f}
- Average Forecasted Daily Sales: ₹{:,.2f}
- Expected Growth Rate: {:.1f}%

## Forecast Accuracy Metrics
- Root Mean Square Error (RMSE): ₹{:,.2f}
- Mean Absolute Percentage Error (MAPE): {:.1f}%

## Key Insights
1. Peak Sales Forecast:
   - Date: {}
   - Expected Sales: ₹{:,.2f}

2. Growth Trends:
{}

3. Seasonal Patterns:
{}

## Business Recommendations

1. Inventory Management:
{}

2. Marketing and Promotions:
{}

3. Resource Planning:
{}

## Next Steps
1. Monitor actual sales against predictions and adjust forecasts as needed
2. Update the model with new data periodically
3. Fine-tune forecasting parameters based on accuracy metrics
4. Develop contingency plans for significant deviations from forecast

Note: This forecast should be used as a guide and combined with business expertise and market knowledge for decision-making.
""".format(
    forecast_data.index.min().strftime('%Y-%m-%d'),
    forecast_data.index.max().strftime('%Y-%m-%d'),
    len(forecast_data),
    avg_historical,
    avg_forecast,
    growth_rate,
    metrics['RMSE'],
    metrics['MAPE'],
    peak_forecast_date.strftime('%Y-%m-%d'),
    peak_forecast_value,
    "- Positive growth trend observed" if growth_rate > 0 else "- Declining trend observed",
    "- Weekly patterns show strongest sales on " + str(forecast_data.groupby(forecast_data.index.dayofweek)['predicted_sales'].mean().idxmax()),
    "- Maintain higher stock levels during peak sales periods\n- Optimize inventory for predicted demand patterns",
    "- Plan promotional activities around forecasted slow periods\n- Capitalize on expected peak sales periods",
    "- Adjust staffing levels based on predicted sales volumes\n- Plan system maintenance during forecasted low-traffic periods"
)
    
    with open('sales_forecast_report.md', 'w') as f:
        f.write(report_content)

def main():
    """
    Main function to run sales forecasting analysis
    """
    try:
        # Load historical data
        historical_data = pd.read_csv('daily_sales_processed.csv', index_col='order_date', parse_dates=True)
        
        # Train SARIMA model
        model = train_sarima_model(historical_data)
        
        # Generate future predictions
        forecast_data = make_future_predictions(model, historical_data.index[-1])
        
        # Calculate forecast accuracy using last 30 days of historical data
        test_period = 30
        train_data = historical_data[:-test_period]
        test_data = historical_data[-test_period:]
        
        # Train model on training data
        test_model = train_sarima_model(train_data)
        test_predictions = test_model.get_forecast(steps=test_period).predicted_mean
        
        # Calculate accuracy metrics
        metrics = evaluate_forecast(test_data['amount'], test_predictions)
        
        # Create visualizations
        visualize_forecast(historical_data, forecast_data)
        
        # Generate forecast report
        generate_forecast_report(historical_data, forecast_data, metrics)
        
        print("Sales forecasting analysis completed successfully!")
        
    except Exception as e:
        print(f"Error occurred during sales forecasting: {str(e)}")

if __name__ == "__main__":
    main() 