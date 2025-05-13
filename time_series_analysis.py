import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import plotly.express as px
import plotly.graph_objects as go

# Set style for visualizations
plt.style.use('seaborn')
sns.set_palette("husl")

def load_and_prepare_data(file_path):
    """
    Load and prepare time series data from the e-commerce dataset
    """
    print("Loading and preparing time series data...")
    
    # Load the dataset
    df = pd.read_csv(file_path)
    
    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Extract date components
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['week'] = df['order_date'].dt.isocalendar().week
    df['day'] = df['order_date'].dt.day
    df['day_of_week'] = df['order_date'].dt.dayofweek
    
    return df

def aggregate_sales_data(df):
    """
    Aggregate sales data at different time intervals
    """
    print("Aggregating sales data...")
    
    # Daily aggregation
    daily_sales = df.groupby('order_date')['amount'].sum().reset_index()
    daily_sales.set_index('order_date', inplace=True)
    
    # Weekly aggregation
    weekly_sales = df.groupby(['year', 'week'])['amount'].sum().reset_index()
    
    # Monthly aggregation
    monthly_sales = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    
    return daily_sales, weekly_sales, monthly_sales

def handle_missing_data(daily_sales):
    """
    Handle missing dates and fill gaps in the time series
    """
    print("Handling missing data...")
    
    # Create a complete date range
    date_range = pd.date_range(start=daily_sales.index.min(),
                             end=daily_sales.index.max(),
                             freq='D')
    
    # Reindex the daily sales with the complete date range
    complete_daily_sales = daily_sales.reindex(date_range)
    
    # Fill missing values with 0 or interpolate
    complete_daily_sales.fillna(0, inplace=True)
    
    return complete_daily_sales

def analyze_trends_seasonality(daily_sales):
    """
    Analyze trends and seasonality in the time series data
    """
    print("Analyzing trends and seasonality...")
    
    # Perform seasonal decomposition
    decomposition = seasonal_decompose(daily_sales['amount'], 
                                     period=7,  # Weekly seasonality
                                     model='additive')
    
    # Create visualization of decomposition
    plt.figure(figsize=(15, 12))
    
    plt.subplot(411)
    plt.plot(daily_sales.index, daily_sales['amount'])
    plt.title('Original Time Series')
    plt.xlabel('Date')
    plt.ylabel('Sales Amount')
    
    plt.subplot(412)
    plt.plot(daily_sales.index, decomposition.trend)
    plt.title('Trend')
    plt.xlabel('Date')
    plt.ylabel('Trend')
    
    plt.subplot(413)
    plt.plot(daily_sales.index, decomposition.seasonal)
    plt.title('Seasonal')
    plt.xlabel('Date')
    plt.ylabel('Seasonal')
    
    plt.subplot(414)
    plt.plot(daily_sales.index, decomposition.resid)
    plt.title('Residual')
    plt.xlabel('Date')
    plt.ylabel('Residual')
    
    plt.tight_layout()
    plt.savefig('sales_decomposition.png')
    plt.close()
    
    return decomposition

def create_visualizations(daily_sales, weekly_sales, monthly_sales):
    """
    Create visualizations for time series analysis
    """
    print("Creating visualizations...")
    
    # Daily sales trend
    plt.figure(figsize=(15, 6))
    plt.plot(daily_sales.index, daily_sales['amount'])
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Sales Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('daily_sales_trend_analysis.png')
    plt.close()
    
    # Weekly sales trend
    fig = px.line(weekly_sales, x='week', y='amount', color='year',
                  title='Weekly Sales Trend by Year')
    fig.write_html('weekly_sales_trend.html')
    
    # Monthly sales heatmap
    monthly_pivot = monthly_sales.pivot(index='year', columns='month', values='amount')
    plt.figure(figsize=(12, 6))
    sns.heatmap(monthly_pivot, annot=True, fmt='.0f', cmap='YlOrRd')
    plt.title('Monthly Sales Heatmap')
    plt.xlabel('Month')
    plt.ylabel('Year')
    plt.tight_layout()
    plt.savefig('monthly_sales_heatmap.png')
    plt.close()

def save_processed_data(daily_sales, weekly_sales, monthly_sales):
    """
    Save processed time series data
    """
    print("Saving processed data...")
    
    daily_sales.to_csv('daily_sales_processed.csv')
    weekly_sales.to_csv('weekly_sales_processed.csv')
    monthly_sales.to_csv('monthly_sales_processed.csv')

def generate_time_series_report(daily_sales, decomposition):
    """
    Generate a report summarizing the time series analysis
    """
    print("Generating time series analysis report...")
    
    report_content = """# Time Series Analysis Report

## Overview
This report presents the analysis of e-commerce sales data using time series techniques. The analysis includes trend identification, seasonality patterns, and key insights for business decision-making.

## Data Summary
- Analysis Period: {} to {}
- Total Days Analyzed: {}
- Total Sales: ₹{:,.2f}
- Average Daily Sales: ₹{:,.2f}
- Maximum Daily Sales: ₹{:,.2f}
- Minimum Daily Sales: ₹{:,.2f}

## Trend Analysis
The trend component of the time series shows the long-term progression of sales over time. Key observations:
- Overall trend direction: {}
- Peak sales period: {}
- Lowest sales period: {}

## Seasonality Analysis
The seasonal pattern in sales shows regular fluctuations that repeat over time:
- Weekly seasonality: Strongest on {}
- Monthly seasonality: Highest in {}

## Recommendations
Based on the time series analysis, here are key recommendations:
1. Inventory Planning:
   - Stock up before peak sales periods
   - Maintain lower inventory during identified slow periods

2. Marketing Strategy:
   - Focus promotional activities during historically strong sales periods
   - Plan special campaigns to boost sales during slower periods

3. Business Operations:
   - Adjust staffing levels based on identified peak and low periods
   - Plan system maintenance during historically slower periods

## Visualizations
The following visualizations have been generated for detailed analysis:
1. sales_decomposition.png - Breakdown of sales into trend, seasonal, and residual components
2. daily_sales_trend_analysis.png - Daily sales pattern visualization
3. weekly_sales_trend.html - Interactive weekly sales trend
4. monthly_sales_heatmap.png - Monthly sales patterns across years

## Next Steps
1. Implement forecasting models using this prepared time series data
2. Monitor actual sales against predicted patterns
3. Update analysis periodically to capture changing patterns
4. Use insights for inventory and marketing planning
""".format(
    daily_sales.index.min().strftime('%Y-%m-%d'),
    daily_sales.index.max().strftime('%Y-%m-%d'),
    len(daily_sales),
    daily_sales['amount'].sum(),
    daily_sales['amount'].mean(),
    daily_sales['amount'].max(),
    daily_sales['amount'].min(),
    "Increasing" if decomposition.trend[-1] > decomposition.trend[0] else "Decreasing",
    daily_sales['amount'].idxmax().strftime('%Y-%m-%d'),
    daily_sales['amount'].idxmin().strftime('%Y-%m-%d'),
    daily_sales.groupby(daily_sales.index.dayofweek)['amount'].mean().idxmax(),
    daily_sales.groupby(daily_sales.index.month)['amount'].mean().idxmax()
)
    
    with open('time_series_analysis_report.md', 'w') as f:
        f.write(report_content)

def main():
    """
    Main function to run the time series analysis
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data('ecommerce_data_cleaned.csv')
        
        # Aggregate sales data
        daily_sales, weekly_sales, monthly_sales = aggregate_sales_data(df)
        
        # Handle missing data
        complete_daily_sales = handle_missing_data(daily_sales)
        
        # Analyze trends and seasonality
        decomposition = analyze_trends_seasonality(complete_daily_sales)
        
        # Create visualizations
        create_visualizations(complete_daily_sales, weekly_sales, monthly_sales)
        
        # Save processed data
        save_processed_data(complete_daily_sales, weekly_sales, monthly_sales)
        
        # Generate analysis report
        generate_time_series_report(complete_daily_sales, decomposition)
        
        print("Time series analysis completed successfully!")
        
    except Exception as e:
        print(f"Error occurred during time series analysis: {str(e)}")

if __name__ == "__main__":
    main() 