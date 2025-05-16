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
import logging
from typing import Dict, Tuple, Optional, Union
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for visualizations
plt.style.use('default')
sns.set_theme()

def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate input data for forecasting
    """
    try:
        # Check if dataframe is empty
        if df.empty:
            logger.error("Input data is empty")
            return False
        
        # Check for minimum data points (2 weeks)
        if len(df) < 14:
            logger.error("Insufficient data points for forecasting (minimum 14 required)")
            return False
        
        # Check for missing values
        if df['amount'].isnull().any():
            logger.warning("Missing values detected in sales data")
            return False
        
        # Check for negative values
        if (df['amount'] < 0).any():
            logger.error("Negative sales values detected")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        return False

def load_processed_data(file_path: str = 'daily_sales_processed.csv') -> Optional[pd.DataFrame]:
    """
    Load and validate the processed time series data
    """
    try:
        logger.info("Loading processed time series data...")
        daily_sales = pd.read_csv(file_path)
        daily_sales.index = pd.to_datetime(daily_sales.iloc[:, 0])
        daily_sales = daily_sales[['amount']]
        
        if validate_data(daily_sales):
            return daily_sales
        return None
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None

def determine_optimal_parameters(data: pd.DataFrame) -> Tuple[tuple, tuple]:
    """
    Determine optimal SARIMA parameters based on data characteristics
    """
    try:
        # Calculate basic statistics
        n_samples = len(data)
        
        # Determine seasonality
        if n_samples >= 365:
            seasonal_period = 12  # Monthly seasonality for yearly data
        else:
            seasonal_period = 7   # Weekly seasonality for shorter periods
        
        # Start with conservative parameters
        order = (1, 1, 1)
        seasonal_order = (1, 1, 1, seasonal_period)
        
        logger.info(f"Selected model parameters: order={order}, seasonal_order={seasonal_order}")
        return order, seasonal_order
        
    except Exception as e:
        logger.error(f"Error determining parameters: {str(e)}")
        return (1, 1, 1), (1, 1, 1, 7)  # Default fallback

def train_sarima_model(data: pd.DataFrame) -> Optional[SARIMAX]:
    """
    Train a SARIMA model on the provided time series data
    """
    try:
        logger.info("Training SARIMA model...")
        
        # Determine optimal parameters
        order, seasonal_order = determine_optimal_parameters(data)
        
        # Train model
        model = SARIMAX(
            data['amount'],
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        results = model.fit()
        return results
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return None

def make_future_predictions(
    model: Union[SARIMAX, SARIMAXResults],
    last_date: datetime,
    periods: int = 180
) -> Optional[pd.DataFrame]:
    """
    Generate sales predictions for future dates
    """
    try:
        logger.info(f"Generating predictions for next {periods} days...")
        
        # Validate input parameters
        if periods <= 0:
            logger.error("Invalid forecast period")
            return None
        
        if not isinstance(model, (SARIMAX, SARIMAXResults)):
            logger.error("Invalid model type")
            return None
        
        # Generate forecast
        forecast = model.get_forecast(steps=periods)
        
        # Get confidence intervals
        forecast_mean = forecast.predicted_mean
        conf_int = forecast.conf_int()
        
        # Create future dates
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_sales': forecast_mean,
            'lower_ci': conf_int.iloc[:, 0],
            'upper_ci': conf_int.iloc[:, 1]
        })
        
        forecast_df.set_index('date', inplace=True)
        
        # Save forecast data for export
        forecast_df.to_csv('forecast_data.csv')
        logger.info("Forecast data saved to forecast_data.csv")
        
        return forecast_df
        
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return None

def evaluate_forecast(
    actual: pd.Series,
    predicted: pd.Series
) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics
    """
    try:
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mape = mean_absolute_percentage_error(actual, predicted) * 100
        
        metrics = {
            'RMSE': rmse,
            'MAPE': mape
        }
        
        logger.info(f"Forecast metrics: RMSE={rmse:.2f}, MAPE={mape:.2f}%")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        return {'RMSE': float('nan'), 'MAPE': float('nan')}

def visualize_forecast(historical_data: pd.DataFrame, forecast_data: pd.DataFrame) -> None:
    """
    Create visualizations for historical and forecasted sales
    """
    logger.info("Creating forecast visualizations...")
    
    try:
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
        
        logger.info("Forecast visualizations created successfully")
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {str(e)}")

def generate_forecast_report(historical_data: pd.DataFrame, forecast_data: pd.DataFrame, metrics: Dict[str, float]) -> None:
    """
    Generate a detailed forecast report with insights and recommendations
    """
    logger.info("Generating forecast report...")
    
    try:
        # Calculate key metrics
        avg_historical = historical_data['amount'].mean()
        avg_forecast = forecast_data['predicted_sales'].mean()
        growth_rate = ((avg_forecast - avg_historical) / avg_historical) * 100
        
        peak_forecast_date = forecast_data['predicted_sales'].idxmax()
        peak_forecast_value = forecast_data['predicted_sales'].max()
        
        report_content = f"""# Sales Forecast Analysis Report

## Forecast Overview
- Forecast Period: {forecast_data.index.min().strftime('%Y-%m-%d')} to {forecast_data.index.max().strftime('%Y-%m-%d')}
- Number of Days Forecasted: {len(forecast_data)}
- Average Historical Daily Sales: ₹{avg_historical:,.2f}
- Average Forecasted Daily Sales: ₹{avg_forecast:,.2f}
- Expected Growth Rate: {growth_rate:.1f}%

## Forecast Accuracy Metrics
- Root Mean Square Error (RMSE): ₹{metrics['RMSE']:,.2f}
- Mean Absolute Percentage Error (MAPE): {metrics['MAPE']:.1f}%

## Key Insights
1. Peak Sales Forecast:
   - Date: {peak_forecast_date.strftime('%Y-%m-%d')}
   - Expected Sales: ₹{peak_forecast_value:,.2f}

2. Growth Trends:
{"- Positive growth trend observed" if growth_rate > 0 else "- Declining trend observed"}

3. Seasonal Patterns:
- Weekly patterns show strongest sales on {str(forecast_data.groupby(forecast_data.index.dayofweek)['predicted_sales'].mean().idxmax())}

## Business Recommendations

1. Inventory Management:
- Maintain higher stock levels during peak sales periods
- Optimize inventory for predicted demand patterns

2. Marketing and Promotions:
- Plan promotional activities around forecasted slow periods
- Capitalize on expected peak sales periods

3. Resource Planning:
- Adjust staffing levels based on predicted sales volumes
- Plan system maintenance during forecasted low-traffic periods

## Next Steps
1. Monitor actual sales against predictions and adjust forecasts as needed
2. Update the model with new data periodically
3. Fine-tune forecasting parameters based on accuracy metrics
4. Develop contingency plans for significant deviations from forecast

Note: This forecast should be used as a guide and combined with business expertise and market knowledge for decision-making.
"""
        
        with open('sales_forecast_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.info("Forecast report generated successfully")
            
    except Exception as e:
        logger.error(f"Error generating forecast report: {str(e)}")

def main():
    """
    Main function to run sales forecasting analysis
    """
    try:
        # Load and validate data
        historical_data = load_processed_data()
        if historical_data is None:
            logger.error("Failed to load valid data")
            return
            
        if len(historical_data) < 30:
            logger.error("Insufficient historical data for reliable forecasting (minimum 30 days required)")
            return
        
        # Train model
        model = train_sarima_model(historical_data)
        if model is None:
            logger.error("Failed to train model")
            return
        
        # Generate predictions
        forecast_data = make_future_predictions(model, historical_data.index[-1])
        if forecast_data is None:
            logger.error("Failed to generate predictions")
            return
        
        # Calculate accuracy using last 30 days
        test_period = min(30, len(historical_data) // 3)
        if test_period < 7:
            logger.warning("Test period is less than 7 days, forecast accuracy metrics may be unreliable")
            
        train_data = historical_data[:-test_period]
        test_data = historical_data[-test_period:]
        
        # Train model on training data
        test_model = train_sarima_model(train_data)
        if test_model is None:
            logger.error("Failed to train test model")
            return
        
        try:
            test_predictions = test_model.get_forecast(steps=test_period).predicted_mean
            metrics = evaluate_forecast(test_data['amount'], test_predictions)
            
            if metrics['MAPE'] > 50:
                logger.warning(f"High forecast error (MAPE={metrics['MAPE']:.1f}%), predictions may be unreliable")
                
        except Exception as e:
            logger.error(f"Error calculating forecast metrics: {str(e)}")
            metrics = {'RMSE': float('nan'), 'MAPE': float('nan')}
        
        # Create visualizations and report
        try:
            visualize_forecast(historical_data, forecast_data)
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            
        try:
            generate_forecast_report(historical_data, forecast_data, metrics)
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
        
        logger.info("Sales forecasting analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise  # Re-raise the exception for proper error handling

if __name__ == "__main__":
    main() 