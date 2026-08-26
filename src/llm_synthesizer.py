import pandas as pd
from google import genai
import os
import json
from datetime import datetime, timedelta

def retrieve_context(file_path, target_region, target_date_str):
    """
    Loads unstructured_logs.csv and filters for logs in the target region 
    around the anomaly date window.
    """
    if not os.path.exists(file_path):
        return "No relevant text logs found: file does not exist."
        
    df = pd.read_csv(file_path)
    df['log_date'] = pd.to_datetime(df['log_date'])
    
    target_date = pd.to_datetime(target_date_str)
    start_date = target_date - timedelta(days=7)
    end_date = target_date + timedelta(days=2)  # Include trailing incident logs
    
    # Filter by region and date window
    mask = (df['region'] == target_region) & (df['log_date'] >= start_date) & (df['log_date'] <= end_date)
    filtered_logs = df[mask]
    
    if filtered_logs.empty:
        return "No relevant text logs found for this region and timeframe."
        
    log_strings = []
    for _, row in filtered_logs.iterrows():
        log_strings.append(f"[{row['log_date'].strftime('%Y-%m-%d')}] {row['log_type']}: {row['log_text']}")
        
    return "\n".join(log_strings)

def synthesize_insight():
    # 1. API Setup
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
    
    # 2. Deterministic Math Payload
    math_json = {
        "metric": "Revenue",
        "region": "Northeast",
        "target_date": "2026-08-24",
        "variance_from_baseline": -484.23,
        "primary_driver": "Volume Impact (Units/Traffic)",
        "sub_drivers": [
            {
                "driver": "Volume Impact (Units/Traffic)",
                "impact_value": -447.47,
                "contribution_percentage": 92.41
            },
            {
                "driver": "Price Impact (Discounts/AUP)",
                "impact_value": -36.76,
                "contribution_percentage": 7.59
            }
        ]
    }
    
    # 3. Context Retrieval
    logs_file_path = "data/unstructured_logs.csv"
    text_context = retrieve_context(logs_file_path, math_json["region"], math_json["target_date"])
    
    print("\n--- RETRIEVED LOG CONTEXT ---")
    print(text_context)
    print("-----------------------------\n")
    
    # 4. Prompt Construction
    prompt = f"""
    You are an expert Business Intelligence AI. Your task is to explain a business anomaly using ONLY the provided data.
    
    [STRICT GUARDRAIL - RULE 1]
    You must NEVER invent, estimate, or hallucinate financial numbers. You must rely strictly on the Provided Math JSON for all quantitative impacts.
    
    [ABSTENTION LOGIC - RULE 4]
    If the provided text logs do not logically explain the quantitative drop shown in the math, output exactly: 
    'Confidence: Low (32%). Abstaining from definitive recommendation. Please clarify: Was there an untracked regional campaign?'
    
    [PROVIDED MATH JSON]
    {json.dumps(math_json, indent=2)}
    
    [PROVIDED TEXT LOGS]
    {text_context}
    
    [YOUR TASK - RULE 2 & 3]
    Based on the logs and the math, generate TWO separate narratives for the following personas:
    
    1. Persona A (VP of Sales): Write a concise, 3-sentence executive summary focusing on macro impact and strategic actions. Followed by the structured recommendation.
    2. Persona B (Regional Operations Lead): Write a detailed technical breakdown focusing on logistics, ground-level actions, and incident logs. Followed by the structured recommendation.
    
    For BOTH personas, the final recommendation MUST be formatted as:
    Driver -> Controllable Lever -> Action -> Expected Impact -> Owner -> Confidence -> Monitoring Plan
    """
    
    # 5. Execution
    print("Sending deterministic math and contextual logs to Gemini...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        print("\n" + "="*50)
        print("🤖 AI SYNTHESIS RESULT:")
        print("="*50 + "\n")
        print(response.text)
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")

if __name__ == "__main__":
    synthesize_insight()