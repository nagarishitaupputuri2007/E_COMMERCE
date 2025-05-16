import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Optional
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BusinessVisualizer:
    def __init__(self, sales_data: pd.DataFrame, forecast_data: pd.DataFrame):
        """
        Initialize the visualizer with sales and forecast data
        """
        self.sales_data = sales_data.copy()
        self.forecast_data = forecast_data.copy()
        
        # Ensure date columns are datetime
        if 'date' not in self.sales_data.columns:
            self.sales_data['date'] = pd.to_datetime(self.sales_data.iloc[:, 0])
        else:
            self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
            
        if 'date' not in self.forecast_data.columns:
            self.forecast_data['date'] = pd.to_datetime(self.forecast_data.iloc[:, 0])
        else:
            self.forecast_data['date'] = pd.to_datetime(self.forecast_data['date'])
        
        # Set style
        plt.style.use('default')
        sns.set_style("whitegrid")
        
    def create_category_growth_chart(self) -> None:
        """
        Create visualization for category growth trends
        """
        try:
            # Calculate category growth
            category_growth = self.sales_data.pivot_table(
                index='category',
                columns=pd.Grouper(key='date', freq='M'),
                values='amount',
                aggfunc='sum'
            ).pct_change(axis=1).mean(axis=1)
            
            # Create bar chart
            plt.figure(figsize=(12, 6))
            category_growth.sort_values().plot(kind='barh')
            plt.title('Category Growth Rates')
            plt.xlabel('Growth Rate (%)')
            plt.ylabel('Category')
            plt.tight_layout()
            plt.savefig('category_growth.png')
            plt.close()
            
            logger.info("Category growth chart created successfully")
            
        except Exception as e:
            logger.error(f"Error creating category growth chart: {str(e)}")
    
    def create_regional_performance_map(self) -> None:
        """
        Create visualization for regional performance
        """
        try:
            # Calculate regional metrics
            regional_metrics = self.sales_data.groupby('region').agg({
                'amount': 'sum',
                'customer_id': 'nunique'
            }).reset_index()
            
            # Create bar chart instead of map
            plt.figure(figsize=(12, 6))
            plt.bar(regional_metrics['region'], regional_metrics['amount'])
            plt.title('Regional Sales Performance')
            plt.xlabel('Region')
            plt.ylabel('Total Sales Amount')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('regional_performance.png')
            plt.close()
            
            logger.info("Regional performance visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating regional performance visualization: {str(e)}")
    
    def create_customer_segment_analysis(self) -> None:
        """
        Create visualizations for customer segment analysis
        """
        try:
            # Calculate RFM metrics
            now = self.sales_data['date'].max()
            
            rfm = self.sales_data.groupby('customer_id').agg({
                'date': lambda x: (now - x.max()).days,
                'order_id': 'count',
                'amount': 'sum'
            })
            
            rfm.columns = ['recency', 'frequency', 'monetary']
            
            # Create segments
            rfm['segment'] = 'Standard'
            rfm.loc[rfm['monetary'] > rfm['monetary'].quantile(0.75), 'segment'] = 'High Value'
            rfm.loc[rfm['frequency'] > rfm['frequency'].quantile(0.75), 'segment'] = 'Loyal'
            rfm.loc[rfm['recency'] > rfm['recency'].quantile(0.75), 'segment'] = 'At Risk'
            
            # Create segment distribution plot
            plt.figure(figsize=(10, 6))
            segment_dist = rfm['segment'].value_counts()
            plt.pie(segment_dist, labels=segment_dist.index, autopct='%1.1f%%')
            plt.title('Customer Segment Distribution')
            plt.axis('equal')
            plt.savefig('customer_segments.png')
            plt.close()
            
            logger.info("Customer segment analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating customer segment analysis: {str(e)}")
    
    def create_sales_trend_analysis(self) -> None:
        """
        Create sales trend analysis visualization
        """
        try:
            # Create figure with secondary y-axis
            fig, ax1 = plt.subplots(figsize=(15, 8))
            
            # Plot historical sales
            ax1.plot(self.sales_data['date'], self.sales_data['amount'],
                    color='blue', label='Historical Sales')
            
            # Plot forecast
            ax1.plot(self.forecast_data['date'], self.forecast_data['predicted_sales'],
                    color='red', linestyle='--', label='Forecast')
            
            # Add confidence intervals
            ax1.fill_between(self.forecast_data['date'],
                           self.forecast_data['lower_ci'],
                           self.forecast_data['upper_ci'],
                           color='red', alpha=0.2, label='95% CI')
            
            # Customize plot
            plt.title('Sales Trend Analysis and Forecast')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Sales Amount')
            plt.legend()
            
            # Rotate x-axis labels
            plt.xticks(rotation=45)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save plot
            plt.savefig('sales_trend.png')
            plt.close()
            
            logger.info("Sales trend analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating sales trend analysis: {str(e)}")
    
    def create_all_visualizations(self) -> None:
        """
        Create all business opportunity visualizations
        """
        try:
            self.create_category_growth_chart()
            self.create_regional_performance_map()
            self.create_customer_segment_analysis()
            self.create_sales_trend_analysis()
            
            logger.info("All visualizations created successfully!")
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")

def main():
    """
    Main function to create business visualizations
    """
    try:
        # Check if data files exist, if not create sample data
        if not os.path.exists('daily_sales_processed.csv'):
            # Create sample sales data
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            np.random.seed(42)
            
            sales_data = pd.DataFrame({
                'date': dates.strftime('%Y-%m-%d'),
                'amount': np.random.normal(1000, 200, len(dates)),
                'category': np.random.choice(['Electronics', 'Fashion', 'Home & Living'], len(dates)),
                'region': np.random.choice(['South', 'North', 'West', 'East'], len(dates)),
                'customer_id': np.random.randint(1, 100, len(dates)),
                'product_id': np.random.randint(1, 50, len(dates)),
                'order_id': [f'ORD-{i:05d}' for i in range(len(dates))]
            })
            
            sales_data.to_csv('daily_sales_processed.csv', index=False)
            logger.info("Created sample sales data")
        
        if not os.path.exists('forecast_data.csv'):
            # Create sample forecast data
            future_dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D')
            
            forecast_data = pd.DataFrame({
                'date': future_dates.strftime('%Y-%m-%d'),
                'predicted_sales': np.random.normal(1200, 250, len(future_dates)),
                'lower_ci': np.random.normal(900, 200, len(future_dates)),
                'upper_ci': np.random.normal(1500, 200, len(future_dates))
            })
            
            forecast_data.to_csv('forecast_data.csv', index=False)
            logger.info("Created sample forecast data")
        
        # Load data
        sales_data = pd.read_csv('daily_sales_processed.csv')
        forecast_data = pd.read_csv('forecast_data.csv')
        
        # Create visualizer
        visualizer = BusinessVisualizer(sales_data, forecast_data)
        
        # Generate all visualizations
        visualizer.create_all_visualizations()
        
        logger.info("Business visualization process completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 