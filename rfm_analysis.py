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
        'total_revenue': 'sum'  # Monetary
    }).reset_index()
    
    # Rename columns
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
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
    Segment customers based on RFM scores
    """
    # Calculate average RFM score
    rfm['RFM_Avg'] = (rfm['R'] + rfm['F'] + rfm['M']) / 3
    
    # Define customer segments
    def segment_label(row):
        if row['RFM_Avg'] >= 4.5:
            return 'Champions'
        elif (row['R'] >= 4) and (row['F'] >= 3) and (row['M'] >= 3):
            return 'Loyal Customers'
        elif (row['R'] >= 3) and (row['F'] >= 2) and (row['M'] >= 2):
            return 'Potential Loyalists'
        elif row['R'] <= 2:
            return 'At Risk'
        elif (row['R'] <= 1) and (row['F'] <= 1) and (row['M'] <= 1):
            return 'Lost Customers'
        else:
            return 'Average Customers'
    
    rfm['Customer_Segment'] = rfm.apply(segment_label, axis=1)
    return rfm

def visualize_rfm_segments(rfm):
    """
    Create visualizations for RFM analysis
    """
    # 1. Customer Segments Distribution
    plt.figure(figsize=(10, 6))
    segment_counts = rfm['Customer_Segment'].value_counts()
    plt.pie(segment_counts, labels=segment_counts.index, autopct='%1.1f%%')
    plt.title('Customer Segments Distribution')
    plt.savefig('customer_segments_distribution.png')
    plt.close()
    
    # 2. Average RFM Values by Segment
    plt.figure(figsize=(12, 6))
    segment_avg = rfm.groupby('Customer_Segment')[['R', 'F', 'M']].mean()
    segment_avg.plot(kind='bar')
    plt.title('Average RFM Values by Customer Segment')
    plt.xlabel('Customer Segment')
    plt.ylabel('Average Score')
    plt.legend(title='RFM Metrics')
    plt.tight_layout()
    plt.savefig('rfm_values_by_segment.png')
    plt.close()

def generate_rfm_report(rfm):
    """
    Generate a comprehensive RFM analysis report
    """
    report = """
# RFM Analysis Report

## Overview
This report presents the results of RFM (Recency, Frequency, Monetary) analysis performed on the e-commerce customer data.

## Customer Segments Summary

{}

## Key Metrics by Segment

{}

## Recommendations

1. Champions (Best Customers):
   - Implement VIP customer program
   - Offer exclusive early access to new products
   - Seek testimonials and referrals

2. Loyal Customers:
   - Provide personalized communication
   - Create loyalty rewards program
   - Offer premium customer service

3. Potential Loyalists:
   - Encourage more frequent purchases
   - Provide targeted promotions
   - Implement engagement programs

4. At Risk Customers:
   - Re-engagement email campaign
   - Special "We Miss You" offers
   - Gather feedback through surveys

5. Lost Customers:
   - Win-back campaign with attractive offers
   - Understand reasons for churn
   - Update contact information

## Detailed Statistics

### Recency (days)
{}

### Frequency (orders)
{}

### Monetary (revenue)
{}
    """.format(
        rfm['Customer_Segment'].value_counts().to_frame().to_string(),
        rfm.groupby('Customer_Segment')[['recency', 'frequency', 'monetary']].mean().round(2).to_string(),
        rfm['recency'].describe().round(2).to_string(),
        rfm['frequency'].describe().round(2).to_string(),
        rfm['monetary'].describe().round(2).to_string()
    )
    
    with open('rfm_analysis_report.md', 'w') as f:
        f.write(report)

def main():
    """
    Main function to execute RFM analysis
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
        
        # Create visualizations
        print("Creating visualizations...")
        visualize_rfm_segments(rfm)
        
        # Generate report
        print("Generating report...")
        generate_rfm_report(rfm)
        
        # Save RFM data
        rfm.to_csv('rfm_analysis_results.csv', index=False)
        
        print("RFM analysis completed successfully! Check the generated report and visualizations.")
        
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 