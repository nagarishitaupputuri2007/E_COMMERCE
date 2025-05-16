import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import plotly.express as px
import plotly.graph_objects as go
import calendar

# Set style for visualizations
plt.style.use('default')
sns.set_theme()

def load_processed_data():
    """
    Load the processed time series data
    """
    print("Loading processed time series data...")
    daily_sales = pd.read_csv('daily_sales_processed.csv')
    daily_sales.index = pd.to_datetime(daily_sales.iloc[:, 0])
    daily_sales = daily_sales[['amount']]
    return daily_sales

def prepare_data_for_prophet(daily_sales):
    """
    Prepare data for Prophet model
    """
    print("Preparing data for Prophet model...")
    
    # Create Prophet dataframe
    prophet_data = pd.DataFrame({
        'ds': daily_sales.index,
        'y': daily_sales['amount']
    })
    
    # Add Indian holiday events
    holidays = pd.DataFrame({
        'holiday': [
            'Diwali', 'Dussehra', 'Republic Day', 'Independence Day',
            'Christmas', 'New Year', 'Holi', 'Eid'
        ],
        'ds': [
            '2024-11-01', '2024-10-12', '2024-01-26', '2024-08-15',
            '2024-12-25', '2024-01-01', '2024-03-25', '2024-04-11'
        ],
        'lower_window': [-2] * 8,  # Days before event
        'upper_window': [2] * 8    # Days after event
    })
    
    return prophet_data, holidays

def train_prophet_model(prophet_data, holidays, forecast_periods=365):
    """
    Train Prophet model and generate predictions
    """
    print("Training Prophet model and generating predictions...")
    
    # Initialize and train Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=holidays,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05
    )
    
    model.fit(prophet_data)
    
    # Create future dates dataframe
    future_dates = model.make_future_dataframe(periods=forecast_periods)
    
    # Generate predictions
    forecast = model.predict(future_dates)
    
    return model, forecast

def analyze_seasonal_patterns(model, forecast):
    """
    Analyze seasonal patterns in the predictions
    """
    print("Analyzing seasonal patterns...")
    
    # Plot yearly seasonality
    yearly_seasonality = plt.figure(figsize=(12, 6))
    model.plot_components(forecast)
    plt.tight_layout()
    plt.savefig('seasonal_patterns.png')
    plt.close()
    
    # Create monthly pattern analysis
    monthly_pattern = forecast.groupby(forecast['ds'].dt.month).agg({
        'yhat': 'mean',
        'yhat_lower': 'mean',
        'yhat_upper': 'mean'
    }).reset_index()
    
    monthly_pattern['month_name'] = monthly_pattern['ds'].apply(lambda x: calendar.month_name[x])
    
    return monthly_pattern

def create_prediction_visualizations(daily_sales, forecast, monthly_pattern):
    """
    Create visualizations for sales predictions
    """
    print("Creating prediction visualizations...")
    
    # Historical vs Predicted Sales
    plt.figure(figsize=(15, 8))
    plt.plot(daily_sales.index, daily_sales['amount'], label='Historical Sales', alpha=0.7)
    plt.plot(forecast['ds'], forecast['yhat'], label='Predicted Sales', alpha=0.7)
    plt.fill_between(
        forecast['ds'],
        forecast['yhat_lower'],
        forecast['yhat_upper'],
        alpha=0.3,
        label='Prediction Interval'
    )
    plt.title('Historical vs Predicted Sales')
    plt.xlabel('Date')
    plt.ylabel('Sales Amount')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('sales_prediction.png')
    plt.close()
    
    # Monthly Sales Pattern
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_pattern['month_name'], monthly_pattern['yhat'], marker='o')
    plt.fill_between(
        monthly_pattern['month_name'],
        monthly_pattern['yhat_lower'],
        monthly_pattern['yhat_upper'],
        alpha=0.3
    )
    plt.title('Monthly Sales Pattern')
    plt.xlabel('Month')
    plt.ylabel('Average Sales Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly_sales_pattern.png')
    plt.close()
    
    # Interactive Forecast Plot
    fig = go.Figure()
    
    # Historical Data
    fig.add_trace(go.Scatter(
        x=daily_sales.index,
        y=daily_sales['amount'],
        name='Historical Sales',
        mode='lines'
    ))
    
    # Predicted Data
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        name='Predicted Sales',
        mode='lines'
    ))
    
    # Prediction Interval
    fig.add_trace(go.Scatter(
        x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
        y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Prediction Interval'
    ))
    
    fig.update_layout(
        title='Interactive Sales Forecast',
        xaxis_title='Date',
        yaxis_title='Sales Amount',
        hovermode='x'
    )
    
    fig.write_html('interactive_forecast.html')

def calculate_growth_metrics(forecast):
    """
    Calculate growth metrics from the forecast
    """
    print("Calculating growth metrics...")
    
    # Split forecast into current and future periods
    current_period = forecast[forecast['ds'] <= datetime.now()]
    future_period = forecast[forecast['ds'] > datetime.now()]
    
    # Calculate metrics
    avg_current_sales = current_period['yhat'].mean() if not current_period.empty else 0
    avg_future_sales = future_period['yhat'].mean() if not future_period.empty else 0
    growth_rate = ((avg_future_sales - avg_current_sales) / avg_current_sales * 100) if avg_current_sales > 0 else 0
    
    # Find peak and low sales dates
    if not future_period.empty:
        peak_sales_date = future_period.loc[future_period['yhat'].idxmax(), 'ds']
        low_sales_date = future_period.loc[future_period['yhat'].idxmin(), 'ds']
    else:
        peak_sales_date = datetime.now()
        low_sales_date = datetime.now()
    
    return {
        'growth_rate': growth_rate,
        'peak_sales_date': peak_sales_date,
        'low_sales_date': low_sales_date,
        'avg_future_sales': avg_future_sales
    }

def generate_prediction_report(forecast, growth_metrics, monthly_pattern):
    """
    Generate a comprehensive prediction report
    """
    print("Generating prediction report...")
    
    report_content = """# Sales Prediction Analysis Report

## Executive Summary
Based on our analysis of historical sales data and future predictions, we forecast a {:.1f}% {} in average sales over the next 12 months.

## Key Predictions

### Growth Metrics
- Average Predicted Daily Sales: Rs. {:,.2f}
- Expected Growth Rate: {:.1f}%
- Peak Sales Period: {}
- Lowest Sales Period: {}

### Monthly Sales Patterns
{}

## Business Implications

### Inventory Planning
1. Peak Season Preparation ({}):
   - Increase inventory levels by 25-30%
   - Ensure adequate storage capacity
   - Plan for additional logistics support

2. Low Season Management ({}):
   - Maintain minimal inventory levels
   - Focus on clearing slow-moving stock
   - Plan maintenance activities

### Marketing Recommendations
1. High Sales Periods:
   - Increase marketing budget for peak months
   - Focus on customer retention and loyalty programs
   - Implement premium pricing strategies

2. Low Sales Periods:
   - Launch promotional campaigns
   - Offer special discounts
   - Focus on customer acquisition

### Operational Considerations
1. Staffing:
   - Increase temporary staff during peak months
   - Optimize workforce during slower periods
   - Plan training during low seasons

2. Website/App Performance:
   - Ensure platform can handle peak traffic
   - Schedule maintenance during low periods
   - Monitor performance metrics closely

## Forecast Accuracy
- The model accounts for:
  - Yearly seasonality
  - Weekly patterns
  - Holiday effects
  - Special events

## Visualizations
1. sales_prediction.png - Historical vs Predicted Sales
2. monthly_sales_pattern.png - Monthly Sales Patterns
3. seasonal_patterns.png - Seasonal Components
4. interactive_forecast.html - Interactive Forecast Visualization

## Risk Factors
1. Market Conditions:
   - Economic fluctuations
   - Competition
   - Consumer behavior changes

2. External Events:
   - Festival dates
   - Weather conditions
   - Supply chain disruptions

## Next Steps
1. Regular Monitoring:
   - Track actual vs predicted sales
   - Update forecasts monthly
   - Adjust strategies based on performance

2. Continuous Improvement:
   - Refine prediction models
   - Incorporate new data sources
   - Adjust for changing market conditions
""".format(
    abs(growth_metrics['growth_rate']),
    'increase' if growth_metrics['growth_rate'] > 0 else 'decrease',
    growth_metrics['avg_future_sales'],
    growth_metrics['growth_rate'],
    growth_metrics['peak_sales_date'].strftime('%B %Y'),
    growth_metrics['low_sales_date'].strftime('%B %Y'),
    monthly_pattern.to_string(),
    growth_metrics['peak_sales_date'].strftime('%B'),
    growth_metrics['low_sales_date'].strftime('%B')
)
    
    try:
        with open('sales_prediction_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
    except UnicodeEncodeError:
        with open('sales_prediction_report.md', 'w', encoding='ascii', errors='ignore') as f:
            f.write(report_content)

def main():
    """
    Main function to run the sales prediction analysis
    """
    try:
        # Load processed data
        daily_sales = load_processed_data()
        
        # Prepare data for Prophet
        prophet_data, holidays = prepare_data_for_prophet(daily_sales)
        
        # Train model and generate predictions
        model, forecast = train_prophet_model(prophet_data, holidays)
        
        # Analyze seasonal patterns
        monthly_pattern = analyze_seasonal_patterns(model, forecast)
        
        # Create visualizations
        create_prediction_visualizations(daily_sales, forecast, monthly_pattern)
        
        # Calculate growth metrics
        growth_metrics = calculate_growth_metrics(forecast)
        
        # Generate prediction report
        generate_prediction_report(forecast, growth_metrics, monthly_pattern)
        
        print("Sales prediction analysis completed successfully!")
        
    except Exception as e:
        print(f"Error occurred during sales prediction: {str(e)}")

if __name__ == "__main__":
    main() 