import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the directory structure for the final submission"""
    base_dir = Path("final_submission")
    
    # Create main directories
    directories = [
        "reports",
        "presentation",
        "datasets",
        "visualizations",
        "visualizations/sales",
        "visualizations/customer",
        "visualizations/geographic",
        "visualizations/product",
        "visualizations/interactive"
    ]
    
    for dir_name in directories:
        (base_dir / dir_name).mkdir(parents=True, exist_ok=True)

def copy_files():
    """Copy files to their respective directories"""
    # Define file mappings
    file_mappings = {
        # Reports
        "reports": [
            "final_business_report.md",
            "sales_forecast_final_report.md",
            "rfm_analysis_report.md",
            "geographic_analysis_report.md",
            "product_analysis_report.md",
            "time_series_analysis_report.md"
        ],
        
        # Presentation
        "presentation": [
            "business_analysis_presentation.pptx"
        ],
        
        # Datasets
        "datasets": [
            "ecommerce_data_cleaned.csv",
            "customer_segmentation_rfm.csv",
            "forecast_data.csv",
            "segment_statistics.csv",
            "daily_sales_processed.csv",
            "weekly_sales_processed.csv",
            "monthly_sales_processed.csv"
        ],
        
        # Visualizations - Sales
        "visualizations/sales": [
            "sales_trend.png",
            "monthly_sales_pattern.png",
            "seasonal_patterns.png",
            "sales_decomposition.png",
            "daily_sales_trend.png",
            "monthly_sales_trend.png"
        ],
        
        # Visualizations - Customer
        "visualizations/customer": [
            "customer_segments.png",
            "rfm_heatmap.png",
            "segment_revenue_distribution.png",
            "customer_segments_distribution.png"
        ],
        
        # Visualizations - Geographic
        "visualizations/geographic": [
            "regional_sales.png",
            "zone_revenue_distribution.png",
            "state_revenue_distribution.png",
            "zone_category_distribution.png"
        ],
        
        # Visualizations - Product
        "visualizations/product": [
            "category_revenue_distribution.png",
            "top_products_revenue.png",
            "category_sales_performance.png",
            "top_products_quantity.png",
            "top_products_trend.png"
        ],
        
        # Visualizations - Interactive
        "visualizations/interactive": [
            "interactive_forecast.html",
            "rfm_3d_scatter.html",
            "weekly_sales_trend.html"
        ]
    }
    
    base_dir = Path("final_submission")
    
    # Copy files to their respective directories
    for target_dir, files in file_mappings.items():
        for file_name in files:
            source = Path(file_name)
            destination = base_dir / target_dir / file_name
            
            if source.exists():
                shutil.copy2(source, destination)
                print(f"Copied {file_name} to {target_dir}")
            else:
                print(f"Warning: {file_name} not found")

def convert_markdown_to_pdf():
    """Convert markdown files to PDF format"""
    # This is a placeholder - in a real implementation, you would use a library
    # like mdpdf or pandoc to convert markdown files to PDF
    print("Converting markdown files to PDF...")
    # Implementation would go here

def create_submission_zip():
    """Create a ZIP file of the final submission"""
    shutil.make_archive(
        "final_submission_package",
        "zip",
        "final_submission"
    )
    print("Created final_submission_package.zip")

def main():
    """Main function to organize the submission"""
    print("Organizing final submission...")
    
    # Create directory structure
    create_directory_structure()
    
    # Copy files to appropriate directories
    copy_files()
    
    # Convert markdown files to PDF
    convert_markdown_to_pdf()
    
    # Create final ZIP package
    create_submission_zip()
    
    print("Submission organization complete!")

if __name__ == "__main__":
    main() 