import pandas as pd
import json
import os

# Define the file path (assumes script is run from the project root)
DATA_PATH = "data/orders_daily.csv"

def detect_anomalies(file_path):
    # 1. Load the CSV
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": f"Dataset not found at {file_path}. Run from the root directory."}
    
    # Ensure order_date is a datetime object for proper chronological sorting
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Group by region and sort chronologically by order_date
    df = df.sort_values(by=['region', 'order_date']).reset_index(drop=True)
    
    # 2. Calculate a 30-day rolling mean and standard deviation per region
    # Using min_periods=1 so we don't return nulls for the first 29 days
    df['rolling_mean'] = df.groupby('region')['revenue'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    df['rolling_std'] = df.groupby('region')['revenue'].transform(
        lambda x: x.rolling(window=30, min_periods=1).std()
    )
    
    # 3. Calculate the Z-score
    # Formula: Z = (Revenue - Rolling Mean) / Rolling StdDev
    df['z_score'] = (df['revenue'] - df['rolling_mean']) / df['rolling_std']
    
    # 4. Calculate the Absolute Business Impact
    # Formula: Impact = Rolling Mean - Revenue
    df['abs_impact'] = df['rolling_mean'] - df['revenue']
    
    # 5. The Two-Tier Filter
    # Flag ONLY IF Z-score < -1.0 AND Absolute Impact > 100
    # will change -1.0 to -2.0 and 100 to 10000 for real world scenarios
    anomalies = df[(df['z_score'] < -1.0) & (df['abs_impact'] > 100)].copy()

    # --- DEBUG BLOCK START ---
    print("--- DEBUG: Last 5 days of Northeast math ---")
    debug_df = df[df['region'] == 'Northeast'][['order_date', 'revenue', 'rolling_mean', 'z_score', 'abs_impact']].tail(5)
    print(debug_df.to_string(index=False))
    print("--------------------------------------------\n")
# --- DEBUG BLOCK END ---
    
    # Format the date back to string for clean JSON serialization
    anomalies['order_date'] = anomalies['order_date'].dt.strftime('%Y-%m-%d')
    
    # Replace any NaN values (e.g., standard deviation on day 1) with None for JSON compliance
    anomalies = anomalies.where(pd.notnull(anomalies), None)
    
    # Convert the filtered dataframe to a list of dictionaries
    anomalies_json = anomalies.to_dict(orient='records')
    
    return anomalies_json

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"Error: Could not find the dataset at {DATA_PATH}.")
        print("Please ensure your terminal is in the 'BusinessIntelligence' root folder.")
    else:
        # Run the detection engine
        flagged_anomalies = detect_anomalies(DATA_PATH)
        
        # Print the flagged anomalies to the terminal as clean JSON
        print(json.dumps(flagged_anomalies, indent=4))