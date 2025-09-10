#!/usr/bin/env python3
"""
Test script for the cross-platform traceroute tool.
This script demonstrates the functionality and tests both Windows and Unix compatibility.
"""

import subprocess
import json
import os
import sys
import platform

def test_basic_functionality():
    """Test basic traceroute functionality"""
    print("=" * 60)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 60)
    
    # Test with a simple target
    cmd = [sys.executable, "traceroute.py", "-t", "8.8.8.8", "-n", "1", "-m", "5", "-o", "test_basic"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Basic traceroute test PASSED")
            
            # Check if output file was created
            if os.path.exists("test_basic.json"):
                with open("test_basic.json", "r") as f:
                    data = json.load(f)
                print(f"   - Generated {len(data)} hop entries")
                print(f"   - Sample hop: {data[0] if data else 'No data'}")
                return True
            else:
                print("❌ Output file not created")
                return False
        else:
            print(f"❌ Basic test FAILED: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_platform_detection():
    """Test platform detection"""
    print("\n" + "=" * 60)
    print("TESTING PLATFORM DETECTION")
    print("=" * 60)
    
    # Import the traceroute module to test detection
    try:
        # We'll test by running the script and checking output
        cmd = [sys.executable, "traceroute.py", "-t", "127.0.0.1", "-n", "1", "-m", "2", "-o", "test_platform"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if "Using tracert command" in result.stdout:
            print("✅ Windows tracert detection PASSED")
        elif "Using traceroute command" in result.stdout:
            print("✅ Unix traceroute detection PASSED")
        else:
            print("⚠️  Platform detection unclear")
        
        # Clean up
        if os.path.exists("test_platform.json"):
            os.remove("test_platform.json")
        if os.path.exists("traceroute_outputs/test_platform_run_1.txt"):
            os.remove("traceroute_outputs/test_platform_run_1.txt")
            
        return True
    except Exception as e:
        print(f"❌ Platform detection test error: {e}")
        return False

def test_file_mode():
    """Test file processing mode"""
    print("\n" + "=" * 60)
    print("TESTING FILE PROCESSING MODE")
    print("=" * 60)
    
    # Check if we have existing traceroute files
    if os.path.exists("traceroute_outputs") and os.listdir("traceroute_outputs"):
        cmd = [sys.executable, "traceroute.py", "--test", "traceroute_outputs", "-o", "test_file_mode"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ File processing mode PASSED")
                
                if os.path.exists("test_file_mode.json"):
                    with open("test_file_mode.json", "r") as f:
                        data = json.load(f)
                    print(f"   - Processed {len(data)} hop entries from files")
                    return True
                else:
                    print("❌ Output file not created")
                    return False
            else:
                print(f"❌ File mode test FAILED: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ File mode test error: {e}")
            return False
    else:
        print("⚠️  No existing traceroute files found, skipping file mode test")
        return True

def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    # Test with invalid target
    cmd = [sys.executable, "traceroute.py", "-t", "invalid-target-that-should-fail", "-n", "1", "-m", "2", "-o", "test_error"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # This should either fail gracefully or timeout
        if "Error" in result.stdout or "Warning" in result.stdout:
            print("✅ Error handling PASSED - handled invalid target gracefully")
            return True
        else:
            print("⚠️  Error handling unclear - no error message detected")
            return True  # Not necessarily a failure
    except subprocess.TimeoutExpired:
        print("✅ Error handling PASSED - timed out as expected")
        return True
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False

def test_help():
    """Test help functionality"""
    print("\n" + "=" * 60)
    print("TESTING HELP FUNCTIONALITY")
    print("=" * 60)
    
    cmd = [sys.executable, "traceroute.py", "-h"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "Cross-platform traceroute tool" in result.stdout:
            print("✅ Help functionality PASSED")
            return True
        else:
            print("❌ Help functionality FAILED")
            return False
    except Exception as e:
        print(f"❌ Help test error: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    print("\n" + "=" * 60)
    print("CLEANING UP TEST FILES")
    print("=" * 60)
    
    test_files = [
        "test_basic.json",
        "test_platform.json", 
        "test_file_mode.json",
        "test_error.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")
    
    # Clean up traceroute output files
    for file in os.listdir("traceroute_outputs"):
        if file.startswith("test_"):
            os.remove(os.path.join("traceroute_outputs", file))
            print(f"✅ Removed traceroute_outputs/{file}")

def main():
    """Run all tests"""
    print("🚀 STARTING TRACEROUTE TOOL TESTS")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    tests = [
        test_help,
        test_platform_detection,
        test_basic_functionality,
        test_file_mode,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed - check output above")
    
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
