import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_and_explore_data(file_path):
    """
    Load and perform initial exploration of the e-commerce dataset
    """
    print("Loading dataset...")
    # Load the dataset
    df = pd.read_csv(file_path)
    
    print("\n1. Basic Dataset Information:")
    print("-" * 50)
    print(f"Number of rows: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")
    
    print("\n2. First few rows of the dataset:")
    print("-" * 50)
    print(df.head())
    
    print("\n3. Column Information:")
    print("-" * 50)
    print(df.info())
    
    print("\n4. Missing Values Analysis:")
    print("-" * 50)
    missing_values = df.isnull().sum()
    print(missing_values[missing_values > 0])
    
    print("\n5. Duplicate Records:")
    print("-" * 50)
    duplicates = df.duplicated().sum()
    print(f"Number of duplicate records: {duplicates}")
    
    print("\n6. Basic Statistics:")
    print("-" * 50)
    print(df.describe())
    
    return df

def analyze_sales_trends(df):
    """
    Analyze sales trends and patterns
    """
    print("\n7. Sales Analysis:")
    print("-" * 50)
    
    # Assuming we have 'order_date' and 'amount' columns
    if 'order_date' in df.columns and 'amount' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
        daily_sales = df.groupby('order_date')['amount'].sum()
        
        print("Daily Sales Statistics:")
        print(daily_sales.describe())
        
        # Plot daily sales trend
        plt.figure(figsize=(12, 6))
        daily_sales.plot()
        plt.title('Daily Sales Trend')
        plt.xlabel('Date')
        plt.ylabel('Sales Amount')
        plt.savefig('daily_sales_trend.png')
        plt.close()

def analyze_customer_behavior(df):
    """
    Analyze customer behavior and segments
    """
    print("\n8. Customer Analysis:")
    print("-" * 50)
    
    # Assuming we have 'customer_id' and 'amount' columns
    if 'customer_id' in df.columns and 'amount' in df.columns:
        customer_stats = df.groupby('customer_id').agg({
            'amount': ['count', 'sum', 'mean'],
            'order_id': 'nunique'
        })
        
        print("Customer Purchase Statistics:")
        print(customer_stats.describe())

def analyze_product_performance(df):
    """
    Analyze product performance and categories
    """
    print("\n9. Product Analysis:")
    print("-" * 50)
    
    # Assuming we have 'product_id' and 'amount' columns
    if 'product_id' in df.columns and 'amount' in df.columns:
        product_stats = df.groupby('product_id').agg({
            'amount': ['count', 'sum', 'mean'],
            'quantity': 'sum'
        })
        
        print("Top 10 Products by Sales:")
        print(product_stats.sort_values(('amount', 'sum'), ascending=False).head(10))

def main():
    """
    Main function to run the analysis
    """
    # Replace with your dataset path
    file_path = 'ecommerce_data.csv'
    
    try:
        # Load and explore data
        df = load_and_explore_data(file_path)
        
        # Perform various analyses
        analyze_sales_trends(df)
        analyze_customer_behavior(df)
        analyze_product_performance(df)
        
        print("\nAnalysis completed successfully!")
        
    except FileNotFoundError:
        print(f"Error: Dataset file not found at {file_path}")
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 