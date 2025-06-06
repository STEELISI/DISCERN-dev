import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

# INPUT_FILE_PATH = Path("cpu-load-data.txt")
# OUTPUT_CSV_FILE = Path("cpu-res.csv")
# VERBOSE_LOGGING = False


def process_cpu_load_file_time_weighted(file_path: Path, verbose: bool = False):

    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing CPU load file (time-weighted): {file_path}...")

    extracted_data = []
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
                    load_list = data_entry.get("Load")
                    timestamp = data_entry.get("TimeStamp")

                    if not dev_id: continue
                    if timestamp is None: continue # Skip if no timestamp
                    if not isinstance(load_list, list) or not load_list: continue

                    cpu_load_value = load_list[0]
                    if not isinstance(cpu_load_value, (int, float)): continue

                    extracted_data.append({
                        'DevID': dev_id,
                        'TimeStamp': int(timestamp),
                        'CpuLoad': float(cpu_load_value)
                    })
                    processed_lines += 1

                except Exception as e:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to error: {e}")
                    continue

    except Exception as e:
        print(f"An error occurred during file reading: {e}")
        return None

    if parsing_errors > 0: print(f" Lines skipped (errors/invalid data): {parsing_errors} at file: {file_path}")

    if not extracted_data:
        print("No valid CPU load data extracted from the file: {file_path}.")
        return None

    # print("Converting extracted data to DataFrame...")
    df = pd.DataFrame(extracted_data)

    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s', errors='coerce')
    df['CpuLoad'] = pd.to_numeric(df['CpuLoad'], errors='coerce')

    df.dropna(subset=['TimeStamp', 'DevID', 'CpuLoad'], inplace=True)

    if df.empty:
        print("DataFrame is empty after initial processing and cleaning for file: {file_path}.")
        return None

    # print("Sorting data by DevID and TimeStamp...")
    df.sort_values(by=['DevID', 'TimeStamp'], inplace=True)

    if verbose:
        print("\n--- Processed & Sorted DataFrame Head ---")
        print(df.head())

    df['NextTimeStamp'] = df.groupby('DevID')['TimeStamp'].shift(-1)
    df['Duration'] = (df['NextTimeStamp'] - df['TimeStamp']).dt.total_seconds()
    df['LoadTimesDuration'] = df['CpuLoad'] * df['Duration'].fillna(0)

    if verbose:
        print("\n--- DataFrame with Durations Head ---")
        print(df[['DevID', 'TimeStamp', 'CpuLoad', 'NextTimeStamp', 'Duration', 'LoadTimesDuration']].head())

    # Aggregate results per DevID
    summary = df.groupby('DevID').agg(
        SumLoadTimesDuration=('LoadTimesDuration', 'sum'),
        TotalDurationSeconds=('Duration', 'sum'),
        MaxCpuUsage=('CpuLoad', 'max'),
        DataPoints=('CpuLoad', 'count')
    ).reset_index()

    summary['AvgCpuUsage'] = summary.apply(
        lambda row: row['SumLoadTimesDuration'] / row['TotalDurationSeconds']
                    if row['TotalDurationSeconds'] > 0 else 0.0,
        axis=1
    )

    summary = summary[[
        'DevID', 'AvgCpuUsage', 'MaxCpuUsage',
        'DataPoints', 'TotalDurationSeconds'
    ]]

    # print("Calculations complete.")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse and process the (json-like) data collected from the discern project to display the summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file change log (cpu-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='cpu-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_cpu_load_file_time_weighted(args.input_file, verbose=args.verbose)
    
    # final_summary = process_cpu_load_file_time_weighted(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)

    if final_summary is not None and not final_summary.empty:
        # print("\n--- CPU Usage Summary Per DevID ---")
        # Configure pandas display options
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
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}")
    else:
        print("\nNo CPU usage summary statistics generated.")
