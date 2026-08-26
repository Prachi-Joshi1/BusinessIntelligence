import pandas as pd
import json
import os

def analyze_drivers(file_path, target_region, target_date):
    """
    Deterministically calculates the Volume vs. Price contribution 
    to a top-line revenue anomaly.
    """
    # 1. Load the dataset
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}. Run from root directory."}
        
    df = pd.read_csv(file_path)
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # 2. Filter for the target region
    df_region = df[df['region'] == target_region].sort_values('order_date')
    
    # 3. Calculate Baseline: 30 days prior to target date
    target_dt = pd.to_datetime(target_date)
    start_dt = target_dt - pd.Timedelta(days=30)
    
    baseline_mask = (df_region['order_date'] >= start_dt) & (df_region['order_date'] < target_dt)
    baseline_data = df_region[baseline_mask]
    
    if baseline_data.empty:
        return {"error": "Not enough baseline data for the prior 30 days."}
        
    # Baseline Averages
    baseline_revenue = baseline_data['revenue'].mean()
    baseline_units = baseline_data['units'].mean()
    baseline_aup = baseline_revenue / baseline_units  # Baseline Average Unit Price
    
    # 4. Calculate Actuals: For the specific target date
    actual_mask = df_region['order_date'] == target_dt
    actual_data = df_region[actual_mask]
    
    if actual_data.empty:
        return {"error": f"No data found for date {target_date}"}
        
    actual_revenue = actual_data['revenue'].values[0]
    actual_units = actual_data['units'].values[0]
    actual_aup = actual_revenue / actual_units        # Actual Average Unit Price
    
    # 5. Calculate Variance (The Financial Math)
    total_variance = actual_revenue - baseline_revenue
    
    # Volume Impact = (Actual Units - Baseline Units) * Baseline AUP
    volume_impact = (actual_units - baseline_units) * baseline_aup
    
    # Price Impact = (Actual AUP - Baseline AUP) * Actual Units
    price_impact = (actual_aup - baseline_aup) * actual_units
    
    # 6. Rank Drivers by Absolute Variance
    drivers = [
        {"driver": "Volume Impact (Units/Traffic)", "impact_value": volume_impact},
        {"driver": "Price Impact (Discounts/AUP)", "impact_value": price_impact}
    ]
    
    # Sort descending by absolute impact
    drivers.sort(key=lambda x: abs(x['impact_value']), reverse=True)
    
    # Calculate percentage contribution
    total_abs_variance = sum(abs(d['impact_value']) for d in drivers)
    
    for d in drivers:
        d['contribution_percentage'] = round((abs(d['impact_value']) / total_abs_variance) * 100, 2)
        d['impact_value'] = round(d['impact_value'], 2)
        
    # 7. Format clean JSON output
    result = {
        "metric": "Revenue",
        "region": target_region,
        "target_date": target_date,
        "variance_from_baseline": round(total_variance, 2),
        "primary_driver": drivers[0]['driver'],
        "sub_drivers": drivers
    }
    
    return result

if __name__ == "__main__":
    # Define parameters from our previous anomaly engine catch
    FILE_PATH = "data/orders_daily.csv"
    TARGET_REGION = "Northeast"
    TARGET_DATE = "2026-08-23"
    
    # Run the math layer and output JSON
    analysis_payload = analyze_drivers(FILE_PATH, TARGET_REGION, TARGET_DATE)
    print(json.dumps(analysis_payload, indent=4))