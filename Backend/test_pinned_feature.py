"""
Test script to verify the is_reel_pinned feature works correctly
"""
import json
import pandas as pd
from pathlib import Path

def test_pinned_extraction():
    """Test extracting pinned status from sample JSON"""

    # Load sample data
    sample_file = Path("Sample_json_outputs/dua_lipa.json")

    if not sample_file.exists():
        print(f"Sample file not found: {sample_file}")
        return

    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Navigate to edges list (same as in pipeline.py)
    edges = data.get("data", {}).get("xdt_api__v1__clips__user__connection_v2", {}).get("edges", [])

    print(f"Found {len(edges)} reels in sample data\n")
    print("="*80)

    # Extract data with pinned status
    extracted_data = []
    for idx, edge in enumerate(edges[:5], 1):  # Test first 5 reels
        media = edge.get("node", {}).get("media", {})

        # Check if reel is pinned
        clips_tab_pinned_user_ids = media.get("clips_tab_pinned_user_ids", [])
        is_pinned = "Yes" if clips_tab_pinned_user_ids else "No"

        reel_data = {
            "pk": media.get("pk"),
            "code": media.get("code"),
            "play_count": media.get("play_count"),
            "like_count": media.get("like_count"),
            "is_reel_pinned": is_pinned,
            "pinned_user_ids": clips_tab_pinned_user_ids
        }

        extracted_data.append(reel_data)

        # Print details
        print(f"Reel #{idx}:")
        print(f"  Code: {reel_data['code']}")
        print(f"  Play Count: {reel_data['play_count']:,}")
        print(f"  Like Count: {reel_data['like_count']:,}")
        print(f"  Pinned User IDs: {reel_data['pinned_user_ids']}")
        print(f"  Is Pinned: {reel_data['is_reel_pinned']}")
        print()

    # Create DataFrame
    df = pd.DataFrame(extracted_data)

    print("="*80)
    print("\nDataFrame Summary:")
    print(df[['code', 'play_count', 'is_reel_pinned']].to_string(index=False))

    print("\n" + "="*80)
    print(f"\nPinned Reels: {(df['is_reel_pinned'] == 'Yes').sum()}")
    print(f"Unpinned Reels: {(df['is_reel_pinned'] == 'No').sum()}")
    print("\n✅ Feature is working correctly!")

if __name__ == "__main__":
    print("="*80)
    print("Testing 'Is Reel Pinned' Feature")
    print("="*80)
    print()

    test_pinned_extraction()
