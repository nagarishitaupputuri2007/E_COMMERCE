import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set style for better visualizations
plt.style.use('ggplot')
sns.set_palette("husl")

def load_and_prepare_data():
    # Load the cleaned data
    df = pd.read_csv('ecommerce_data_cleaned.csv')
    
    # Convert date column to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

def calculate_rfm_scores(df):
    # Calculate Recency, Frequency, and Monetary values
    today_date = df['order_date'].max()
    
    # Group by customer_id and calculate RFM metrics
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (today_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency (unique orders)
        'amount': 'sum'  # Monetary (total amount spent)
    }).reset_index()
    
    # Rename columns
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Calculate quintiles for scoring
    r_quintiles = rfm['recency'].quantile([0.2, 0.4, 0.6, 0.8]).to_dict()
    f_quintiles = rfm['frequency'].quantile([0.2, 0.4, 0.6, 0.8]).to_dict()
    m_quintiles = rfm['monetary'].quantile([0.2, 0.4, 0.6, 0.8]).to_dict()
    
    # Function to assign scores based on quintiles
    def assign_r_score(x):
        if x <= r_quintiles[0.2]:
            return 5
        elif x <= r_quintiles[0.4]:
            return 4
        elif x <= r_quintiles[0.6]:
            return 3
        elif x <= r_quintiles[0.8]:
            return 2
        else:
            return 1
            
    def assign_fm_score(x, quintiles):
        if x <= quintiles[0.2]:
            return 1
        elif x <= quintiles[0.4]:
            return 2
        elif x <= quintiles[0.6]:
            return 3
        elif x <= quintiles[0.8]:
            return 4
        else:
            return 5
    
    # Assign RFM scores
    rfm['R'] = rfm['recency'].apply(assign_r_score)
    rfm['F'] = rfm['frequency'].apply(lambda x: assign_fm_score(x, f_quintiles))
    rfm['M'] = rfm['monetary'].apply(lambda x: assign_fm_score(x, m_quintiles))
    
    return rfm

def segment_customers(rfm):
    # Calculate RFM Score
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    # Define customer segments
    def segment_customer(row):
        r, f, m = row['R'], row['F'], row['M']
        
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif (f >= 4 and m >= 4) or (r >= 4 and m >= 4):
            return 'Loyal Customers'
        elif r >= 4:
            return 'Recent Customers'
        elif m >= 4:
            return 'Big Spenders'
        elif r <= 2 and f <= 2 and m <= 2:
            return 'Lost Customers'
        elif r <= 2:
            return 'At Risk'
        else:
            return 'Average Customers'
    
    rfm['Customer_Segment'] = rfm.apply(segment_customer, axis=1)
    return rfm

def create_visualizations(rfm):
    # Set up the plotting style
    plt.style.use('ggplot')
    colors = sns.color_palette("husl", 7)
    
    # 1. Customer Segments Distribution
    plt.figure(figsize=(12, 6))
    segment_counts = rfm['Customer_Segment'].value_counts()
    ax = sns.barplot(x=segment_counts.index, y=segment_counts.values, palette=colors)
    plt.title('Distribution of Customer Segments', fontsize=14, pad=20)
    plt.xlabel('Customer Segment', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.xticks(rotation=45)
    
    # Add value labels on top of bars
    for i, v in enumerate(segment_counts.values):
        ax.text(i, v, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('customer_segments_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. RFM Score Distribution Heatmap
    plt.figure(figsize=(10, 8))
    rfm_pivot = pd.crosstab(rfm['R'], rfm['F'])
    sns.heatmap(rfm_pivot, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Number of Customers'})
    plt.title('RFM Score Distribution Heatmap', fontsize=14, pad=20)
    plt.xlabel('Frequency Score', fontsize=12)
    plt.ylabel('Recency Score', fontsize=12)
    plt.tight_layout()
    plt.savefig('rfm_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. 3D Scatter Plot using Plotly
    fig = px.scatter_3d(
        rfm,
        x='recency',
        y='frequency',
        z='monetary',
        color='Customer_Segment',
        title='3D RFM Analysis',
        labels={
            'recency': 'Recency (days)',
            'frequency': 'Frequency (orders)',
            'monetary': 'Monetary (total spend)'
        }
    )
    fig.update_layout(
        title_x=0.5,
        scene=dict(
            xaxis_title='Recency (days)',
            yaxis_title='Frequency (orders)',
            zaxis_title='Monetary (total spend)'
        )
    )
    fig.write_html('rfm_3d_scatter.html')
    
    # 4. Segment Revenue Distribution
    plt.figure(figsize=(10, 8))
    segment_revenue = rfm.groupby('Customer_Segment')['monetary'].sum()
    total_revenue = segment_revenue.sum()
    revenue_pct = (segment_revenue / total_revenue * 100).round(1)
    
    plt.pie(revenue_pct, 
            labels=[f'{segment}\n({pct}%)' for segment, pct in revenue_pct.items()],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90)
    plt.title('Revenue Distribution by Customer Segment', fontsize=14, pad=20)
    plt.axis('equal')
    plt.savefig('segment_revenue_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Load and prepare data
    print("Loading and preparing data...")
    df = load_and_prepare_data()
    
    # Calculate RFM scores
    print("Calculating RFM scores...")
    rfm = calculate_rfm_scores(df)
    
    # Segment customers
    print("Segmenting customers...")
    rfm = segment_customers(rfm)
    
    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(rfm)
    
    # Save the final RFM dataset
    print("Saving results...")
    rfm.to_csv('customer_segmentation_rfm.csv', index=False)
    
    # Generate summary statistics
    segment_stats = rfm.groupby('Customer_Segment').agg({
        'recency': ['mean', 'min', 'max'],
        'frequency': ['mean', 'min', 'max'],
        'monetary': ['mean', 'min', 'max'],
        'customer_id': 'count'
    }).round(2)
    
    segment_stats.columns = ['Recency_Mean', 'Recency_Min', 'Recency_Max',
                           'Frequency_Mean', 'Frequency_Min', 'Frequency_Max',
                           'Monetary_Mean', 'Monetary_Min', 'Monetary_Max',
                           'Customer_Count']
    
    segment_stats.to_csv('segment_statistics.csv')
    print("Analysis completed successfully!")

if __name__ == "__main__":
    main() 