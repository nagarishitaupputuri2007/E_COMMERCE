import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    """
    Load the cleaned dataset
    """
    return pd.read_csv(file_path, parse_dates=['order_date'])

def analyze_product_performance(df):
    """
    Analyze and visualize product performance
    """
    # Product level analysis
    product_performance = df.groupby('product_name').agg({
        'quantity': 'sum',
        'total_revenue': 'sum',
        'order_id': 'count'
    }).reset_index()
    
    product_performance = product_performance.sort_values('total_revenue', ascending=False)
    
    # Visualize top products by revenue
    plt.figure(figsize=(12, 6))
    sns.barplot(data=product_performance.head(10), 
                x='total_revenue', 
                y='product_name')
    plt.title('Top 10 Products by Revenue', fontsize=14)
    plt.xlabel('Total Revenue ($)', fontsize=12)
    plt.ylabel('Product Name', fontsize=12)
    plt.tight_layout()
    plt.savefig('top_products_revenue.png')
    plt.close()
    
    # Visualize top products by quantity
    plt.figure(figsize=(12, 6))
    product_by_quantity = product_performance.sort_values('quantity', ascending=False)
    sns.barplot(data=product_by_quantity.head(10), 
                x='quantity', 
                y='product_name')
    plt.title('Top 10 Products by Quantity Sold', fontsize=14)
    plt.xlabel('Total Quantity Sold', fontsize=12)
    plt.ylabel('Product Name', fontsize=12)
    plt.tight_layout()
    plt.savefig('top_products_quantity.png')
    plt.close()
    
    return product_performance

def analyze_category_performance(df):
    """
    Analyze and visualize category performance
    """
    # Category level analysis
    category_performance = df.groupby('category').agg({
        'quantity': 'sum',
        'total_revenue': 'sum',
        'order_id': 'count',
        'product_id': 'nunique'
    }).reset_index()
    
    category_performance = category_performance.sort_values('total_revenue', ascending=False)
    
    # Calculate category share
    total_revenue = category_performance['total_revenue'].sum()
    category_performance['revenue_share'] = (category_performance['total_revenue'] / total_revenue * 100).round(2)
    
    # Visualize category revenue distribution
    plt.figure(figsize=(10, 6))
    plt.pie(category_performance['revenue_share'], 
            labels=category_performance['category'],
            autopct='%1.1f%%',
            startangle=90)
    plt.title('Revenue Distribution by Category', fontsize=14)
    plt.axis('equal')
    plt.savefig('category_revenue_distribution.png')
    plt.close()
    
    return category_performance

def analyze_product_trends(df):
    """
    Analyze product trends over time
    """
    # Daily product performance
    daily_product = df.groupby(['order_date', 'product_name'])['quantity'].sum().reset_index()
    
    # Get top 5 products
    top_products = df.groupby('product_name')['total_revenue'].sum().nlargest(5).index
    
    # Visualize daily trends for top products
    plt.figure(figsize=(12, 6))
    for product in top_products:
        product_data = daily_product[daily_product['product_name'] == product]
        plt.plot(product_data['order_date'], 
                product_data['quantity'], 
                marker='o', 
                label=product)
    
    plt.title('Daily Sales Trends - Top 5 Products', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Quantity Sold', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('top_products_trend.png')
    plt.close()

def generate_product_report(product_performance, category_performance):
    """
    Generate a comprehensive product analysis report
    """
    report = """
# Best-Selling Products and Categories Analysis Report

## 1. Top 10 Products by Revenue

{}

## 2. Top 10 Products by Quantity Sold

{}

## 3. Category Performance Overview

{}

## 4. Key Insights

### Product Performance:
1. Highest Revenue Product: {} (${:,.2f})
2. Most Sold Product: {} ({} units)
3. Average Revenue per Product: ${:,.2f}

### Category Performance:
1. Top Category: {} (${:,.2f} revenue, {:.1f}% share)
2. Most Diverse Category: {} ({} unique products)
3. Average Orders per Category: {:.1f}

### Sales Distribution:
1. Total Products Sold: {} units
2. Total Revenue Generated: ${:,.2f}
3. Average Order Value: ${:,.2f}

## 5. Recommendations

1. Inventory Management:
   - Maintain higher stock levels for top-selling products
   - Consider bundling opportunities for complementary products
   - Monitor stock levels for high-revenue products

2. Category Strategy:
   - Focus marketing efforts on {} category
   - Expand product range in successful categories
   - Review pricing strategy for high-volume products

3. Product Development:
   - Consider introducing new products in successful categories
   - Analyze features of top-selling products
   - Monitor customer feedback for popular items
    """.format(
        product_performance[['product_name', 'quantity', 'total_revenue']].head(10).to_string(index=False),
        product_performance[['product_name', 'quantity', 'total_revenue']].sort_values('quantity', ascending=False).head(10).to_string(index=False),
        category_performance.to_string(index=False),
        product_performance.iloc[0]['product_name'],
        product_performance.iloc[0]['total_revenue'],
        product_performance.sort_values('quantity', ascending=False).iloc[0]['product_name'],
        product_performance.sort_values('quantity', ascending=False).iloc[0]['quantity'],
        product_performance['total_revenue'].mean(),
        category_performance.iloc[0]['category'],
        category_performance.iloc[0]['total_revenue'],
        category_performance.iloc[0]['revenue_share'],
        category_performance.sort_values('product_id', ascending=False).iloc[0]['category'],
        category_performance.sort_values('product_id', ascending=False).iloc[0]['product_id'],
        category_performance['order_id'].mean(),
        product_performance['quantity'].sum(),
        product_performance['total_revenue'].sum(),
        product_performance['total_revenue'].sum() / product_performance['order_id'].sum(),
        category_performance.iloc[0]['category']
    )
    
    with open('product_analysis_report.md', 'w') as f:
        f.write(report)

def main():
    """
    Main function to execute the product analysis
    """
    try:
        # Load the cleaned dataset
        df = load_data('ecommerce_data_cleaned.csv')
        
        # Perform analyses
        product_performance = analyze_product_performance(df)
        category_performance = analyze_category_performance(df)
        analyze_product_trends(df)
        
        # Generate report
        generate_product_report(product_performance, category_performance)
        
        print("Product analysis completed successfully! Check the generated report and visualizations.")
        
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 