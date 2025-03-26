import pandas as pd
import json
import os

def extract_data(match_result):
    """
    Extracts scores, positions, and errors from the match result.
    
    Returns tuple of:
    - overall_score
    - part scores for J23101_B0030_combined, GFP, B0015
    - start positions for each part
    - end positions for each part
    - errors (if any)
    """
    data = json.loads(match_result)

    if not data or not isinstance(data, list):
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None

    result = data[0]  # Assume one result per sequence
    overall_score = result.get("score", 0)
    errors = result.get("errors")

    # Extract part scores and positions, default to 0 if missing
    part_scores = {"J23101_B0030_combined": 0, "GFP": 0, "B0015": 0}
    part_starts = {"J23101_B0030_combined": 0, "GFP": 0, "B0015": 0}
    part_ends = {"J23101_B0030_combined": 0, "GFP": 0, "B0015": 0}

    if "path" in result and result["path"]:
        for part in result["path"]:
            part_name = part.get("name", "")
            if part_name in part_scores:
                part_scores[part_name] = part.get("score", 0)
                part_starts[part_name] = part.get("start", 0)
                part_ends[part_name] = part.get("end", 0)

    return (
        overall_score, 
        part_scores["J23101_B0030_combined"], 
        part_scores["GFP"], 
        part_scores["B0015"],
        part_starts["J23101_B0030_combined"],
        part_starts["GFP"],
        part_starts["B0015"],
        part_ends["J23101_B0030_combined"],
        part_ends["GFP"],
        part_ends["B0015"],
        errors
    )

def store_match_results(results_json, parquet_file, similarity_threshold, overlap_tolerance):
    """
    Stores match function output in a Parquet file with additional parameters.
    If the file exists, appends the new data to it.
    
    :param results_json: JSON string from match function
    :param parquet_file: Path to save the output Parquet file
    :param similarity_threshold: Similarity threshold value
    :param overlap_tolerance: Overlap tolerance value
    :return: Number of records processed
    """
    try:
        # Parse JSON output
        data = json.loads(results_json)
        
        if not data:
            print("Warning: Empty results data")
            return 0

        # Extract required fields
        records = []
        for item in data:
            target = item.get("target", "UNKNOWN")  # Sequence ID
            reconstruct = item.get("reconstruct", "")  # Reconstruction pattern
            
            # Extract scores, positions and errors
            (
                overall_score, 
                part1_score, part2_score, part3_score,
                part1_start, part2_start, part3_start,
                part1_end, part2_end, part3_end,
                errors
            ) = extract_data(json.dumps([item]))
            
            records.append({
                "ID": target,
                "Reconstruction": reconstruct,
                "Overall_Score": overall_score,
                "J23101_B0030_Score": part1_score,
                "GFP_Score": part2_score,
                "B0015_Score": part3_score,
                "J23101_B0030_Start": part1_start,
                "GFP_Start": part2_start,
                "B0015_Start": part3_start,
                "J23101_B0030_End": part1_end,
                "GFP_End": part2_end,
                "B0015_End": part3_end,
                "Errors": str(errors) if errors is not None else None,
                "Similarity_Threshold": similarity_threshold,
                "Overlap_Tolerance": overlap_tolerance
            })

        # Convert new data to DataFrame
        new_df = pd.DataFrame(records)
        
        # Check if the file already exists
        if os.path.exists(parquet_file):
            try:
                # Read existing DataFrame
                existing_df = pd.read_parquet(parquet_file)
                
                # Concatenate the DataFrames
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Remove duplicates based on ID and parameters
                combined_df = combined_df.drop_duplicates(
                    subset=["ID", "Similarity_Threshold", "Overlap_Tolerance"], 
                    keep="last"
                )
                
                # Save the combined DataFrame
                combined_df.to_parquet(parquet_file, index=False)
                print(f"Added {len(new_df)} records to existing file {parquet_file}. Total records: {len(combined_df)}")
            except Exception as e:
                print(f"Error appending to existing file: {e}")
                print(f"Creating new file with current data only.")
                new_df.to_parquet(parquet_file, index=False)
        else:
            # File doesn't exist, create new
            new_df.to_parquet(parquet_file, index=False)
            print(f"Created new file {parquet_file} with {len(new_df)} records.")
        
        return len(new_df)
    
    except Exception as e:
        print(f"Error processing match results: {e}")
        return 0

# Example usage
if __name__ == "__main__":
    # Sample JSON from the provided format
    example_json = '''[
  {
    "target":"pb_gfp_99_sub_only_S_1_0",
    "reconstruct":"J23101_B0030_combined-GFP-B0015",
    "score":0.989034203871302,
    "path":[
      {
        "name":"J23101_B0030_combined",
        "score":1.0,
        "start":0,
        "length":50,
        "end":50
      },
      {
        "name":"GFP",
        "score":0.9674620390455532,
        "start":50,
        "length":922,
        "end":972
      },
      {
        "name":"B0015",
        "score":1.0,
        "start":972,
        "length":129,
        "end":1101
      }
    ],
    "errors":null
  }
]'''
    
    store_match_results(example_json, "test_results.parquet", 0.8, 0.2)