import argparse
import subprocess
import json
import os
import statistics
import re
import time
import platform
import shutil

def detect_traceroute_command():
    """Detect available traceroute command based on platform"""
    system = platform.system().lower()
    
    if system == "windows":
        # Try tracert.exe first (Windows native)
        if shutil.which("tracert"):
            return "tracert", "windows"
        # Try traceroute in WSL/Git Bash
        elif shutil.which("traceroute"):
            return "traceroute", "unix"
        else:
            return None, None
    else:
        # Unix-like systems
        if shutil.which("traceroute"):
            return "traceroute", "unix"
        else:
            return None, None

def build_traceroute_command(command, target, max_hops, platform_type):
    """Build the appropriate traceroute command based on platform"""
    if platform_type == "windows":
        # Windows tracert uses -h for max hops
        return [command, "-h", str(max_hops), target]
    else:
        # Unix traceroute uses -m for max hops
        return [command, "-m", str(max_hops), target]

def parse_tracert_output(output):
    """Parse Windows tracert output format"""
    hop_data = {}
    
    for line in output.split("\n"):
        # Windows tracert format examples:
        # "  1    <1 ms    <1 ms    <1 ms  router.home.local [192.168.1.1]"
        # "  2     *        *        *     Request timed out."
        # "  3     5 ms     4 ms     6 ms  gateway.example.com [10.0.0.1]"
        # IPv6: "  1     3 ms     2 ms     3 ms  router.example.com [2610:130:110:1505::253]"
        
        # Pattern to match hop number and extract data
        hop_match = re.match(r'^\s*(\d+)\s+', line)
        if hop_match:
            hop = int(hop_match.group(1))
            
            # Extract latencies (handles both regular numbers and <1 format)
            latency_pattern = r'(\d+|\<\d+)\s*ms'
            latencies = []
            for match in re.finditer(latency_pattern, line):
                lat_str = match.group(1)
                if lat_str.startswith('<'):
                    latencies.append(float(lat_str[1:]))
                else:
                    latencies.append(float(lat_str))
            
            # Extract hostname and IP (support both IPv4 and IPv6)
            hostname = ""
            ip = ""
            
            # Extract hostname and IP from the end of the line
            # Windows tracert format: "  1     2 ms     2 ms     6 ms  hostname [ip]"
            
            # Find all text after the last latency measurement
            # Use a more precise pattern that looks for the complete latency section
            pattern = r'^\s*\d+\s+(?:(?:\d+|\<\d+|\*)\s*ms\s*){1,3}\s*(.*)$'
            match = re.match(pattern, line)
            if match:
                remaining_text = match.group(1).strip()
                
                if remaining_text:
                    # Pattern: hostname [IP]
                    host_ip_match = re.search(r'^(.+?)\s+\[([^\]]+)\]$', remaining_text)
                    if host_ip_match:
                        hostname = host_ip_match.group(1).strip()
                        ip = host_ip_match.group(2).strip()
                    else:
                        # Pattern: just [IP]
                        ip_only_match = re.search(r'^\[([^\]]+)\]$', remaining_text)
                        if ip_only_match:
                            ip = ip_only_match.group(1).strip()
                        else:
                            # Pattern: just hostname (no IP in brackets)
                            hostname = remaining_text
            
            # Check for timeout
            if "*" in line or "Request timed out" in line:
                latencies = []  # No valid latencies for timeout
            
            # Build host entry
            if hostname and ip:
                host_entry = [f"{hostname} [{ip}]"]
            elif hostname:
                host_entry = [hostname]
            elif ip:
                host_entry = [f"[{ip}]"]
            else:
                host_entry = ["*"]
            
            if hop not in hop_data:
                hop_data[hop] = {'hosts': set(), 'latencies': []}
            hop_data[hop]['hosts'].update(host_entry)
            hop_data[hop]['latencies'].extend(latencies)
    
    return hop_data

def run_traceroute(target, num_runs, run_delay, max_hops, output_dir):
    """Run traceroute with platform detection"""
    
    # Detect available traceroute command
    command, platform_type = detect_traceroute_command()
    if not command:
        print("Error: No traceroute command found.")
        print("On Windows: tracert.exe should be available by default")
        print("On Linux/Unix: install traceroute package")
        return []
    
    print(f"Using {command} command ({platform_type} format)")
    
    os.makedirs(output_dir, exist_ok=True)
    traceroute_outputs = []
    
    for i in range(num_runs):
        try:
            # Build command based on platform
            cmd = build_traceroute_command(command, target, max_hops, platform_type)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, text=True, check=True, timeout=300
            )
            print(f"Raw Traceroute Output (Run {i+1}):")
            print(result.stdout)
            traceroute_outputs.append(result.stdout)
            
            with open(os.path.join(output_dir, f"traceroute_run_{i+1}.txt"), "w", encoding="utf-8") as f:
                f.write(result.stdout)
                
            # Add delay between runs if specified
            if run_delay > 0 and i < num_runs - 1:
                print(f"Waiting {run_delay} seconds before next run...")
                time.sleep(run_delay)
                
        except subprocess.TimeoutExpired:
            print(f"Warning: Traceroute run {i+1} timed out after 300 seconds")
            continue
        except FileNotFoundError:
            print(f"Error: {command} command not found. Ensure it is installed on your system.")
            return []
        except subprocess.CalledProcessError as e:
            print(f"Error in traceroute run {i+1}: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            continue
        except Exception as e:
            print(f"Unexpected error in traceroute run {i+1}: {e}")
            continue
    
    return traceroute_outputs

def parse_traceroute_output(output):
    
    hop_data = {}
    for line in output.split("\n"):
        # More robust pattern that handles various traceroute formats
        match = re.findall(r"^\s*(\d+)\s+([a-zA-Z0-9.-]+)?(?: \((\d+\.\d+\.\d+\.\d+)\))?((?:\s+\d+\.\d+ ms)+|\s*\*|\s+\*+)", line)
        if match:
            for hop_match in match:
                hop = int(hop_match[0])
                hostname = hop_match[1] if hop_match[1] else ""
                ip = hop_match[2] if hop_match[2] else ""
                
                # Better host entry construction
                if hostname and ip:
                    host_entry = [f"{hostname} ({ip})"]
                elif hostname:
                    host_entry = [hostname]
                elif ip:
                    host_entry = [f"({ip})"]
                else:
                    host_entry = ["*"]
                
                # Extract latencies more robustly
                latencies = [float(x) for x in re.findall(r"(\d+\.\d+) ms", line)]
                
                if hop not in hop_data:
                    hop_data[hop] = {'hosts': set(), 'latencies': []}
                hop_data[hop]['hosts'].update(host_entry)
                hop_data[hop]['latencies'].extend(latencies)
    print("Parsed Hop Data:", hop_data)  # Debugging print statement
    return hop_data

def compute_statistics(hop_data):
    
    result = []
    for hop, data in sorted(hop_data.items()):
        latencies = data['latencies']
        if latencies:
            result.append({
                'hop': hop,
                'hosts': list(data['hosts']),
                'latencies': latencies,  # Include raw data
                'count': len(latencies),  # Number of measurements
                'min': min(latencies),
                'max': max(latencies),
                'avg': round(sum(latencies) / len(latencies), 3),
                'med': statistics.median(latencies),
                'std': round(statistics.stdev(latencies) if len(latencies) > 1 else 0, 3)
            })
    return result

def process_traceroute_runs(outputs):
    """Process multiple traceroute runs and aggregate data"""
    aggregated_data = {}
    for output in outputs:
        # Detect format and parse accordingly
        if "Tracing route to" in output or "Trace complete" in output:
            # Windows tracert format
            parsed_data = parse_tracert_output(output)
            print("Detected Windows tracert format")
        else:
            # Unix traceroute format
            parsed_data = parse_traceroute_output(output)
            print("Detected Unix traceroute format")
            
        for hop, data in parsed_data.items():
            if hop not in aggregated_data:
                aggregated_data[hop] = {'hosts': set(), 'latencies': []}
            aggregated_data[hop]['hosts'].update(data['hosts'])
            aggregated_data[hop]['latencies'].extend(data['latencies'])
    return compute_statistics(aggregated_data)

def read_traceroute_files(directory):
    """Read traceroute output files from directory"""
    outputs = []
    for file in sorted(os.listdir(directory)):
        if file.endswith('.txt'):
            with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                outputs.append(f.read())
    return outputs

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Cross-platform traceroute tool (uses tracert on Windows, traceroute on Linux/Unix)",
        usage="python traceroute.py [-h] [-n NUM_RUNS] [-d RUN_DELAY] [-m MAX_HOPS] -o OUTPUT [-t TARGET] [--test TEST_DIR] [--outdir OUTPUT_DIR]"
    )
    parser.add_argument("-n", type=int, default=3, metavar="NUM_RUNS", help="Number of times traceroute will run")
    parser.add_argument("-d", type=int, default=1, metavar="RUN_DELAY", help="Number of seconds to wait between two consecutive runs")
    parser.add_argument("-m", type=int, default=30, metavar="MAX_HOPS", help="Max number of hops that traceroute will probe")
    parser.add_argument("-o", type=str, required=True, metavar="OUTPUT", help="Path and name (without extension) of the .json output file")
    parser.add_argument("-t", type=str, metavar="TARGET", help="A target domain name or IP address")
    parser.add_argument("--test", type=str, metavar="TEST_DIR", help="Directory containing num_runs text files, each of which contains the output of a traceroute run. If present, this will override all other options and traceroute will not be invoked. Statistics will be computed over the traceroute output stored in the text files only.")
    parser.add_argument("--outdir", type=str, default="traceroute_outputs", metavar="OUTPUT_DIR", help="Directory to save raw traceroute outputs (additional functionality)")
    
    args = parser.parse_args()
    
    try:
        if args.test:
            traceroute_outputs = read_traceroute_files(args.test)
        else:
            if not args.t:
                print("Error: Target must be provided if not using test mode.")
                return
            traceroute_outputs = run_traceroute(args.t, args.n, args.d, args.m, args.outdir)
            if not traceroute_outputs:
                return
        
        results = process_traceroute_runs(traceroute_outputs)
        
        with open(f"{args.o}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        
        print(f"Results saved to {args.o}.json")
    except Exception as e:
        print(f"Error encountered: {e}")

if __name__ == "__main__":
    main()
