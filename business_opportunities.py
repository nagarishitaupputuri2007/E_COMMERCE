import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Tuple, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BusinessOpportunityAnalyzer:
    def __init__(self, sales_data: pd.DataFrame, forecast_data: pd.DataFrame):
        self.sales_data = sales_data
        self.forecast_data = forecast_data
        
    def analyze_product_categories(self) -> Dict[str, Dict]:
        """
        Analyze product categories for growth opportunities
        """
        try:
            # Group by category and calculate metrics
            category_analysis = self.sales_data.groupby('category').agg({
                'amount': ['sum', 'mean', 'count'],
                'quantity': 'sum'
            }).round(2)
            
            # Calculate growth rate for each category
            category_growth = self.sales_data.pivot_table(
                index='category',
                columns=pd.Grouper(key='date', freq='M'),
                values='amount',
                aggfunc='sum'
            ).pct_change(axis=1).mean(axis=1)
            
            # Combine metrics
            category_metrics = {
                cat: {
                    'total_revenue': stats[('amount', 'sum')],
                    'avg_order_value': stats[('amount', 'mean')],
                    'order_count': stats[('amount', 'count')],
                    'total_quantity': stats[('quantity', 'sum')],
                    'growth_rate': category_growth[cat] if cat in category_growth else 0
                }
                for cat, stats in category_analysis.iterrows()
            }
            
            return category_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing product categories: {str(e)}")
            return {}
    
    def analyze_regional_performance(self) -> Dict[str, Dict]:
        """
        Analyze regional sales performance
        """
        try:
            # Group by region and calculate metrics
            regional_analysis = self.sales_data.groupby('region').agg({
                'amount': ['sum', 'mean', 'count'],
                'customer_id': 'nunique'
            }).round(2)
            
            # Calculate growth rate for each region
            regional_growth = self.sales_data.pivot_table(
                index='region',
                columns=pd.Grouper(key='date', freq='M'),
                values='amount',
                aggfunc='sum'
            ).pct_change(axis=1).mean(axis=1)
            
            # Combine metrics
            regional_metrics = {
                region: {
                    'total_revenue': stats[('amount', 'sum')],
                    'avg_order_value': stats[('amount', 'mean')],
                    'order_count': stats[('amount', 'count')],
                    'unique_customers': stats[('customer_id', 'nunique')],
                    'growth_rate': regional_growth[region] if region in regional_growth else 0
                }
                for region, stats in regional_analysis.iterrows()
            }
            
            return regional_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing regional performance: {str(e)}")
            return {}
    
    def identify_cross_selling_opportunities(self) -> List[Tuple[str, str, float]]:
        """
        Identify product pairs frequently bought together
        """
        try:
            # Group transactions by order_id
            order_products = self.sales_data.groupby('order_id')['product_id'].agg(list)
            
            # Find product pairs
            product_pairs = []
            for products in order_products:
                if len(products) > 1:
                    for i in range(len(products)):
                        for j in range(i + 1, len(products)):
                            product_pairs.append(tuple(sorted([products[i], products[j]])))
            
            # Calculate pair frequencies
            pair_counts = pd.Series(product_pairs).value_counts()
            
            # Get top product pairs
            top_pairs = [(pair[0], pair[1], count) 
                        for pair, count in pair_counts.head(10).items()]
            
            return top_pairs
            
        except Exception as e:
            logger.error(f"Error identifying cross-selling opportunities: {str(e)}")
            return []
    
    def analyze_customer_segments(self) -> Dict[str, Dict]:
        """
        Analyze customer segments based on RFM
        """
        try:
            # Calculate RFM metrics
            now = self.sales_data['date'].max()
            
            rfm = self.sales_data.groupby('customer_id').agg({
                'date': lambda x: (now - x.max()).days,  # Recency
                'order_id': 'count',  # Frequency
                'amount': 'sum'  # Monetary
            })
            
            # Rename columns
            rfm.columns = ['recency', 'frequency', 'monetary']
            
            # Create segments
            rfm['segment'] = 'Standard'
            rfm.loc[rfm['monetary'] > rfm['monetary'].quantile(0.75), 'segment'] = 'High Value'
            rfm.loc[rfm['frequency'] > rfm['frequency'].quantile(0.75), 'segment'] = 'Loyal'
            rfm.loc[rfm['recency'] > rfm['recency'].quantile(0.75), 'segment'] = 'At Risk'
            
            # Calculate segment metrics
            segment_metrics = rfm.groupby('segment').agg({
                'recency': 'mean',
                'frequency': 'mean',
                'monetary': 'mean'
            }).round(2)
            
            return segment_metrics.to_dict('index')
            
        except Exception as e:
            logger.error(f"Error analyzing customer segments: {str(e)}")
            return {}
    
    def generate_opportunities_report(self) -> None:
        """
        Generate a comprehensive business opportunities report
        """
        try:
            # Get analysis results
            category_metrics = self.analyze_product_categories()
            regional_metrics = self.analyze_regional_performance()
            cross_sell_opportunities = self.identify_cross_selling_opportunities()
            segment_metrics = self.analyze_customer_segments()
            
            # Create report content
            report_content = """# Business Opportunities Analysis Report

## 1. High-Growth Product Categories

### Top Growing Categories:
{}

### Recommendations:
- Increase inventory for high-growth categories
- Launch marketing campaigns for top performers
- Consider new product lines in growing categories

## 2. Regional Performance Analysis

### Key Regional Insights:
{}

### Recommendations:
- Focus marketing in high-performing regions
- Investigate underperforming regions
- Develop region-specific promotions

## 3. Cross-Selling Opportunities

### Top Product Pairs:
{}

### Recommendations:
- Create product bundles
- Implement "Frequently Bought Together" suggestions
- Develop targeted cross-sell campaigns

## 4. Customer Segment Analysis

### Segment Insights:
{}

### Recommendations:
- Develop segment-specific marketing campaigns
- Create loyalty programs for high-value customers
- Implement win-back campaigns for at-risk customers

## 5. Key Business Opportunities

1. Product Portfolio Expansion
   - Focus on high-growth categories
   - Introduce complementary products
   - Consider private label opportunities

2. Regional Growth
   - Expand in high-performing regions
   - Address challenges in underperforming areas
   - Develop location-based marketing strategies

3. Customer Engagement
   - Implement personalized marketing
   - Launch loyalty program
   - Develop retention strategies

## Next Steps

1. Immediate Actions (Next 30 Days):
   - Launch top product bundles
   - Implement segment-specific promotions
   - Start loyalty program development

2. Medium-term Actions (60-90 Days):
   - Expand inventory in growth categories
   - Develop regional marketing campaigns
   - Launch customer win-back program

3. Long-term Initiatives (90+ Days):
   - Evaluate new market opportunities
   - Develop private label products
   - Build advanced personalization capabilities
""".format(
    self._format_category_metrics(category_metrics),
    self._format_regional_metrics(regional_metrics),
    self._format_cross_sell_opportunities(cross_sell_opportunities),
    self._format_segment_metrics(segment_metrics)
)
            
            # Save report
            with open('business_opportunities_report.md', 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            logger.info("Business opportunities report generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating opportunities report: {str(e)}")
    
    def _format_category_metrics(self, metrics: Dict) -> str:
        """Format category metrics for the report"""
        return "\n".join([
            f"- {cat}:\n"
            f"  - Revenue: ₹{stats['total_revenue']:,.2f}\n"
            f"  - Growth Rate: {stats['growth_rate']*100:.1f}%\n"
            f"  - Order Count: {stats['order_count']:,.0f}"
            for cat, stats in metrics.items()
        ])
    
    def _format_regional_metrics(self, metrics: Dict) -> str:
        """Format regional metrics for the report"""
        return "\n".join([
            f"- {region}:\n"
            f"  - Revenue: ₹{stats['total_revenue']:,.2f}\n"
            f"  - Growth Rate: {stats['growth_rate']*100:.1f}%\n"
            f"  - Unique Customers: {stats['unique_customers']:,.0f}"
            for region, stats in metrics.items()
        ])
    
    def _format_cross_sell_opportunities(self, opportunities: List[Tuple]) -> str:
        """Format cross-sell opportunities for the report"""
        return "\n".join([
            f"- {prod1} + {prod2}: {count} times purchased together"
            for prod1, prod2, count in opportunities
        ])
    
    def _format_segment_metrics(self, metrics: Dict) -> str:
        """Format segment metrics for the report"""
        return "\n".join([
            f"- {segment}:\n"
            f"  - Average Spend: ₹{stats['monetary']:,.2f}\n"
            f"  - Purchase Frequency: {stats['frequency']:.1f} orders\n"
            f"  - Days Since Last Purchase: {stats['recency']:.0f}"
            for segment, stats in metrics.items()
        ])

def main():
    """
    Main function to run business opportunity analysis
    """
    try:
        # Load data
        sales_data = pd.read_csv('daily_sales_processed.csv', parse_dates=['date'])
        forecast_data = pd.read_csv('forecast_data.csv', parse_dates=['date'])
        
        # Create analyzer
        analyzer = BusinessOpportunityAnalyzer(sales_data, forecast_data)
        
        # Generate report
        analyzer.generate_opportunities_report()
        
        logger.info("Business opportunity analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 