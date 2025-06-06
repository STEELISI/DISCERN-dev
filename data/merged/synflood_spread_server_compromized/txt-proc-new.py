import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

# INPUT_FILE_PATH = Path("proc-new-data.txt")
# OUTPUT_CSV_FILE = Path("proc_new_summary.csv")
# VERBOSE_LOGGING = False


def process_proc_creation_log(file_path: Path, verbose: bool = False):
    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing process creation log: {file_path}...")

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
                    if verbose: print(f"Warning: Skipping line {line_num} due to error: {e} for file: {file_path}.")
                    continue

    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}.")
        return None

    # print(f"\n--- File Processing Summary ---")
    # print(f" Lines processed: {line_num}")
    if parsing_errors > 0: print(f" Lines skipped (errors/invalid data): {parsing_errors} for file: {file_path}.")
    # print(f" Valid process creation records extracted: {len(extracted_records)}")
    # print("-" * 30)

    if not extracted_records:
        print("No valid process creation records extracted from the file.")
        return None


    # print("Converting extracted data to DataFrame...")
    df = pd.DataFrame(extracted_records)
    df['TimeStamp'] = pd.to_datetime(df['EpochTimeStamp'], unit='s', errors='coerce')
    df.dropna(subset=['TimeStamp', 'DevID'], inplace=True) # Drop if timestamp conversion failed

    if df.empty:
        print("DataFrame is empty after initial processing.")
        return None

    if verbose:
        print("\n--- Processed DataFrame Head ---")
        print(df.head())

    # --- Calculate Statistics per DevID ---
    # print("Calculating statistics per DevID...")
    all_dev_summaries = []

    for dev_id, group_df in df.groupby('DevID'):
        if verbose: print(f"  Processing DevID: {dev_id} ({len(group_df)} records)")

        # W: Total New Processes
        total_procs_w = len(group_df)

        # --- Peak Calculation (per 30s) ---
        # Group process creations by 30-second intervals and count
        # Need TimeStamp as index for Grouper
        group_df_indexed = group_df.set_index('TimeStamp')
        per_30s_counts = group_df_indexed.groupby(pd.Grouper(freq='30s')).size()
        # group_df.reset_index(inplace=True) # Reset index if needed later, not needed here

        peak_per_30s = per_30s_counts.max() if not per_30s_counts.empty else 0

        # --- Average Calculation (per 30s) ---
        if total_procs_w > 0:
            # Calculate time span of observations for this device
            first_proc_time = group_df['TimeStamp'].min()
            last_proc_time = group_df['TimeStamp'].max()
            duration_seconds = (last_proc_time - first_proc_time).total_seconds()

            # Calculate number of 30-second intervals in the duration
            # Ensure at least one interval even if duration is < 30s
            num_30s_intervals = max(1.0, duration_seconds / 30.0)

            avg_per_30s_x = total_procs_w / num_30s_intervals
        else:
            # Handle case where a DevID might somehow have 0 records after filtering
            avg_per_30s_x = 0.0
            num_30s_intervals = 0.0 # Represent duration as 0 intervals

        all_dev_summaries.append({
            'DevID': dev_id,
            'TotalNewProcs': total_procs_w,
            'AvgNewProcsPer30Sec': avg_per_30s_x,
            'PeakNewProcsPer30Sec': peak_per_30s,
            'TotalTime': duration_seconds if total_procs_w > 0 else 0 # Add duration context
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
        help="Path to the input file change log (proc-new-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='proc-new-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_proc_creation_log(args.input_file, verbose=args.verbose)
    
    # final_summary = process_proc_creation_log(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)

    if final_summary is not None and not final_summary.empty:
        # print("\n--- Process Creation Summary Per DevID ---")
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:.2f}'.format)

        # print(final_summary)

        if args.output:
            try:
                final_summary.to_csv(args.output, index=False)
                # print(f"\nSummary saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}.")
    else:
        print("\nNo process creation summary statistics generated.")