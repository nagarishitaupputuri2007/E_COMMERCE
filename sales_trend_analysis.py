import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_data(file_path):
    """
    Load the cleaned dataset
    """
    return pd.read_csv(file_path, parse_dates=['order_date'])

def analyze_monthly_trends(df):
    """
    Analyze and visualize monthly sales trends
    """
    # Monthly sales aggregation
    monthly_sales = df.groupby(['year', 'month'])['total_revenue'].sum().reset_index()
    monthly_sales['month_year'] = monthly_sales.apply(
        lambda x: datetime(int(x['year']), int(x['month']), 1), axis=1
    )
    
    # Create monthly trend visualization
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_sales['month_year'], monthly_sales['total_revenue'], 
             marker='o', linewidth=2, markersize=8)
    plt.title('Monthly Sales Trend', fontsize=14)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly_sales_trend.png')
    plt.close()
    
    # Calculate monthly statistics
    monthly_stats = monthly_sales.agg({
        'total_revenue': ['mean', 'min', 'max', 'std']
    }).round(2)
    
    return monthly_sales, monthly_stats

def analyze_daily_distribution(df):
    """
    Analyze sales distribution by day of week
    """
    daily_sales = df.groupby('day_of_week')['total_revenue'].agg(['sum', 'count']).reset_index()
    daily_sales.columns = ['day_of_week', 'total_revenue', 'number_of_orders']
    
    # Create daily distribution visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(x='day_of_week', y='total_revenue', data=daily_sales)
    plt.title('Sales Distribution by Day of Week', fontsize=14)
    plt.xlabel('Day of Week', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('daily_sales_distribution.png')
    plt.close()
    
    return daily_sales

def analyze_category_trends(df):
    """
    Analyze sales trends by product category
    """
    category_sales = df.groupby('category').agg({
        'total_revenue': 'sum',
        'order_id': 'count',
        'quantity': 'sum'
    }).reset_index()
    
    category_sales.columns = ['category', 'total_revenue', 'number_of_orders', 'total_quantity']
    
    # Create category performance visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(x='category', y='total_revenue', data=category_sales)
    plt.title('Sales Performance by Category', fontsize=14)
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('category_sales_performance.png')
    plt.close()
    
    return category_sales

def generate_sales_report(monthly_sales, monthly_stats, daily_sales, category_sales):
    """
    Generate a comprehensive sales trend report
    """
    report = """
# E-Commerce Sales Trend Analysis Report

## 1. Monthly Sales Performance

### Key Statistics:
- Average Monthly Revenue: ${:,.2f}
- Highest Monthly Revenue: ${:,.2f}
- Lowest Monthly Revenue: ${:,.2f}
- Standard Deviation: ${:,.2f}

## 2. Daily Sales Distribution

### Orders by Day of Week:
{}

## 3. Category Performance

### Revenue by Category:
{}

## 4. Key Insights:

1. Sales Trends:
   - Total analyzed period: {} to {}
   - Peak revenue day: {}
   - Most active shopping day: {}

2. Category Analysis:
   - Top performing category: {}
   - Category with most orders: {}

3. Performance Metrics:
   - Total revenue: ${:,.2f}
   - Total number of orders: {}
   - Average order value: ${:,.2f}
    """.format(
        monthly_stats['total_revenue']['mean'],
        monthly_stats['total_revenue']['max'],
        monthly_stats['total_revenue']['min'],
        monthly_stats['total_revenue']['std'],
        daily_sales.to_string(index=False),
        category_sales.to_string(index=False),
        monthly_sales['month_year'].min().strftime('%Y-%m-%d'),
        monthly_sales['month_year'].max().strftime('%Y-%m-%d'),
        daily_sales.loc[daily_sales['total_revenue'].idxmax(), 'day_of_week'],
        daily_sales.loc[daily_sales['number_of_orders'].idxmax(), 'day_of_week'],
        category_sales.loc[category_sales['total_revenue'].idxmax(), 'category'],
        category_sales.loc[category_sales['number_of_orders'].idxmax(), 'category'],
        category_sales['total_revenue'].sum(),
        category_sales['number_of_orders'].sum(),
        category_sales['total_revenue'].sum() / category_sales['number_of_orders'].sum()
    )
    
    with open('sales_trend_report.md', 'w') as f:
        f.write(report)

def main():
    """
    Main function to execute the sales trend analysis
    """
    try:
        # Load the cleaned dataset
        df = load_data('ecommerce_data_cleaned.csv')
        
        # Perform analyses
        monthly_sales, monthly_stats = analyze_monthly_trends(df)
        daily_sales = analyze_daily_distribution(df)
        category_sales = analyze_category_trends(df)
        
        # Generate report
        generate_sales_report(monthly_sales, monthly_stats, daily_sales, category_sales)
        
        print("Analysis completed successfully! Check the generated report and visualizations.")
        
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 