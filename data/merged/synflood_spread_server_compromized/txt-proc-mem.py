import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse


# INPUT_FILE_PATH = Path("proc-mem-data.txt")
# OUTPUT_CSV_FILE = Path("proc_mem_summary.csv")
# VERBOSE_LOGGING = False
SORT_BY_COLUMN = 'TimeWeightedAvgVmSizeMiB'

BYTES_TO_MIB = 1024 * 1024

def process_program_vmemory_usage(file_path: Path, verbose: bool = False):


    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing program memory usage file (Avg: VmSize, Peaks: VmPeak/VmHWM): {file_path}...")

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
                    timestamp = data_entry.get("TimeStamp")
                    name = data_entry.get("Name")
                    vm_size_str = data_entry.get("VmSize")
                    vm_peak_str = data_entry.get("VmPeak")
                    vm_hwm_str = data_entry.get("VmHWM")

                    if timestamp is None or name is None or vm_size_str is None \
                       or vm_peak_str is None or vm_hwm_str is None:
                        if verbose: print(f"Warning: Skipping line {line_num}. Missing required fields (TimeStamp, Name, VmSize, VmPeak, VmHWM) for file: {file_path}.")
                        continue

                    # Convert memory strings to integer bytes
                    vm_size_bytes = int(vm_size_str)
                    vm_peak_bytes = int(vm_peak_str)
                    vm_hwm_bytes = int(vm_hwm_str)

                    # Append valid data
                    extracted_records.append({
                        'EpochTimeStamp': int(timestamp),
                        'Name': name,
                        'VmSizeBytes': vm_size_bytes,
                        'VmPeakBytes': vm_peak_bytes,
                        'VmHwmBytes': vm_hwm_bytes
                    })
                    processed_lines += 1

                except (ValueError, TypeError) as e:
                     parsing_errors += 1
                     if verbose: print(f"Warning: Skipping line {line_num} due to numeric conversion error: {e} for file: {file_path}.")
                     continue
                except Exception as e:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to error: {e}for file: {file_path}.")
                    continue

    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}.")
        return None


    if parsing_errors > 0: print(f" Lines skipped (errors/invalid data): {parsing_errors} for file: {file_path}.")



    if not extracted_records:
        print("No valid process memory records extracted for file: {file_path}.")
        return None


    df = pd.DataFrame(extracted_records)
    df['TimeStamp'] = pd.to_datetime(df['EpochTimeStamp'], unit='s', errors='coerce')
    for col in ['VmSizeBytes', 'VmPeakBytes', 'VmHwmBytes']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['TimeStamp', 'Name', 'VmSizeBytes', 'VmPeakBytes', 'VmHwmBytes'], inplace=True)

    if df.empty:
        print("DataFrame is empty after initial processing and cleaning.")
        return None


    distinct_timestamps = df['TimeStamp'].sort_values().unique()

    if len(distinct_timestamps) < 2:
         print("Warning: Need >= 2 distinct timestamps for time-weighted average.")
        
         summary = df.groupby('Name').agg(
             MaxVmPeakBytes = ('VmPeakBytes', 'max'),
             MaxVmHwmBytes = ('VmHwmBytes', 'max')
             ).reset_index()
         summary['TimeWeightedAvgVmSizeBytes'] = np.nan
         # Convert max values to MiB
         summary['MaxVmPeakMiB'] = summary['MaxVmPeakBytes'].fillna(0) / BYTES_TO_MIB
         summary['MaxVmHwmMiB'] = summary['MaxVmHwmBytes'].fillna(0) / BYTES_TO_MIB
         summary['TimeWeightedAvgVmSizeMiB'] = np.nan
         return summary[['Name', 'TimeWeightedAvgVmSizeMiB', 'MaxVmPeakMiB', 'MaxVmHwmMiB']]
    else:
         min_ts = pd.to_datetime(distinct_timestamps.min())
         max_ts = pd.to_datetime(distinct_timestamps.max())

    total_duration_seconds = (max_ts - min_ts).total_seconds()
    # print(f"Total observation time span: {total_duration_seconds:.2f} seconds (from {min_ts} to {max_ts})")

    if total_duration_seconds <= 0:
        print("Warning: Total duration is zero or negative. Cannot calculate time-weighted average.")
        return None

    ts_map = {pd.Timestamp(t): pd.Timestamp(next_t) for t, next_t in zip(distinct_timestamps[:-1], distinct_timestamps[1:])}
    df['NextOverallTimeStamp'] = df['TimeStamp'].map(ts_map)


    # df['NextOverallTimeStamp'].fillna(max_ts, inplace=True)
    df.fillna({'NextOverallTimeStamp':max_ts}, inplace=True)
    df['Duration'] = (df['NextOverallTimeStamp'] - df['TimeStamp']).dt.total_seconds()
    # Set duration for records at the last timestamp to 0
    df.loc[df['TimeStamp'] == max_ts, 'Duration'] = 0
    df['Duration'] = df['Duration'].clip(lower=0) # Ensure non-negative

    df['VmSizeWeighted'] = df['VmSizeBytes'] * df['Duration'] # Units: Byte-Seconds

    if verbose:
        df_sorted = df.sort_values(by=['Name', 'TimeStamp'])
        print(df_sorted[['Name', 'TimeStamp', 'VmSizeBytes', 'NextOverallTimeStamp', 'Duration', 'VmSizeWeighted']].head(10))

    summary = df.groupby('Name').agg(
        TotalVmSizeWeighted=('VmSizeWeighted', 'sum'),     # Sum of VmSize Byte-Seconds
        MaxVmPeakBytes=('VmPeakBytes', 'max'),             # Max VmPeak observed
        MaxVmHwmBytes=('VmHwmBytes', 'max'),
        DataPoints=('VmSizeBytes', 'count'),
        PeakDuration=('Duration','sum')
    ).reset_index()

    summary['TimeWeightedAvgVmSizeBytes'] = summary['TotalVmSizeWeighted'] / summary['PeakDuration']

    summary['TimeWeightedAvgVmSizeMiB'] = summary['TimeWeightedAvgVmSizeBytes'] / BYTES_TO_MIB
    summary['MaxVmPeakMiB'] = summary['MaxVmPeakBytes'] / BYTES_TO_MIB
    summary['MaxVmHwmMiB'] = summary['MaxVmHwmBytes'] / BYTES_TO_MIB

    # print("Calculations complete.")


    summary = summary[[
        'Name', 'TimeWeightedAvgVmSizeMiB', 'MaxVmPeakMiB', 'MaxVmHwmMiB', 'DataPoints', 'PeakDuration'
    ]]

    return summary


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Parse and process the (json-like) data collected from the discern project to display the summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file change log (proc-mem-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='proc-mem-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_program_vmemory_usage(args.input_file, verbose=args.verbose)
    
    
    # final_summary = process_program_vmemory_usage(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)

    if final_summary is not None and not final_summary.empty:
        # print("\n--- Program Memory Usage Summary (Avg VmSize, Peak VmPeak/VmHWM in MiB, PeakDuration in seconds) ---")

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1200)
        pd.set_option('display.float_format', '{:.2f}'.format)

        # print(final_summary.sort_values(by=SORT_BY_COLUMN, ascending=False))
        final_summary.sort_values(by=SORT_BY_COLUMN, ascending=False)
        if args.output:
            try:
                final_summary.to_csv(args.output, index=False)
                # print(f"\nSummary saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}.")

    else:
        print("\nNo program memory usage summary statistics generated.")