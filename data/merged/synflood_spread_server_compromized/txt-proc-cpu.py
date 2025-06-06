import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

# INPUT_FILE_PATH = Path("proc-cpu-data.txt")
# OUTPUT_CSV_FILE = Path("proc_cpu_summary.csv")
# VERBOSE_LOGGING = False

def process_program_cpu_usage(file_path: Path, verbose: bool = False):

    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing program CPU usage file: {file_path}...")

    extracted_records = []
    line_num = 0
    # parsing_errors = 0 # Not used
    # processed_lines = 0 # Not used

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    data_entry = json.loads(line)
                    timestamp = data_entry.get("TimeStamp")
                    name = data_entry.get("Name")
                    cpu_percent = data_entry.get("Cpu")

                    if timestamp is None or name is None or cpu_percent is None:
                        if verbose: print(f"Warning: Skipping line {line_num}. Missing TimeStamp, Name, or Cpu.")
                        continue

                    extracted_records.append({
                        'TimeStamp': int(timestamp),
                        'Name': name,
                        'CpuPercent': float(cpu_percent)
                    })
                    # processed_lines += 1

                except Exception as e:
                    # parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to error: {e}")
                    continue

    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}")
        return None

    if not extracted_records:
        print(f"No valid process CPU records extracted for file: {file_path}")
        return None

    df = pd.DataFrame(extracted_records)
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s', errors='coerce')
    df['CpuPercent'] = pd.to_numeric(df['CpuPercent'], errors='coerce')
    df.dropna(subset=['TimeStamp', 'Name', 'CpuPercent'], inplace=True)

    if df.empty:
        print(f"DataFrame is empty after initial processing and cleaning for file: {file_path}.")
        return None

    # --- Calculate Total Observation Duration ---
    distinct_timestamps = df['TimeStamp'].sort_values().unique()

    if len(distinct_timestamps) < 2:
         print(f"Warning: Need at least two distinct measurement timestamps to calculate time-weighted average for file: {file_path}.")
         # Early return removed to allow flow-through calculations resulting in 0 duration and NaN averages.
    
    # min_ts and max_ts calculation will proceed. If len(distinct_timestamps) < 2, min_ts will equal max_ts.
    min_ts = pd.to_datetime(distinct_timestamps.min()) if len(distinct_timestamps) > 0 else pd.NaT
    max_ts = pd.to_datetime(distinct_timestamps.max()) if len(distinct_timestamps) > 0 else pd.NaT

    total_duration_seconds = (max_ts - min_ts).total_seconds() if pd.notna(min_ts) and pd.notna(max_ts) else 0.0
    
    # print(f"Total observation time span: {total_duration_seconds:.2f} seconds (from {min_ts} to {max_ts})")

    if total_duration_seconds <= 0: # This will also be true if len(distinct_timestamps) < 2
        print(f"Warning: Total observation duration is {total_duration_seconds:.2f} seconds. Meaningful time-weighted average might not be calculable (e.g., will be NaN) for file: {file_path}.")
        # Early return removed. Calculations will proceed with 0 duration where appropriate.

    ts_map = {pd.Timestamp(t): pd.Timestamp(next_t) for t, next_t in zip(distinct_timestamps[:-1], distinct_timestamps[1:])}
    df['NextOverallTimeStamp'] = df['TimeStamp'].map(ts_map)
    df['Duration'] = (df['NextOverallTimeStamp'] - df['TimeStamp']).dt.total_seconds()
    df.fillna({'Duration': 0}, inplace=True) # For last timestamps in series, or if ts_map is empty
    df['Duration'] = df['Duration'].clip(lower=0)


    df['CpuWeighted'] = df['CpuPercent'] * df['Duration']

    if verbose:
        print("\n--- DataFrame with Corrected Durations and Weights Head ---")
        # Sort by Name first for grouped view if multiple processes share timestamps
        df_sorted_verbose = df.sort_values(by=['Name', 'TimeStamp'])
        print(df_sorted_verbose[['Name', 'TimeStamp', 'CpuPercent', 'NextOverallTimeStamp', 'Duration', 'CpuWeighted']].head(10))

    # --- Aggregation for individual processes ---
    summary = df.groupby('Name').agg(
        TotalCpuWeighted=('CpuWeighted', 'sum'),
        MaxCpuUsage=('CpuPercent', 'max'),
        Duration=('Duration', 'sum'), # Sum of interval durations where the process was active
        DataPoints=('CpuPercent', 'count') # Number of measurements for the process
    ).reset_index()

    # Calculate AvgCpuPercent, handling division by zero if total Duration for a process is 0
    with np.errstate(divide='ignore', invalid='ignore'):
        summary['AvgCpuPercent'] = summary['TotalCpuWeighted'] / summary['Duration']
    summary['AvgCpuPercent'] = np.where(summary['Duration'] == 0, np.nan, summary['AvgCpuPercent'])
    
    summary = summary.sort_values(by='TotalCpuWeighted',ascending=False) # Keep sorting by weight before dropping it

    summary = summary[[
        'Name','Duration', 'AvgCpuPercent', 'MaxCpuUsage', 'DataPoints'
    ]]

    # --- Add Overall System Record (excluding discern-file-so timestamps) ---
    overall_name = "OverallSystemRecord"
    overall_duration_val = 0.0
    overall_avg_cpu_val = np.nan
    overall_max_cpu_val = np.nan
    overall_points_val = 0

    # df must have 'Duration' column at this point.
    discern_file_so_timestamps = df[df['Name'] == 'discern-file-so']['TimeStamp'].unique()
    df_overall = df[~df['TimeStamp'].isin(discern_file_so_timestamps)].copy()

    if not df_overall.empty:
        # Group by timestamp to sum CPU from all other processes, and get the interval duration
        system_metrics_at_ts = df_overall.groupby('TimeStamp').agg(
            TotalSystemCpuThisInstant=('CpuPercent', 'sum'),
            # Duration is the same for all entries at a given TimeStamp, as it's based on NextOverallTimeStamp
            IntervalDuration=('Duration', 'first')
        ).reset_index()

        if not system_metrics_at_ts.empty:
            system_metrics_at_ts['SystemCpuWeighted'] = system_metrics_at_ts['TotalSystemCpuThisInstant'] * system_metrics_at_ts['IntervalDuration']

            overall_total_cpu_weighted_sum = system_metrics_at_ts['SystemCpuWeighted'].sum()
            sum_of_interval_durations = system_metrics_at_ts['IntervalDuration'].sum()

            if sum_of_interval_durations > 0:
                overall_avg_cpu_val = overall_total_cpu_weighted_sum / sum_of_interval_durations
            
            overall_max_cpu_val = system_metrics_at_ts['TotalSystemCpuThisInstant'].max()
            overall_duration_val = sum_of_interval_durations
            # DataPoints for overall: number of unique timestamp intervals with non-zero duration considered
            overall_points_val = int(system_metrics_at_ts[system_metrics_at_ts['IntervalDuration'] > 0]['TimeStamp'].nunique())
    
    overall_system_record_data = {
        'Name': overall_name,
        'Duration': overall_duration_val,
        'AvgCpuPercent': overall_avg_cpu_val,
        'MaxCpuUsage': overall_max_cpu_val,
        'DataPoints': overall_points_val
    }
    overall_system_df = pd.DataFrame([overall_system_record_data])
    summary = pd.concat([summary, overall_system_df], ignore_index=True)

    # print("Calculations complete.")
    return summary


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Parse and process (json-like) data collected from CPU monitoring to display summary statistics.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file (e.g., proc-cpu-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='proc_cpu_summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_program_cpu_usage(args.input_file, verbose=args.verbose)
    
    if final_summary is not None and not final_summary.empty:
        
        pd.set_option('display.max_rows', None) 
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:.3f}'.format)
        
        # Sort before printing to console
        final_summary_sorted_for_print = final_summary.sort_values(by='AvgCpuPercent', ascending=False, na_position='last')
        # print("\n--- Program CPU Usage Summary ---")
        # print(final_summary_sorted_for_print)

        if args.output:
            try:
                # Save the potentially unsorted (or as-calculated) summary to CSV
                final_summary.to_csv(args.output, index=False, float_format='%.3f')
                # print(f"\nSummary saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}")
    else:
        print(f"\nNo program CPU usage summary statistics generated for {args.input_file}.")