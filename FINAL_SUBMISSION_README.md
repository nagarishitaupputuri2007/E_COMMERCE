# E-Commerce Data Analysis - Final Submission

## Overview
This submission package contains all deliverables from subtasks 1-4, providing a comprehensive analysis of the e-commerce dataset including data cleaning, sales trends, product analysis, geographic insights, and customer segmentation.

## Subtask 1: Data Cleaning and Preprocessing
### Files:
1. `data_cleaning.py` - Data cleaning script
2. `data_cleaning_report.md` - Detailed cleaning process documentation
3. `ecommerce_data_cleaned.csv` - Cleaned dataset
4. `outliers_amount.png` - Visualization of amount outliers
5. `outliers_quantity.png` - Visualization of quantity outliers

## Subtask 2: Sales Trend Analysis
### Files:
1. `sales_trend_analysis.py` - Analysis script
2. `sales_trend_report.md` - Detailed sales analysis report
3. Visualizations:
   - `daily_sales_trend.png`
   - `monthly_sales_trend.png`
   - `daily_sales_distribution.png`
   - `category_sales_performance.png`

### Key Findings:
- Peak sales: Monday ($2,439.90) and Tuesday ($2,179.76)
- Total revenue: $7,789.11

## Subtask 3: Product and Geographic Analysis
### Product Analysis Files:
1. `product_analysis.py` - Product analysis script
2. `product_analysis_report.md` - Detailed product insights
3. Visualizations:
   - `top_products_revenue.png`
   - `top_products_quantity.png`
   - `category_revenue_distribution.png`
   - `top_products_trend.png`

### Geographic Analysis Files:
1. `geographic_analysis.py` - Geographic analysis script
2. `geographic_analysis_report.md` - Regional insights report
3. `ecommerce_data_with_location.csv` - Dataset with location data
4. Visualizations:
   - `state_revenue_distribution.png`
   - `zone_revenue_distribution.png`
   - `top_cities_revenue.png`
   - `zone_category_distribution.png`

### Key Findings:
- Top product: Gaming Laptop ($1,299.99)
- Electronics dominates with 59.7% revenue share
- Karnataka leads with 31.84% revenue
- South zone contributes 38.90% of total revenue
- Metro cities drive 80% of revenue

## Subtask 4: RFM Analysis and Customer Segmentation
### Files:
1. `rfm_analysis.py` - RFM analysis script
2. `rfm_analysis_report.md` - Comprehensive RFM analysis report
3. Data Files:
   - `customer_segmentation_rfm.csv` - Customer segments with RFM scores
   - `segment_statistics.csv` - Detailed segment metrics
4. Visualizations:
   - `customer_segments_distribution.png` - Segment distribution chart
   - `rfm_heatmap.png` - RFM score patterns
   - `segment_revenue_distribution.png` - Revenue by segment
   - `rfm_3d_scatter.html` - Interactive RFM visualization

### Key Findings:
- Recent Customers: 29.4% (5 customers)
- Loyal Customers: 23.5% (4 customers)
- Lost Customers: 17.6% (3 customers)
- Big Spenders: 17.6% (3 customers)
- At Risk: 5.9% (1 customer)
- Average Customers: 5.9% (1 customer)

## Supporting Files
1. `requirements.txt` - Python package dependencies
2. `README.md` - Project overview and setup instructions
3. `indian_ecommerce_market_research.md` - Market context and research

## Setup Instructions
1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run analysis scripts in sequence:
   ```bash
   python data_cleaning.py
   python sales_trend_analysis.py
   python product_analysis.py
   python geographic_analysis.py
   python rfm_analysis.py
   ```

## Contact
For any questions or clarifications about this analysis, please contact the data analytics team. 