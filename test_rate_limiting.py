#!/usr/bin/env python3

# Test rate limiting functionality
import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from terminal.ai_parser import parse_nl, get_rate_limit_status, rate_limiter

def test_rate_limiting():
    print("=== Testing Rate Limiting (12 req/min) ===")
    
    # Test 1: Check initial status
    status = get_rate_limit_status()
    print(f"\nInitial status:")
    print(f"  Requests made: {status['requests_made']}")
    print(f"  Requests remaining: {status['requests_remaining']}")
    print(f"  Can make request: {status['can_make_request']}")
    
    # Test 2: Make several quick requests to test fallback patterns (no API calls)
    print(f"\n=== Testing Fallback Patterns (No API calls) ===")
    fallback_commands = [
        "create a new folder",
        "show all python files", 
        "clear screen",
        "make folder test"
    ]
    
    for cmd in fallback_commands:
        result = parse_nl(cmd)
        print(f"'{cmd}' -> {result}")
    
    status = get_rate_limit_status()
    print(f"\nAfter fallback tests:")
    print(f"  Requests made: {status['requests_made']} (should still be 0)")
    
    # Test 3: Test AI commands that would trigger API calls
    print(f"\n=== Testing AI Commands (Would make API calls) ===")
    ai_commands = [
        "delete all temporary files",  # This should trigger AI parsing
        "show me system information in detail",
        "create multiple folders at once"
    ]
    
    for cmd in ai_commands:
        print(f"\nTesting: '{cmd}'")
        status_before = get_rate_limit_status()
        print(f"  Before: {status_before['requests_made']} requests made")
        
        result = parse_nl(cmd)
        print(f"  Result: {result}")
        
        status_after = get_rate_limit_status()
        print(f"  After: {status_after['requests_made']} requests made")
        
        if not status_after['can_make_request']:
            print(f"  ⚠️  Rate limit reached! Wait time: {status_after['wait_time']:.1f}s")
            break
    
    # Test 4: Simulate hitting rate limit
    print(f"\n=== Testing Rate Limit Protection ===")
    print("Simulating rapid API calls...")
    
    # Manually fill up the rate limiter
    current_time = time.time()
    for i in range(12):  # Fill to capacity
        rate_limiter.request_times.append(current_time)
    
    status = get_rate_limit_status()
    print(f"Simulated rate limit status:")
    print(f"  Requests made: {status['requests_made']}")
    print(f"  Can make request: {status['can_make_request']}")
    print(f"  Wait time: {status['wait_time']:.1f}s")
    
    # Try to make a request when rate limited
    print(f"\nTrying to parse command when rate limited:")
    result = parse_nl("some complex command that needs AI")
    print(f"Result: {result}")

def test_rate_limiter_class():
    print("\n=== Testing Rate Limiter Class Directly ===")
    
    # Create a test limiter with smaller limits for faster testing
    from terminal.ai_parser import APIRateLimiter
    test_limiter = APIRateLimiter(max_requests=3, time_window=10)
    
    print("Testing with 3 requests per 10 seconds...")
    
    # Make requests up to the limit
    for i in range(5):
        can_request = test_limiter.can_make_request()
        print(f"Request {i+1}: Can make request = {can_request}")
        
        if can_request:
            test_limiter.record_request()
            print(f"  ✅ Request recorded")
        else:
            wait_time = test_limiter.time_until_next_request()
            print(f"  ❌ Rate limited! Wait {wait_time:.1f} seconds")
            
        time.sleep(1)  # Small delay between tests

if __name__ == "__main__":
    test_rate_limiting()
    test_rate_limiter_class()