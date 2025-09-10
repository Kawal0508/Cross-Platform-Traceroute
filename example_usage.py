#!/usr/bin/env python3
"""
Example usage script for the Cross-Platform Traceroute Tool.
This script demonstrates various ways to use the traceroute tool.
"""

import subprocess
import json
import os
import sys

def run_example(target, description):
    """Run a traceroute example and display results"""
    print(f"\n{'='*60}")
    print(f"EXAMPLE: {description}")
    print(f"Target: {target}")
    print(f"{'='*60}")
    
    output_file = f"example_{target.replace('.', '_').replace(':', '_')}"
    cmd = [sys.executable, "traceroute.py", "-t", target, "-n", "2", "-m", "5", "-o", output_file]
    
    try:
        print("Running traceroute...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Traceroute completed successfully!")
            
            # Load and display results
            if os.path.exists(f"{output_file}.json"):
                with open(f"{output_file}.json", "r") as f:
                    data = json.load(f)
                
                print(f"\nResults Summary:")
                print(f"- Total hops: {len(data)}")
                
                for hop in data[:3]:  # Show first 3 hops
                    print(f"  Hop {hop['hop']}: {hop['hosts'][0] if hop['hosts'] else 'No response'}")
                    print(f"    Latency: {hop['min']:.1f}ms - {hop['max']:.1f}ms (avg: {hop['avg']:.1f}ms)")
                
                if len(data) > 3:
                    print(f"  ... and {len(data) - 3} more hops")
                
                # Clean up
                os.remove(f"{output_file}.json")
                if os.path.exists(f"traceroute_outputs/{output_file}_run_1.txt"):
                    os.remove(f"traceroute_outputs/{output_file}_run_1.txt")
                if os.path.exists(f"traceroute_outputs/{output_file}_run_2.txt"):
                    os.remove(f"traceroute_outputs/{output_file}_run_2.txt")
                
            else:
                print("❌ Output file not found")
        else:
            print(f"❌ Traceroute failed: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        print("⏰ Traceroute timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run example traceroutes"""
    print("🚀 CROSS-PLATFORM TRACEROUTE TOOL - EXAMPLES")
    print("This script demonstrates various traceroute scenarios")
    
    # Example targets
    examples = [
        ("8.8.8.8", "Google DNS (IPv4)"),
        ("1.1.1.1", "Cloudflare DNS (IPv4)"),
        ("google.com", "Google.com (Domain Name)"),
        ("127.0.0.1", "Localhost (IPv4)"),
    ]
    
    print(f"\nRunning {len(examples)} examples...")
    
    for target, description in examples:
        try:
            run_example(target, description)
        except KeyboardInterrupt:
            print("\n\n⏹️  Examples interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
    
    print(f"\n{'='*60}")
    print("EXAMPLES COMPLETED")
    print("="*60)
    print("For more advanced usage, see README.md")
    print("To run tests, use: python test_traceroute.py")

if __name__ == "__main__":
    main()
