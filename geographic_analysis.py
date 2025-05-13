import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    """
    Load the dataset with geographic information
    """
    return pd.read_csv(file_path, parse_dates=['order_date'])

def analyze_state_performance(df):
    """
    Analyze sales performance by state
    """
    # State level analysis
    state_performance = df.groupby('state').agg({
        'total_revenue': 'sum',
        'order_id': 'count',
        'customer_id': 'nunique',
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate state metrics
    state_performance['average_order_value'] = state_performance['total_revenue'] / state_performance['order_id']
    state_performance['revenue_share'] = (state_performance['total_revenue'] / state_performance['total_revenue'].sum() * 100).round(2)
    
    # Sort by revenue
    state_performance = state_performance.sort_values('total_revenue', ascending=False)
    
    # Visualize state revenue distribution
    plt.figure(figsize=(12, 6))
    sns.barplot(data=state_performance, x='state', y='total_revenue')
    plt.title('Revenue Distribution by State', fontsize=14)
    plt.xlabel('State', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('state_revenue_distribution.png')
    plt.close()
    
    return state_performance

def analyze_zone_performance(df):
    """
    Analyze sales performance by zone
    """
    # Zone level analysis
    zone_performance = df.groupby('zone').agg({
        'total_revenue': 'sum',
        'order_id': 'count',
        'state': 'nunique',
        'city': 'nunique'
    }).reset_index()
    
    # Calculate zone metrics
    zone_performance['revenue_share'] = (zone_performance['total_revenue'] / zone_performance['total_revenue'].sum() * 100).round(2)
    
    # Visualize zone distribution
    plt.figure(figsize=(10, 6))
    plt.pie(zone_performance['revenue_share'], 
            labels=zone_performance['zone'],
            autopct='%1.1f%%',
            startangle=90)
    plt.title('Revenue Distribution by Zone', fontsize=14)
    plt.axis('equal')
    plt.savefig('zone_revenue_distribution.png')
    plt.close()
    
    return zone_performance

def analyze_city_performance(df):
    """
    Analyze sales performance by city
    """
    # City level analysis
    city_performance = df.groupby(['city', 'state']).agg({
        'total_revenue': 'sum',
        'order_id': 'count',
        'customer_id': 'nunique'
    }).reset_index()
    
    # Sort by revenue
    city_performance = city_performance.sort_values('total_revenue', ascending=False)
    
    # Visualize top cities
    plt.figure(figsize=(12, 6))
    sns.barplot(data=city_performance.head(10), x='city', y='total_revenue')
    plt.title('Top 10 Cities by Revenue', fontsize=14)
    plt.xlabel('City', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_cities_revenue.png')
    plt.close()
    
    return city_performance

def analyze_category_by_zone(df):
    """
    Analyze category performance by zone
    """
    # Category performance by zone
    zone_category = df.groupby(['zone', 'category'])['total_revenue'].sum().unstack()
    
    # Visualize category distribution by zone
    plt.figure(figsize=(12, 6))
    zone_category.plot(kind='bar', stacked=True)
    plt.title('Category Revenue Distribution by Zone', fontsize=14)
    plt.xlabel('Zone', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('zone_category_distribution.png')
    plt.close()
    
    return zone_category

def generate_geographic_report(state_performance, zone_performance, city_performance, zone_category):
    """
    Generate a comprehensive geographic analysis report
    """
    report = """
# Geographic Sales Performance Analysis Report

## 1. State-wise Performance

### Top 5 States by Revenue:
{}

### State-wise Metrics:
{}

## 2. Zone-wise Performance

### Zone Distribution:
{}

## 3. City-wise Performance

### Top 10 Cities by Revenue:
{}

## 4. Category Performance by Zone:
{}

## 5. Key Insights

### Regional Performance:
1. Top Performing State: {} (${:,.2f} revenue, {:.1f}% share)
2. Top Performing City: {} (${:,.2f} revenue)
3. Leading Zone: {} (${:,.2f} revenue, {:.1f}% share)

### Geographic Distribution:
1. Number of Active States: {}
2. Number of Active Cities: {}
3. Average Revenue per State: ${:,.2f}
4. Average Revenue per City: ${:,.2f}

### Customer Reach:
1. Most Customer Dense State: {} ({} unique customers)
2. Most Orders from: {} ({} orders)
3. Highest Average Order Value: {} (${:,.2f})

## 6. Recommendations

1. Market Expansion:
   - Focus on expanding presence in {} where revenue share is highest
   - Target high-potential cities in {} zone
   - Develop strategies for low-performing states

2. Regional Strategy:
   - Customize marketing campaigns for {} zone preferences
   - Optimize delivery network in top-performing cities
   - Consider regional warehouses in major hubs

3. Category Focus:
   - Promote top-performing categories in each zone
   - Analyze successful category-region combinations
   - Develop region-specific product bundles
    """.format(
        state_performance.head().to_string(index=False),
        state_performance.to_string(index=False),
        zone_performance.to_string(index=False),
        city_performance.head(10).to_string(index=False),
        zone_category.to_string(),
        state_performance.iloc[0]['state'],
        state_performance.iloc[0]['total_revenue'],
        state_performance.iloc[0]['revenue_share'],
        city_performance.iloc[0]['city'],
        city_performance.iloc[0]['total_revenue'],
        zone_performance.iloc[zone_performance['total_revenue'].idxmax()]['zone'],
        zone_performance.iloc[zone_performance['total_revenue'].idxmax()]['total_revenue'],
        zone_performance.iloc[zone_performance['total_revenue'].idxmax()]['revenue_share'],
        state_performance['state'].nunique(),
        city_performance['city'].nunique(),
        state_performance['total_revenue'].mean(),
        city_performance['total_revenue'].mean(),
        state_performance.iloc[state_performance['customer_id'].idxmax()]['state'],
        state_performance.iloc[state_performance['customer_id'].idxmax()]['customer_id'],
        state_performance.iloc[state_performance['order_id'].idxmax()]['state'],
        state_performance.iloc[state_performance['order_id'].idxmax()]['order_id'],
        state_performance.iloc[state_performance['average_order_value'].idxmax()]['state'],
        state_performance.iloc[state_performance['average_order_value'].idxmax()]['average_order_value'],
        state_performance.iloc[0]['state'],
        zone_performance.iloc[zone_performance['total_revenue'].idxmax()]['zone'],
        zone_performance.iloc[zone_performance['revenue_share'].idxmax()]['zone']
    )
    
    with open('geographic_analysis_report.md', 'w') as f:
        f.write(report)

def main():
    """
    Main function to execute the geographic analysis
    """
    try:
        # Load the dataset
        df = load_data('ecommerce_data_with_location.csv')
        
        # Calculate total revenue
        df['total_revenue'] = df['quantity'] * df['amount']
        
        # Perform analyses
        state_performance = analyze_state_performance(df)
        zone_performance = analyze_zone_performance(df)
        city_performance = analyze_city_performance(df)
        zone_category = analyze_category_by_zone(df)
        
        # Generate report
        generate_geographic_report(state_performance, zone_performance, 
                                city_performance, zone_category)
        
        print("Geographic analysis completed successfully! Check the generated report and visualizations.")
        
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 