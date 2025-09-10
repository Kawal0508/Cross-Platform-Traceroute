# Cross-Platform Traceroute Tool

A powerful, cross-platform traceroute implementation that automatically detects your operating system and uses the appropriate traceroute command (`tracert` on Windows, `traceroute` on Linux/Unix).

## Features

- 🌍 **Cross-Platform**: Works on Windows, Linux, macOS, and other Unix-like systems
- 📊 **Rich Statistics**: Provides min, max, average, median, and standard deviation
- 🔄 **Multiple Runs**: Supports multiple traceroute runs with configurable delays
- 📁 **File Processing**: Can process existing traceroute output files
- 🎯 **Automatic Detection**: Detects platform and uses appropriate command
- 📈 **Detailed Output**: Includes raw latency data and comprehensive statistics
- ⚡ **Robust Parsing**: Handles both IPv4 and IPv6 addresses
- 🛡️ **Error Handling**: Graceful error handling with helpful messages

## Installation

No installation required! Just ensure you have Python 3.6+ installed.

### Prerequisites

- **Windows**: `tracert.exe` (included with Windows)
- **Linux/Unix**: `traceroute` command (install via package manager)

```bash
# Ubuntu/Debian
sudo apt install traceroute

# CentOS/RHEL
sudo yum install traceroute

# macOS
brew install traceroute
```

## Usage

### Basic Usage

```bash
python traceroute.py -t <target> -o <output_file>
```

### Examples

```bash
# Basic traceroute to Google DNS
python traceroute.py -t 8.8.8.8 -o google_dns

# Multiple runs with delay
python traceroute.py -t google.com -n 5 -d 2 -m 20 -o google_multiple

# Process existing files
python traceroute.py --test traceroute_outputs -o processed_results
```

### Command Line Options

```
usage: python traceroute.py [-h] [-n NUM_RUNS] [-d RUN_DELAY] [-m MAX_HOPS] -o OUTPUT [-t TARGET] [--test TEST_DIR] [--outdir OUTPUT_DIR]

Cross-platform traceroute tool (uses tracert on Windows, traceroute on Linux/Unix)

options:
  -h, --help            show this help message and exit
  -n NUM_RUNS           Number of times traceroute will run (default: 3)
  -d RUN_DELAY          Number of seconds to wait between two consecutive runs (default: 1)
  -m MAX_HOPS           Max number of hops that traceroute will probe (default: 30)
  -o OUTPUT             Path and name (without extension) of the .json output file (required)
  -t TARGET             A target domain name or IP address
  --test TEST_DIR       Directory containing num_runs text files, each of which contains the output of a traceroute run. If present, this will override all other options and traceroute will not be invoked. Statistics will be computed over the traceroute output stored in the text files only.
  --outdir OUTPUT_DIR   Directory to save raw traceroute outputs (default: traceroute_outputs)
```

## Output Format

The tool generates JSON output with comprehensive statistics for each hop:

```json
[
  {
    "hop": 1,
    "hosts": ["router.example.com [192.168.1.1]"],
    "latencies": [2.1, 1.8, 2.3],
    "count": 3,
    "min": 1.8,
    "max": 2.3,
    "avg": 2.067,
    "med": 2.1,
    "std": 0.25
  }
]
```

### Output Fields

- `hop`: Hop number
- `hosts`: List of hostnames and IP addresses encountered
- `latencies`: Raw latency measurements (in milliseconds)
- `count`: Number of successful measurements
- `min`: Minimum latency
- `max`: Maximum latency
- `avg`: Average latency
- `med`: Median latency
- `std`: Standard deviation

## Testing

Run the included test suite:

```bash
python test_traceroute.py
```

The test suite will:
- ✅ Test basic functionality
- ✅ Verify platform detection
- ✅ Test file processing mode
- ✅ Check error handling
- ✅ Validate help functionality

## Platform Support

### Windows
- Uses `tracert.exe` (built-in)
- Supports IPv4 and IPv6
- Handles Windows-specific output format

### Linux/Unix
- Uses `traceroute` command
- Supports IPv4 and IPv6
- Handles standard Unix output format

## Examples

### Windows Example
```cmd
C:\> python traceroute.py -t google.com -n 3 -o google_test
Using tracert command (windows format)
Raw Traceroute Output (Run 1):
Tracing route to google.com [142.250.191.14]
over a maximum of 30 hops:

  1    <1 ms    <1 ms    <1 ms  router.home.local [192.168.1.1]
  2     5 ms     4 ms     5 ms  gateway.example.com [10.0.0.1]
  ...

Results saved to google_test.json
```

### Linux Example
```bash
$ python traceroute.py -t google.com -n 3 -o google_test
Using traceroute command (unix format)
Raw Traceroute Output (Run 1):
traceroute to google.com (142.250.191.14), 30 hops max, 60 byte packets
 1  router.home.local (192.168.1.1)  1.234 ms  1.123 ms  1.456 ms
 2  gateway.example.com (10.0.0.1)  4.567 ms  5.123 ms  4.890 ms
 ...

Results saved to google_test.json
```

## File Structure

```
project/
├── traceroute.py          # Main traceroute tool
├── test_traceroute.py     # Test suite
├── README.md              # This file
└── traceroute_outputs/    # Directory for raw output files
    ├── traceroute_run_1.txt
    ├── traceroute_run_2.txt
    └── traceroute_run_3.txt
```

## Error Handling

The tool provides comprehensive error handling:

- **Missing Commands**: Clear error messages with installation instructions
- **Timeouts**: Configurable timeout handling (default: 300 seconds)
- **Network Errors**: Graceful handling of network failures
- **Invalid Targets**: Proper error reporting for unreachable targets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Author

Created as part of COMS 5880 - Computer Networks programming assignment.

## Acknowledgments

- Built for cross-platform compatibility
- Inspired by standard traceroute implementations
- Designed for educational and practical use
