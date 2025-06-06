import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
# import seaborn as sns


# INPUT_FILE_PATH = Path("network-data.txt")
# OUTPUT_CSV_FILE = Path("net-res.csv")
# VERBOSE_LOGGING = False
SORT_BY_COLUMN = 'TotalBytes'
DEFAULT_TIME_BIN_ACTIVITY_PLOT = "3s"

def create_canonical_pair(ip1, ip2):
    """Creates a sorted tuple representing the IP pair."""
    return tuple(sorted((ip1, ip2)))

def draw_time_activity_plot(df: pd.DataFrame, ax1: plt.Axes, time_bin: str, verbose: bool = False):
    
    if df.empty or 'PacketTimestamp' not in df.columns or 'Length' not in df.columns:
        if verbose: print("Verbose: Time activity plot cannot be drawn, DataFrame is empty or required columns missing.")
        ax1.text(0.5, 0.5, "No data for time activity plot", ha='center', va='center')
        ax1.set_title('Network Activity Over Time')
        return
    if len(df) < 2:
        if verbose: print(f"Verbose: Not enough data points (found {len(df)}) for time activity plot with bin '{time_bin}'.")
        ax1.text(0.5, 0.5, f"Not enough data for plot (bin: {time_bin})", ha='center', va='center')
        ax1.set_title('Network Activity Over Time')
        return

    df_ts = df.copy()
    df_ts['PacketTimestamp'] = pd.to_datetime(df_ts['PacketTimestamp'])
    df_ts = df_ts.set_index('PacketTimestamp')
    
    try:
        aggregated_data = df_ts['Length'].resample(time_bin).agg(['mean', 'sum'])
        aggregated_data.rename(columns={'mean': 'AvgPacketSize', 'sum': 'TotalPacketSize'}, inplace=True)
        
        aggregated_data['AvgPacketSize'] = aggregated_data['AvgPacketSize'].fillna(0)
        aggregated_data['TotalPacketSize'] = aggregated_data['TotalPacketSize'].fillna(0).astype(int)

        if aggregated_data.empty:
            if verbose: print(f"Verbose: No data to plot after resampling with bin '{time_bin}'.")
            ax1.text(0.5, 0.5, f"No data after resampling (bin: {time_bin})", ha='center', va='center')
            ax1.set_title(f'Network Activity Over Time (Bin: {time_bin})')
            return


        if aggregated_data.index.empty:
            if verbose: print(f"Verbose: No time index data after resampling for bin '{time_bin}'.")
            return
            
        start_time = aggregated_data.index[0]

        time_offsets_seconds = (aggregated_data.index - start_time).total_seconds()


        color_bar = 'skyblue'
        
        try:
            bin_duration_seconds = pd.to_timedelta(time_bin).total_seconds()
            bar_width_numeric = bin_duration_seconds * 0.8 
        except ValueError:
            if verbose: print(f"Verbose: Could not parse time_bin '{time_bin}' for dynamic bar width. Using default width of 0.8*bin_value.")

            numeric_part_str = ''.join(filter(str.isdigit, time_bin))
            if numeric_part_str:
                bar_width_numeric = float(numeric_part_str) * 0.8
            else:
                bar_width_numeric = 1.0 * 0.8 
        
        ax1.bar(time_offsets_seconds, aggregated_data['AvgPacketSize'],
                width=bar_width_numeric,
                color=color_bar, alpha=0.7, label='Avg Packet Size (Bytes)')
        ax1.set_xlabel(f"Time from start (seconds, binned every {time_bin})")
        ax1.set_ylabel("Average Packet Size (Bytes)", color=color_bar)
        ax1.tick_params(axis='y', labelcolor=color_bar)


        ax2 = ax1.twinx() 
        color_line = 'coral'
        ax2.plot(time_offsets_seconds, aggregated_data['TotalPacketSize'],
                 color=color_line, marker='o', linestyle='-', linewidth=2, markersize=4, label='Total Packet Size (Bytes)')
        ax2.set_ylabel("Total Packet Size (Bytes)", color=color_line)
        ax2.tick_params(axis='y', labelcolor=color_line)
        ax2.set_ylim(bottom=0) 

        ax1.set_title(f"Network Activity Over Time (Bin: {time_bin})", pad=20)
        
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right')

        ax1.grid(True, linestyle='--', alpha=0.5, axis='y')

    except Exception as e:
        if verbose: print(f"Verbose: Error drawing time activity plot: {e}")
        ax1.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', color='red', wrap=True)
        ax1.set_title(f'Network Activity Over Time (Bin: {time_bin})')




def process_all_pairs_file(file_path: Path, verbose: bool = False):
    """
    Reads the JSON Lines file, processes all IP packets, calculates network
    statistics per unique communication pair {IP_A, IP_B}, and returns a
    summary DataFrame.
    """
    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None, None, None

    # print(f"Processing file: {file_path}")
    # print(f"Analyzing ALL communication pairs...")

    extracted_packets = []
    line_num = 0
    parsing_errors = 0
    processed_lines = 0
    packets_processed = 0
    packets_skipped_no_ip = 0

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    data_batch = json.loads(line)
                    packets = data_batch.get("Packets", [])

                    if not packets:
                        continue

                    processed_lines += 1
                    for packet in packets:
                        arp_flag = False
                        packet_ts = packet.get("TimeStamp")
                        packet_len = packet.get("Length")
                        ip_data = packet.get("IP")
                        if not ip_data:
                            ip_data = packet.get("ARP")
                            arp_flag = True

                        if packet_ts is None or packet_len is None or not ip_data:
                            packets_skipped_no_ip += 1
                            continue
                        
                        if(arp_flag):
                            src_ip = ip_data.get("SrcProtAdd")
                            dst_ip = ip_data.get("DstProtAdd")
                        else:
                            src_ip = ip_data.get("SRCIP")
                            dst_ip = ip_data.get("DSTIP")

                        if not src_ip or not dst_ip:
                            packets_skipped_no_ip += 1
                            continue

                        ip_pair = create_canonical_pair(src_ip, dst_ip)

                        extracted_packets.append({
                            'PacketTimestamp': int(packet_ts),
                            'Length': int(packet_len),
                            'IP_A': ip_pair[0],
                            'IP_B': ip_pair[1]
                        })
                        packets_processed += 1

                except json.JSONDecodeError:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to JSON decode error.")
                    continue
                except Exception as e:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to other error: {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}")
        return None,None,None
    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}.")
        return None,None,None

    if parsing_errors > 0: print(f" Lines skipped (parsing error): {parsing_errors} for file: {file_path}")

    if not extracted_packets:
        print("No valid IP packet data for analysis was extracted for file: {file_path}.")
        return None,None,None


    # print("Converting extracted data to DataFrame...")
    df = pd.DataFrame(extracted_packets)
    df['PacketTimestamp'] = pd.to_datetime(df['PacketTimestamp'], unit='s', errors='coerce')
    df['Length'] = pd.to_numeric(df['Length'], errors='coerce').fillna(0)
    df.dropna(subset=['PacketTimestamp', 'IP_A', 'IP_B'], inplace=True)

        # --- Overall Statistics Calculation ---
    overall_total_analyzed_packets = len(df)
    overall_stats = {
        'Overall Packet Count': 0,
        'Overall Total Bytes': 0,
        'Overall Average Packet Size (Bytes)': 0.0,
        'Overall Capture Duration (Seconds)': 0.0,
        'Overall Average Rate (Mbps)': 0.0
    }

    if overall_total_analyzed_packets > 0:
        overall_total_bytes = df['Length'].sum()
        overall_avg_packet_size = (overall_total_bytes / overall_total_analyzed_packets) if overall_total_analyzed_packets > 0 else 0.0
        
        min_timestamp = df['PacketTimestamp'].min()
        max_timestamp = df['PacketTimestamp'].max()
        overall_duration_seconds = 0.0
        overall_avg_rate_mbps = 0.0

        if pd.notna(min_timestamp) and pd.notna(max_timestamp):
            duration_timedelta = max_timestamp - min_timestamp
            overall_duration_seconds = duration_timedelta.total_seconds()

            if overall_duration_seconds > 0:
                overall_avg_rate_mbps = (overall_total_bytes * 8.0) / (overall_duration_seconds * 1_000_000.0)
            elif overall_total_bytes > 0: # Duration is 0 (e.g. all in same sec), but data exists
                overall_avg_rate_mbps = (overall_total_bytes * 8.0) / (1.0 * 1_000_000.0) # Assume 1s for rate calc
        
        overall_stats.update({
            'Overall Packet Count': int(overall_total_analyzed_packets),
            'Overall Total Bytes': int(overall_total_bytes),
            'Overall Average Packet Size (Bytes)': float(overall_avg_packet_size),
            'Overall Capture Duration (Seconds)': float(overall_duration_seconds),
            'Overall Average Rate (Mbps)': float(overall_avg_rate_mbps)
        })

    if df.empty:
        print("DataFrame is empty after initial processing and cleaning for file: {file_path}.")
        return None,None,None

    # print(f"DataFrame created with {len(df)} relevant packet entries.")
    if verbose:
        print("\n--- Processed DataFrame Head ---")
        print(df.head())

    # print("\nCalculating statistics per communication pair...")
    pair_grouping_keys = ['IP_A', 'IP_B']

    bytes_per_second = df.groupby(
        pair_grouping_keys + [pd.Grouper(key='PacketTimestamp', freq='1s')]
    )['Length'].sum().reset_index()
    bytes_per_second.rename(columns={'Length': 'BytesInSecond'}, inplace=True)

    if bytes_per_second.empty:
        print("Warning: No data after grouping by second for file: {file_path}.")
    elif verbose: print("Per-second byte aggregation complete.")
    peak_bytes = bytes_per_second.groupby(pair_grouping_keys)['BytesInSecond'].max().reset_index()
    peak_bytes['PeakRateMbps'] = peak_bytes['BytesInSecond'] * 8.0 / 1_000_000.0
    if verbose: print("Peak rate calculation complete.")


    avg_rate_data = bytes_per_second.groupby(pair_grouping_keys).agg(
        TotalBytes=('BytesInSecond', 'sum'),
        TotalActiveSeconds=('BytesInSecond', 'count')
    ).reset_index()
    avg_rate_data['AvgRateMbps'] = avg_rate_data.apply(
        lambda row: (row['TotalBytes'] * 8.0 / (row['TotalActiveSeconds'] * 1_000_000.0))
                    if row['TotalActiveSeconds'] > 0 else 0.0, axis=1)
    if verbose: print("Average rate, Total Bytes, Active Seconds calculation complete.")

    total_packets = df.groupby(pair_grouping_keys).size().reset_index(name='TotalPackets')
    if verbose: print("Total packet count complete.")

    if verbose: print("Merging results...")
    summary_df = total_packets
    summary_df = pd.merge(summary_df, avg_rate_data[['IP_A', 'IP_B', 'AvgRateMbps', 'TotalBytes', 'TotalActiveSeconds']], on=pair_grouping_keys, how='left')
    summary_df = pd.merge(summary_df, peak_bytes[['IP_A', 'IP_B', 'PeakRateMbps']], on=pair_grouping_keys, how='left')
    summary_df.fillna(0, inplace=True)

    for col in ['TotalPackets', 'TotalBytes', 'TotalActiveSeconds']:
        if col in summary_df.columns:
             summary_df[col] = summary_df[col].astype(np.int64)
    if verbose: print("Merging complete.")

    summary_df = summary_df[[
        'IP_A', 'IP_B', 'TotalPackets', 'TotalBytes',
        'TotalActiveSeconds', 'AvgRateMbps', 'PeakRateMbps'
    ]]

    return summary_df, overall_stats,df

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Parse and process the (json-like) data collected from the discern project to display the summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file change log (network-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='network-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary_df, overall_stats, plotting_df= process_all_pairs_file(args.input_file, verbose=args.verbose)
    # final_summary = process_all_pairs_file(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)

    # if final_summary is not None and not final_summary.empty:
    #     # print("\n--- Summary Per Communication Pair {IP_A, IP_B} ---")
    #     pd.set_option('display.max_rows', 200)
    #     pd.set_option('display.max_columns', None)
    #     pd.set_option('display.width', 1200)
    #     pd.set_option('display.float_format', '{:.3f}'.format)

        # print(f"Sorting results by '{SORT_BY_COLUMN}' (descending)...")
        # final_summary_sorted = final_summary.sort_values(by=SORT_BY_COLUMN, ascending=False)
        # print(final_summary_sorted)

    if args.output:
        try:
            with open(args.output, 'w', newline='') as f:
                if overall_stats:
                    f.write(f"# Overall Packet Count: {overall_stats.get('Overall Packet Count', 'N/A')}\n")
                    f.write(f"# Overall Total Bytes: {overall_stats.get('Overall Total Bytes', 'N/A')}\n")
                    f.write(f"# Overall Average Packet Size (Bytes): {overall_stats.get('Overall Average Packet Size (Bytes)', 0.0):.2f}\n")
                    f.write(f"# Overall Capture Duration (Seconds): {overall_stats.get('Overall Capture Duration (Seconds)', 0.0):.3f}\n")
                    f.write(f"# Overall Average Rate (Mbps): {overall_stats.get('Overall Average Rate (Mbps)', 0.0):.3f}\n")
                    

                    if final_summary_df is not None and not final_summary_df.empty:
                        f.write("\n")

                if final_summary_df is not None and not final_summary_df.empty:
                    final_summary_sorted = final_summary_df.sort_values(by=SORT_BY_COLUMN, ascending=False)
                    final_summary_sorted.to_csv(f, index=False, header=True)
                elif overall_stats and args.verbose: # Only overall stats written
                    print(f"Verbose: Overall statistics written to {args.output}. No per-pair data to write.")

            if args.verbose:
                print(f"Verbose: Network summary CSV (with overall stats) saved to: {args.output}")

        except Exception as e:
            if args.verbose:
                print(f"Verbose: Error saving summary to CSV: {e} for file: {args.input_file}")
            raise e 
    elif args.verbose:
        print(f"Verbose: No output file specified. Results not saved. Run with -o <filename.csv> to save.")

    if plotting_df is not None and not plotting_df.empty:
        
        plot_output_dir = args.output.parent
        combined_plot_file = plot_output_dir / f"network.png"
        
        if args.verbose: 
            print(f"Verbose: Generating combined analysis plot: {combined_plot_file}")

        fig, ax1 = plt.subplots(figsize=(15, 7))

        draw_time_activity_plot(plotting_df, ax1, 
                                time_bin=DEFAULT_TIME_BIN_ACTIVITY_PLOT, 
                                verbose=args.verbose)
        
        try:
            plt.savefig(combined_plot_file)
            if args.verbose: print(f"Verbose: Combined analysis plot saved to {combined_plot_file}")
        except Exception as e:
            if args.verbose: print(f"Verbose: Error saving combined analysis plot: {e}")
        finally:
            plt.close(fig)
            
    elif args.verbose:
        print("Verbose: No packet data available to generate combined plot.")
