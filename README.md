# E-Commerce Data Analysis Project

## Project Overview
This project contains a cleaned and preprocessed e-commerce dataset along with the cleaning scripts and documentation. The dataset includes transaction data with customer purchases, product information, and derived metrics for analysis.

## File Structure
```
.
├── ecommerce_data.csv          # Original dataset
├── ecommerce_data_cleaned.csv  # Cleaned dataset
├── data_cleaning.py            # Data cleaning script
├── data_cleaning_report.md     # Detailed cleaning process documentation
├── outliers_amount.png         # Visualization of amount outliers
└── outliers_quantity.png       # Visualization of quantity outliers
```

## Dataset Description

### Original Dataset Columns
- order_id: Unique identifier for each order
- customer_id: Unique identifier for each customer
- product_id: Unique identifier for each product
- order_date: Date of the order
- quantity: Number of items purchased
- amount: Price per item
- product_name: Name of the product
- category: Product category

### Additional Features in Cleaned Dataset
- year: Year extracted from order_date
- month: Month extracted from order_date
- day_of_week: Day name extracted from order_date
- total_revenue: Total revenue per order (quantity × amount)
- customer_purchase_frequency: Number of orders per customer

## Requirements
- Python 3.7+
- pandas
- numpy
- matplotlib
- seaborn

## Installation
```bash
pip install pandas numpy matplotlib seaborn
```

## Usage
To run the data cleaning process:
```bash
python data_cleaning.py
```

The script will:
1. Load the original dataset
2. Perform cleaning operations
3. Generate outlier visualizations
4. Save the cleaned dataset

## Data Quality Assurance
The cleaned dataset has been verified for:
- No missing values
- No duplicate records
- Correct data types
- Standardized categories
- Valid date ranges
- Non-negative quantities and amounts

## Documentation
For detailed information about the cleaning process and findings, please refer to:
- `data_cleaning_report.md`: Complete documentation of the cleaning process
- Generated visualizations in PNG format for outlier analysis

## License
This project is licensed under the MIT License - see the LICENSE file for details. 