import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_data(file_path):
    """
    Load the e-commerce dataset and ensure proper date formatting
    """
    df = pd.read_csv(file_path)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

def calculate_rfm_metrics(df, reference_date=None):
    """
    Calculate RFM metrics for each customer
    """
    # If no reference date provided, use the most recent date in the dataset
    if reference_date is None:
        reference_date = df['order_date'].max()
    
    # Group by customer_id and calculate RFM metrics
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (reference_date - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency
        'total_revenue': 'sum',  # Monetary
        'product_id': 'nunique',  # Number of unique products
        'category': lambda x: x.nunique()  # Number of unique categories
    }).reset_index()
    
    # Rename columns
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary', 'unique_products', 'unique_categories']
    return rfm

def assign_rfm_scores(rfm):
    """
    Assign RFM scores (1-5) using quintiles
    """
    # Create quintiles for each metric
    r_labels = range(5, 0, -1)  # 5 is best (lowest recency)
    f_labels = range(1, 6)      # 5 is best (highest frequency)
    m_labels = range(1, 6)      # 5 is best (highest monetary)
    
    # Assign scores using quintiles
    r_quintiles = pd.qcut(rfm['recency'], q=5, labels=r_labels)
    f_quintiles = pd.qcut(rfm['frequency'], q=5, labels=f_labels)
    m_quintiles = pd.qcut(rfm['monetary'], q=5, labels=m_labels)
    
    # Add scores to dataframe
    rfm['R'] = r_quintiles
    rfm['F'] = f_quintiles
    rfm['M'] = m_quintiles
    
    # Calculate RFM Score
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    return rfm

def segment_customers(rfm):
    """
    Segment customers based on RFM scores with detailed criteria
    """
    # Calculate average RFM score
    rfm['RFM_Avg'] = (rfm['R'] + rfm['F'] + rfm['M']) / 3
    
    def segment_label(row):
        # Champions: Recent buyers, frequent buyers, high spending
        if (row['R'] >= 4) and (row['F'] >= 4) and (row['M'] >= 4):
            return 'Champions'
        
        # Loyal Customers: Regular buyers with good spending
        elif (row['R'] >= 3) and (row['F'] >= 3) and (row['M'] >= 3):
            return 'Loyal Customers'
        
        # Potential Loyalists: Recent buyers with moderate frequency
        elif (row['R'] >= 4) and (row['F'] >= 2):
            return 'Potential Loyalists'
        
        # New Customers: Very recent buyers but low frequency
        elif (row['R'] == 5) and (row['F'] == 1):
            return 'New Customers'
        
        # At Risk: Low recency but good history
        elif (row['R'] <= 2) and (row['F'] >= 3) and (row['M'] >= 3):
            return 'At Risk'
        
        # Lost Customers: Lowest scores across all metrics
        elif (row['R'] == 1) and (row['F'] == 1) and (row['M'] == 1):
            return 'Lost Customers'
        
        # Average Customers: Middle scores
        else:
            return 'Average Customers'
    
    rfm['Customer_Segment'] = rfm.apply(segment_label, axis=1)
    return rfm

def analyze_segment_behavior(rfm, df):
    """
    Analyze detailed behavior patterns for each segment
    """
    # Segment level metrics
    segment_analysis = rfm.groupby('Customer_Segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'unique_products': 'mean',
        'unique_categories': 'mean'
    }).round(2)
    
    segment_analysis.columns = [
        'Customer_Count',
        'Avg_Recency_Days',
        'Avg_Purchase_Frequency',
        'Avg_Revenue',
        'Avg_Unique_Products',
        'Avg_Categories'
    ]
    
    return segment_analysis

def create_segment_distribution_plots(rfm):
    """
    Create detailed distribution plots for customer segments
    """
    # 1. Bar Chart of Segment Distribution
    plt.figure(figsize=(12, 6))
    segment_counts = rfm['Customer_Segment'].value_counts()
    ax = segment_counts.plot(kind='bar')
    plt.title('Distribution of Customers Across Segments')
    plt.xlabel('Customer Segment')
    plt.ylabel('Number of Customers')
    plt.xticks(rotation=45)
    
    # Add value labels on top of bars
    for i, v in enumerate(segment_counts):
        ax.text(i, v, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('segment_distribution_bar.png')
    plt.close()

def create_rfm_scatter_plots(rfm):
    """
    Create scatter plots to visualize relationships between RFM metrics
    """
    # 1. Recency vs Frequency
    plt.figure(figsize=(10, 6))
    for segment in rfm['Customer_Segment'].unique():
        segment_data = rfm[rfm['Customer_Segment'] == segment]
        plt.scatter(segment_data['recency'], 
                   segment_data['frequency'],
                   label=segment,
                   alpha=0.6)
    
    plt.title('Customer Segments: Recency vs Frequency')
    plt.xlabel('Recency (days)')
    plt.ylabel('Frequency (number of orders)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('rfm_recency_frequency_scatter.png')
    plt.close()
    
    # 2. Frequency vs Monetary
    plt.figure(figsize=(10, 6))
    for segment in rfm['Customer_Segment'].unique():
        segment_data = rfm[rfm['Customer_Segment'] == segment]
        plt.scatter(segment_data['frequency'], 
                   segment_data['monetary'],
                   label=segment,
                   alpha=0.6)
    
    plt.title('Customer Segments: Frequency vs Monetary')
    plt.xlabel('Frequency (number of orders)')
    plt.ylabel('Monetary (total revenue)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('rfm_frequency_monetary_scatter.png')
    plt.close()
    
    # 3. Bubble Plot: RFM Combined
    plt.figure(figsize=(12, 8))
    for segment in rfm['Customer_Segment'].unique():
        segment_data = rfm[rfm['Customer_Segment'] == segment]
        plt.scatter(segment_data['recency'],
                   segment_data['frequency'],
                   s=segment_data['monetary']/100,  # Size proportional to monetary value
                   label=segment,
                   alpha=0.6)
    
    plt.title('Customer Segments: RFM Bubble Plot')
    plt.xlabel('Recency (days)')
    plt.ylabel('Frequency (number of orders)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('rfm_bubble_plot.png')
    plt.close()

def create_rfm_heatmaps(rfm):
    """
    Create detailed heatmaps for RFM analysis
    """
    # 1. Recency-Frequency Heatmap
    plt.figure(figsize=(10, 8))
    rf_pivot = pd.crosstab(rfm['R'], rfm['F'])
    sns.heatmap(rf_pivot, annot=True, fmt='d', cmap='YlOrRd')
    plt.title('Customer Distribution: Recency vs Frequency Scores')
    plt.xlabel('Frequency Score')
    plt.ylabel('Recency Score')
    plt.tight_layout()
    plt.savefig('recency_frequency_heatmap.png')
    plt.close()
    
    # 2. Frequency-Monetary Heatmap
    plt.figure(figsize=(10, 8))
    fm_pivot = pd.crosstab(rfm['F'], rfm['M'])
    sns.heatmap(fm_pivot, annot=True, fmt='d', cmap='YlOrRd')
    plt.title('Customer Distribution: Frequency vs Monetary Scores')
    plt.xlabel('Monetary Score')
    plt.ylabel('Frequency Score')
    plt.tight_layout()
    plt.savefig('frequency_monetary_heatmap.png')
    plt.close()

def create_segment_metrics_plots(rfm, segment_analysis):
    """
    Create plots showing key metrics for each segment
    """
    # 1. Average Values by Segment
    metrics = ['Avg_Recency_Days', 'Avg_Purchase_Frequency', 'Avg_Revenue']
    
    plt.figure(figsize=(15, 6))
    segment_analysis[metrics].plot(kind='bar', width=0.8)
    plt.title('Average Metrics by Customer Segment')
    plt.xlabel('Customer Segment')
    plt.ylabel('Value')
    plt.legend(title='Metrics', bbox_to_anchor=(1.05, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('segment_metrics_comparison.png')
    plt.close()
    
    # 2. Segment Revenue Contribution
    plt.figure(figsize=(10, 10))
    revenue_by_segment = rfm.groupby('Customer_Segment')['monetary'].sum()
    total_revenue = revenue_by_segment.sum()
    revenue_pct = (revenue_by_segment / total_revenue * 100).round(1)
    
    plt.pie(revenue_pct, labels=[f'{segment}\n({pct}%)' for segment, pct in revenue_pct.items()],
            autopct='%1.1f%%', startangle=90)
    plt.title('Revenue Contribution by Customer Segment')
    plt.axis('equal')
    plt.savefig('segment_revenue_pie.png')
    plt.close()

def visualize_rfm_segments(rfm, segment_analysis):
    """
    Create comprehensive visualizations for RFM analysis
    """
    print("Creating segment distribution plots...")
    create_segment_distribution_plots(rfm)
    
    print("Creating RFM scatter plots...")
    create_rfm_scatter_plots(rfm)
    
    print("Creating RFM heatmaps...")
    create_rfm_heatmaps(rfm)
    
    print("Creating segment metrics plots...")
    create_segment_metrics_plots(rfm, segment_analysis)
    
    print("Visualization complete! Check the generated plot files.")

def generate_rfm_report(rfm, segment_analysis):
    """
    Generate a comprehensive RFM analysis report with segment-specific insights
    """
    report = """
# Enhanced RFM Analysis Report

## Overview
This report presents a detailed customer segmentation analysis based on RFM (Recency, Frequency, Monetary) metrics.

## Customer Segments Summary

{}

## Detailed Segment Analysis

{}

## Segment-Specific Recommendations

1. Champions (Best Customers):
   - Implement VIP customer program with exclusive benefits
   - Offer early access to new products and special collections
   - Create a referral program with attractive rewards
   - Seek testimonials and feature their success stories
   - Provide dedicated customer service support

2. Loyal Customers:
   - Develop personalized communication strategies
   - Create a tiered loyalty rewards program
   - Offer premium customer service and priority support
   - Send birthday/anniversary special offers
   - Cross-sell complementary products

3. Potential Loyalists:
   - Encourage more frequent purchases through targeted promotions
   - Implement engagement programs with clear benefits
   - Send product recommendations based on past purchases
   - Offer moderate discounts on next purchase
   - Create educational content about products

4. New Customers:
   - Welcome series emails with product guides
   - First-time purchase incentives
   - Educational content about products and benefits
   - Clear communication about loyalty program benefits
   - Follow-up surveys for feedback

5. At Risk Customers:
   - Launch re-engagement email campaigns
   - Offer "We Miss You" discounts
   - Conduct surveys to understand pain points
   - Provide special comeback offers
   - Personal outreach from customer service

6. Lost Customers:
   - Implement win-back campaigns with attractive offers
   - Survey to understand reasons for churn
   - Update contact information and preferences
   - Offer significant discounts on favorite products
   - Consider remarketing campaigns

7. Average Customers:
   - Regular engagement through newsletters
   - Moderate promotional offers
   - Product recommendations based on browsing history
   - Encourage product reviews and feedback
   - Highlight loyalty program benefits

## Key Metrics by Segment

### Recency (days)
{}

### Frequency (orders)
{}

### Monetary (revenue)
{}

## Action Items

1. Immediate Actions:
   - Launch VIP program for Champions
   - Implement re-engagement campaign for At Risk customers
   - Create welcome series for New Customers
   - Develop win-back campaign for Lost Customers

2. Medium-term Actions:
   - Develop loyalty program tiers
   - Create segment-specific email campaigns
   - Implement personalized recommendation system
   - Design referral program

3. Long-term Strategy:
   - Regular monitoring of segment transitions
   - Continuous refinement of segmentation criteria
   - Development of predictive churn models
   - Implementation of automated marketing workflows
    """.format(
        rfm['Customer_Segment'].value_counts().to_frame().to_string(),
        segment_analysis.to_string(),
        rfm['recency'].describe().round(2).to_string(),
        rfm['frequency'].describe().round(2).to_string(),
        rfm['monetary'].describe().round(2).to_string()
    )
    
    with open('rfm_analysis_report.md', 'w') as f:
        f.write(report)

def main():
    """
    Main function to execute enhanced RFM analysis
    """
    try:
        # Load the data
        print("Loading data...")
        df = load_data('ecommerce_data_cleaned.csv')
        
        # Calculate RFM metrics
        print("Calculating RFM metrics...")
        rfm = calculate_rfm_metrics(df)
        
        # Assign RFM scores
        print("Assigning RFM scores...")
        rfm = assign_rfm_scores(rfm)
        
        # Segment customers
        print("Segmenting customers...")
        rfm = segment_customers(rfm)
        
        # Analyze segment behavior
        print("Analyzing segment behavior...")
        segment_analysis = analyze_segment_behavior(rfm, df)
        
        # Create visualizations
        print("Creating visualizations...")
        visualize_rfm_segments(rfm, segment_analysis)
        
        # Generate report
        print("Generating comprehensive report...")
        generate_rfm_report(rfm, segment_analysis)
        
        # Save RFM data
        rfm.to_csv('rfm_analysis_results.csv', index=False)
        segment_analysis.to_csv('segment_analysis_results.csv')
        
        print("Enhanced RFM analysis completed successfully! Check the generated reports and visualizations.")
        
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 