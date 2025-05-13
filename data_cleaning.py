import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    """
    Load the dataset and display initial information
    """
    print("Loading dataset...")
    df = pd.read_csv(file_path)
    print(f"\nInitial shape: {df.shape}")
    return df

def check_missing_values(df):
    """
    Check and display missing values in the dataset
    """
    print("\n1. Missing Values Analysis:")
    print("-" * 50)
    missing_values = df.isnull().sum()
    missing_percentage = (missing_values / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Missing Values': missing_values,
        'Percentage': missing_percentage
    })
    print(missing_df[missing_df['Missing Values'] > 0])
    return df

def handle_duplicates(df):
    """
    Check and remove duplicate records
    """
    print("\n2. Duplicate Records Analysis:")
    print("-" * 50)
    
    # Check duplicates based on order_id
    order_duplicates = df[df.duplicated(['order_id'], keep=False)]
    print(f"Duplicate orders found: {len(order_duplicates)}")
    
    # Remove duplicates keeping the first occurrence
    df_clean = df.drop_duplicates(subset=['order_id'], keep='first')
    print(f"Shape after removing duplicates: {df_clean.shape}")
    return df_clean

def correct_data_types(df):
    """
    Convert columns to appropriate data types
    """
    print("\n3. Correcting Data Types:")
    print("-" * 50)
    
    # Convert date column to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Ensure numeric columns are correct type
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    
    # Convert categorical columns to category type
    df['category'] = df['category'].astype('category')
    
    print("Updated data types:")
    print(df.dtypes)
    return df

def standardize_categories(df):
    """
    Standardize category names and other text fields
    """
    print("\n4. Standardizing Categories:")
    print("-" * 50)
    
    # Convert categories to title case and strip whitespace
    df['category'] = df['category'].str.strip().str.title()
    
    print("Unique categories after standardization:")
    print(df['category'].unique())
    return df

def handle_outliers(df):
    """
    Identify and handle outliers in numeric columns
    """
    print("\n5. Outlier Analysis:")
    print("-" * 50)
    
    numeric_cols = ['amount', 'quantity']
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        print(f"\nOutliers in {col}:")
        print(f"Number of outliers: {len(outliers)}")
        print(f"Outlier boundaries: {lower_bound:.2f} to {upper_bound:.2f}")
        
        # Create outlier plot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=df[col])
        plt.title(f'Boxplot of {col}')
        plt.savefig(f'outliers_{col}.png')
        plt.close()
    
    return df

def create_additional_features(df):
    """
    Create additional useful columns for analysis
    """
    print("\n6. Creating Additional Features:")
    print("-" * 50)
    
    # Extract date components
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['day_of_week'] = df['order_date'].dt.day_name()
    
    # Calculate total revenue per order
    df['total_revenue'] = df['quantity'] * df['amount']
    
    # Create customer purchase frequency
    customer_frequency = df.groupby('customer_id').size()
    df['customer_purchase_frequency'] = df['customer_id'].map(customer_frequency)
    
    print("New columns added:")
    print(df.columns[-5:])
    return df

def validate_data(df):
    """
    Perform final data validation checks
    """
    print("\n7. Final Data Validation:")
    print("-" * 50)
    
    # Check for negative values
    negative_amounts = df[df['amount'] < 0]
    negative_quantities = df[df['quantity'] < 0]
    
    print(f"Negative amounts found: {len(negative_amounts)}")
    print(f"Negative quantities found: {len(negative_quantities)}")
    
    # Check for future dates
    future_dates = df[df['order_date'] > datetime.now()]
    print(f"Future dates found: {len(future_dates)}")
    
    return df

def save_cleaned_data(df, output_path):
    """
    Save the cleaned dataset
    """
    df.to_csv(output_path, index=False)
    print(f"\nCleaned dataset saved to: {output_path}")

def main():
    """
    Main function to execute the data cleaning pipeline
    """
    input_file = 'ecommerce_data.csv'
    output_file = 'ecommerce_data_cleaned.csv'
    
    try:
        # Load the data
        df = load_data(input_file)
        
        # Apply cleaning steps
        df = check_missing_values(df)
        df = handle_duplicates(df)
        df = correct_data_types(df)
        df = standardize_categories(df)
        df = handle_outliers(df)
        df = create_additional_features(df)
        df = validate_data(df)
        
        # Save the cleaned dataset
        save_cleaned_data(df, output_file)
        
        print("\nData cleaning process completed successfully!")
        
    except Exception as e:
        print(f"Error occurred during data cleaning: {str(e)}")

if __name__ == "__main__":
    main() 