import json
import pandas as pd
import os
from pathlib import Path

def extract_instagram_metrics(json_path: str) -> pd.DataFrame:
    # Load JSON file
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Navigate to edges list
    edges = data.get("data", {}).get("xdt_api__v1__clips__user__connection_v2", {}).get("edges", [])

    # Extract required fields
    extracted_data = []
    for edge in edges:
        media = edge.get("node", {}).get("media", {})
        extracted_data.append({
            "pk": media.get("pk"),
            "code": media.get("code"),
            "play_count": media.get("play_count"),
            "comment_count": media.get("comment_count"),
            "like_count": media.get("like_count"),
            "view_count": media.get("view_count")
        })

    # Create DataFrame
    df = pd.DataFrame(extracted_data)

    # Define CSV path in same folder
    csv_path = os.path.join(os.path.dirname(json_path), "scrapped_data.csv")
    df.to_csv(csv_path, index=False)

    return df

# Example usage
json_file_path = Path(__file__).resolve().parent.parent / "Sample_json_outputs" / "response_2.json"
df_result = extract_instagram_metrics(json_file_path)


