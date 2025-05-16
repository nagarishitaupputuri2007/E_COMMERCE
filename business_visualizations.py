import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BusinessVisualizer:
    def __init__(self, sales_data: pd.DataFrame, forecast_data: pd.DataFrame):
        self.sales_data = sales_data
        self.forecast_data = forecast_data
        
        # Set style
        plt.style.use('seaborn')
        
    def create_category_growth_chart(self) -> None:
        """
        Create visualization for category growth trends
        """
        try:
            # Calculate category growth
            category_growth = self.sales_data.pivot_table(
                index='category',
                columns=pd.Grouper(key='date', freq='M'),
                values='amount',
                aggfunc='sum'
            ).pct_change(axis=1).mean(axis=1)
            
            # Create bar chart
            plt.figure(figsize=(12, 6))
            category_growth.sort_values().plot(kind='barh')
            plt.title('Category Growth Rates')
            plt.xlabel('Growth Rate (%)')
            plt.ylabel('Category')
            plt.tight_layout()
            plt.savefig('category_growth.png')
            plt.close()
            
            logger.info("Category growth chart created successfully")
            
        except Exception as e:
            logger.error(f"Error creating category growth chart: {str(e)}")
    
    def create_regional_performance_map(self) -> None:
        """
        Create visualization for regional performance
        """
        try:
            # Calculate regional metrics
            regional_metrics = self.sales_data.groupby('region').agg({
                'amount': 'sum',
                'customer_id': 'nunique'
            })
            
            # Create choropleth map using plotly
            fig = px.choropleth_mapbox(
                regional_metrics.reset_index(),
                locations='region',
                color='amount',
                hover_name='region',
                hover_data=['customer_id'],
                title='Regional Sales Performance',
                mapbox_style="carto-positron"
            )
            
            fig.write_html('regional_performance_map.html')
            logger.info("Regional performance map created successfully")
            
        except Exception as e:
            logger.error(f"Error creating regional performance map: {str(e)}")
    
    def create_customer_segment_analysis(self) -> None:
        """
        Create visualizations for customer segment analysis
        """
        try:
            # Calculate RFM metrics
            now = self.sales_data['date'].max()
            
            rfm = self.sales_data.groupby('customer_id').agg({
                'date': lambda x: (now - x.max()).days,
                'order_id': 'count',
                'amount': 'sum'
            })
            
            rfm.columns = ['recency', 'frequency', 'monetary']
            
            # Create segments
            rfm['segment'] = 'Standard'
            rfm.loc[rfm['monetary'] > rfm['monetary'].quantile(0.75), 'segment'] = 'High Value'
            rfm.loc[rfm['frequency'] > rfm['frequency'].quantile(0.75), 'segment'] = 'Loyal'
            rfm.loc[rfm['recency'] > rfm['recency'].quantile(0.75), 'segment'] = 'At Risk'
            
            # Create bubble chart
            fig = px.scatter(
                rfm,
                x='recency',
                y='frequency',
                size='monetary',
                color='segment',
                title='Customer Segments Analysis',
                labels={
                    'recency': 'Days Since Last Purchase',
                    'frequency': 'Number of Orders',
                    'monetary': 'Total Spend'
                }
            )
            
            fig.write_html('customer_segments.html')
            logger.info("Customer segment analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating customer segment analysis: {str(e)}")
    
    def create_cross_sell_network(self) -> None:
        """
        Create network visualization for product relationships
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
            pair_counts = pd.Series(product_pairs).value_counts().head(20)
            
            # Create network graph
            fig = go.Figure()
            
            # Add nodes
            products = list(set([p for pair in pair_counts.index for p in pair]))
            
            for i, product in enumerate(products):
                fig.add_trace(go.Scatter(
                    x=[np.cos(2*np.pi*i/len(products))],
                    y=[np.sin(2*np.pi*i/len(products))],
                    mode='markers+text',
                    name=product,
                    text=[product],
                    marker=dict(size=20)
                ))
            
            # Add edges
            for (prod1, prod2), count in pair_counts.items():
                i1 = products.index(prod1)
                i2 = products.index(prod2)
                
                fig.add_trace(go.Scatter(
                    x=[np.cos(2*np.pi*i1/len(products)), np.cos(2*np.pi*i2/len(products))],
                    y=[np.sin(2*np.pi*i1/len(products)), np.sin(2*np.pi*i2/len(products))],
                    mode='lines',
                    line=dict(width=count/pair_counts.max()*5),
                    showlegend=False
                ))
            
            fig.update_layout(
                title='Product Cross-Selling Network',
                showlegend=True,
                hovermode='closest'
            )
            
            fig.write_html('cross_sell_network.html')
            logger.info("Cross-sell network visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating cross-sell network: {str(e)}")
    
    def create_all_visualizations(self) -> None:
        """
        Create all business opportunity visualizations
        """
        try:
            self.create_category_growth_chart()
            self.create_regional_performance_map()
            self.create_customer_segment_analysis()
            self.create_cross_sell_network()
            
            logger.info("All visualizations created successfully!")
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")

def main():
    """
    Main function to create business visualizations
    """
    try:
        # Load data
        sales_data = pd.read_csv('daily_sales_processed.csv', parse_dates=['date'])
        forecast_data = pd.read_csv('forecast_data.csv', parse_dates=['date'])
        
        # Create visualizer
        visualizer = BusinessVisualizer(sales_data, forecast_data)
        
        # Generate all visualizations
        visualizer.create_all_visualizations()
        
        logger.info("Business visualization process completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 