import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_forecast_data():
    """
    Load forecast data from the prediction files
    """
    try:
        # Load historical data
        historical_data = pd.read_csv('daily_sales_processed.csv')
        historical_data['date'] = pd.to_datetime(historical_data.iloc[:, 0])
        historical_data.set_index('date', inplace=True)
        
        # Load forecast data
        forecast_data = pd.read_csv('forecast_data.csv', parse_dates=['date'], index_col='date')
        
        return historical_data, forecast_data
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None, None

def prepare_export_data(historical_data, forecast_data):
    """
    Prepare data for export
    """
    try:
        # Create export dataframe
        export_data = pd.DataFrame({
            'Date': forecast_data.index,
            'Predicted_Sales': forecast_data['predicted_sales'],
            'Lower_CI': forecast_data['lower_ci'],
            'Upper_CI': forecast_data['upper_ci'],
            'Is_Festival': False,  # Default value
            'Is_Holiday': False,   # Default value
            'Day_Of_Week': forecast_data.index.dayofweek,
            'Month': forecast_data.index.month
        })
        
        # Mark festivals and holidays
        festivals = {
            'Diwali': '2024-11-01',
            'Dussehra': '2024-10-12',
            'Christmas': '2024-12-25',
            'New_Year': '2024-01-01'
        }
        
        for festival, date in festivals.items():
            festival_date = pd.to_datetime(date)
            # Mark 5 days around the festival
            for i in range(-2, 3):
                mark_date = festival_date + timedelta(days=i)
                if mark_date in export_data.index:
                    export_data.loc[mark_date, 'Is_Festival'] = True
        
        # Calculate additional metrics
        export_data['Growth_Rate'] = export_data['Predicted_Sales'].pct_change() * 100
        export_data['Prediction_Range'] = export_data['Upper_CI'] - export_data['Lower_CI']
        export_data['Confidence_Level'] = 95  # 95% confidence interval
        
        return export_data
    except Exception as e:
        logger.error(f"Error preparing export data: {str(e)}")
        return None

def export_forecast_data(export_data, filename='sales_forecast_detailed.csv'):
    """
    Export forecast data to CSV
    """
    try:
        # Add metadata
        export_data.attrs['forecast_generated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        export_data.attrs['model_type'] = 'SARIMA'
        export_data.attrs['confidence_level'] = '95%'
        
        # Export to CSV
        export_data.to_csv(filename)
        logger.info(f"Forecast data exported to {filename}")
        
        # Create a data dictionary
        data_dictionary = pd.DataFrame({
            'Column_Name': export_data.columns,
            'Description': [
                'Date of forecast',
                'Predicted sales value',
                'Lower bound of confidence interval',
                'Upper bound of confidence interval',
                'Whether date is during a festival period',
                'Whether date is a holiday',
                'Day of week (0=Monday, 6=Sunday)',
                'Month number',
                'Percentage change from previous day',
                'Range of prediction interval',
                'Confidence level of prediction'
            ],
            'Data_Type': export_data.dtypes.values
        })
        
        # Export data dictionary
        data_dictionary.to_csv('forecast_data_dictionary.csv', index=False)
        logger.info("Data dictionary exported")
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")

def main():
    """
    Main function to export forecast data
    """
    try:
        # Load data
        historical_data, forecast_data = load_forecast_data()
        if historical_data is None or forecast_data is None:
            logger.error("Failed to load data")
            return
        
        # Prepare export data
        export_data = prepare_export_data(historical_data, forecast_data)
        if export_data is None:
            logger.error("Failed to prepare export data")
            return
        
        # Export data
        export_forecast_data(export_data)
        
        logger.info("Forecast data export completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 