import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

# --- Configuration ---
# INPUT_FILE_PATH = Path("file-data.txt")
# OUTPUT_CSV_FILE = Path("file-res.csv") # Set to None to disable CSV output
# VERBOSE_LOGGING = False # Set to True for more print statements during processing

def process_file_change_log(file_path: Path, verbose: bool = False):
    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing file change log: {file_path}...")

    extracted_records = []
    line_num = 0
    parsing_errors = 0
    processed_lines = 0

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    data_entry = json.loads(line)
                    dev_id = data_entry.get("DevID")
                    timestamp = data_entry.get("TimeStamp")

                    if not dev_id: continue
                    if timestamp is None: continue

                    extracted_records.append({
                        'DevID': dev_id,
                        'EpochTimeStamp': int(timestamp),

                    })
                    processed_lines += 1

                except Exception as e:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to error: {e}")
                    continue

    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}")
        return None

    # print(f"\n--- File Processing Summary ---")
    # print(f" Lines processed: {line_num}")
    if parsing_errors > 0: print(f" Lines skipped (errors/invalid data): {parsing_errors} for file: {file_path}")
    # print(f" Valid records extracted: {len(extracted_records)}")
    # print("-" * 30)

    if not extracted_records:
        print("No valid file change records extracted from the file: {file_path}.")
        return None

    # --- Convert to Pandas DataFrame ---
    # print("Converting extracted data to DataFrame...")
    df = pd.DataFrame(extracted_records)
    df['TimeStamp'] = pd.to_datetime(df['EpochTimeStamp'], unit='s', errors='coerce')
    df.dropna(subset=['TimeStamp', 'DevID'], inplace=True) # Drop if timestamp conversion failed

    if df.empty:
        print("DataFrame is empty after initial processing for file: {file_path}.")
        return None

    # print("Identifying baseline (records with earliest timestamp)...")
    min_timestamp_epoch = df['EpochTimeStamp'].min()
    # min_timestamp_dt = pd.to_datetime(min_timestamp_epoch, unit='s')
    # print(f"Earliest timestamp (baseline): {min_timestamp_epoch} ({min_timestamp_dt})")

    df_changes = df[df['EpochTimeStamp'] > min_timestamp_epoch].copy() # Use .copy() to avoid SettingWithCopyWarning

    if df_changes.empty:
        print("No file changes detected after the initial baseline for file: {file_path}.")
        dev_ids = df['DevID'].unique()
        zero_summary = pd.DataFrame({
            'DevID': dev_ids,
            'TotalFilesChanged': 0,
            'AvgFilesChangedPerMin': 0.0,
            'PeakFilesChangedPerMin': 0,
            'ChangeTimeSpanMinutes': 0.0
        })
        return zero_summary


    # print(f"Found {len(df_changes)} change records after baseline.")
    if verbose:
        print("\n--- Change Records DataFrame Head ---")
        print(df_changes.head())

    # --- Calculate Statistics per DevID for Changes ---
    # print("Calculating statistics per DevID...")
    all_dev_summaries = []

    for dev_id, group_df in df_changes.groupby('DevID'):
        if verbose: print(f"  Processing DevID: {dev_id} ({len(group_df)} changes)")

        # W: Total Files Changed
        total_changes_w = len(group_df)

        # --- Peak Calculation ---
        # Group changes by 1-minute intervals and count
        group_df.set_index('TimeStamp', inplace=True)
        per_minute_counts = group_df.groupby(pd.Grouper(freq='1min')).size()
        group_df.reset_index(inplace=True) # Reset index if needed later

        peak_per_min = per_minute_counts.max() if not per_minute_counts.empty else 0


        first_change_time = group_df['TimeStamp'].min()
        last_change_time = group_df['TimeStamp'].max()
        duration_seconds = (last_change_time - first_change_time).total_seconds()


        duration_minutes = max(1.0, (duration_seconds / 60.0))

        avg_per_min_x = total_changes_w / duration_minutes

        all_dev_summaries.append({
            'DevID': dev_id,
            'TotalFilesChanged': total_changes_w,
            'AvgFilesChangedPerMin': avg_per_min_x,
            'PeakFilesChangedPerMin': peak_per_min,
            'ChangeTimeSpanMinutes': duration_minutes
        })

    final_summary_df = pd.DataFrame(all_dev_summaries)

    # print("Calculations complete.")

    return final_summary_df

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Parse and process the (json-like) data collected from the discern project to display the summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file change log (file-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='file-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_file_change_log(args.input_file, verbose=args.verbose)

    # final_summary = process_file_change_log(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)

    if final_summary is not None and not final_summary.empty:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:.2f}'.format)

        # print(final_summary)

        if args.output:
            try:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                final_summary.to_csv(args.output, index=False)
                # print(f"\nSummary saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}.")
    else:
        print("\nNo file change summary statistics generated.")