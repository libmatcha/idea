"""
Benchmark: Matcha vs Regex performance comparison.

Run with: python bench.py
"""

import re
import time
from matcha import match, find, find_all


# Test data
SAMPLE_TEXT = """
Contact us at support@example.com or sales@company.io for more information.
Visit https://www.example.com/products or http://docs.example.org/api/v2
Call us at 123-456-7890 or 987-654-3210.
Our hex codes: #ff0000, #00ff00, #0000ff
Binary data: 10101010, 11110000, 00001111
""" * 100  # Repeat for larger dataset

EMAILS_TEXT = "user@domain.com " * 1000
NUMBERS_TEXT = "abc123def456ghi789 " * 1000


def benchmark(name: str, func, iterations: int = 100):
    """Run a benchmark and return timing."""
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed = time.perf_counter() - start
    avg_ms = (elapsed / iterations) * 1000
    return avg_ms


def run_benchmarks():
    print("=" * 70)
    print("MATCHA vs REGEX BENCHMARK")
    print("=" * 70)
    print()
    
    results = []
    
    # ===== EMAIL MATCHING =====
    print("1. EMAIL MATCHING (full string match)")
    print("-" * 50)
    
    email = "example@domain.com"
    
    # Regex pattern
    regex_email = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$')
    
    # Matcha pattern
    matcha_email = "[anum:a-zA-Z0-9._%+-:]@[anum:a-zA-Z0-9.-:]"
    
    regex_time = benchmark("Regex", lambda: regex_email.match(email))
    matcha_time = benchmark("Matcha", lambda: match(matcha_email, email))
    
    print(f"  Regex:  {regex_time:.4f} ms/iter")
    print(f"  Matcha: {matcha_time:.4f} ms/iter")
    print(f"  Ratio:  Matcha is {matcha_time/regex_time:.1f}x slower")
    results.append(("Email Match", regex_time, matcha_time))
    print()
    
    # ===== FIND ALL EMAILS =====
    print("2. FIND ALL EMAILS (in 1000 emails text)")
    print("-" * 50)
    
    regex_find_email = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+')
    matcha_find_email = "[anum:a-zA-Z0-9._%+-:]@[anum:a-zA-Z0-9.-:]"
    
    regex_time = benchmark("Regex", lambda: regex_find_email.findall(EMAILS_TEXT), iterations=10)
    matcha_time = benchmark("Matcha", lambda: find_all(matcha_find_email, EMAILS_TEXT), iterations=10)
    
    print(f"  Regex:  {regex_time:.4f} ms/iter")
    print(f"  Matcha: {matcha_time:.4f} ms/iter")
    print(f"  Ratio:  Matcha is {matcha_time/regex_time:.1f}x slower")
    results.append(("Find All Emails", regex_time, matcha_time))
    print()
    
    # ===== FIND ALL NUMBERS =====
    print("3. FIND ALL NUMBERS (in 1000 number groups)")
    print("-" * 50)
    
    regex_nums = re.compile(r'[0-9]+')
    matcha_nums = "[dec::]"
    
    regex_time = benchmark("Regex", lambda: regex_nums.findall(NUMBERS_TEXT), iterations=10)
    matcha_time = benchmark("Matcha", lambda: find_all(matcha_nums, NUMBERS_TEXT), iterations=10)
    
    print(f"  Regex:  {regex_time:.4f} ms/iter")
    print(f"  Matcha: {matcha_time:.4f} ms/iter")
    print(f"  Ratio:  Matcha is {matcha_time/regex_time:.1f}x slower")
    results.append(("Find All Numbers", regex_time, matcha_time))
    print()
    
    # ===== PHONE NUMBER PATTERN =====
    print("4. PHONE NUMBER MATCH (###-###-####)")
    print("-" * 50)
    
    phone = "123-456-7890"
    
    regex_phone = re.compile(r'^\d{3}-\d{3}-\d{4}$')
    matcha_phone = "[dec::3]-[dec::3]-[dec::4]"
    
    regex_time = benchmark("Regex", lambda: regex_phone.match(phone))
    matcha_time = benchmark("Matcha", lambda: match(matcha_phone, phone))
    
    print(f"  Regex:  {regex_time:.4f} ms/iter")
    print(f"  Matcha: {matcha_time:.4f} ms/iter")
    print(f"  Ratio:  Matcha is {matcha_time/regex_time:.1f}x slower")
    results.append(("Phone Match", regex_time, matcha_time))
    print()
    
    # ===== HEX COLOR CODE =====
    print("5. HEX COLOR MATCH (#RRGGBB)")
    print("-" * 50)
    
    color = "#ff00aa"
    
    regex_hex = re.compile(r'^#[0-9a-fA-F]{6}$')
    matcha_hex = "#[hex::6]"
    
    regex_time = benchmark("Regex", lambda: regex_hex.match(color))
    matcha_time = benchmark("Matcha", lambda: match(matcha_hex, color))
    
    print(f"  Regex:  {regex_time:.4f} ms/iter")
    print(f"  Matcha: {matcha_time:.4f} ms/iter")
    print(f"  Ratio:  Matcha is {matcha_time/regex_time:.1f}x slower")
    results.append(("Hex Color Match", regex_time, matcha_time))
    print()
    
    # ===== SUMMARY =====
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Test':<20} {'Regex (ms)':<12} {'Matcha (ms)':<12} {'Ratio':<10}")
    print("-" * 54)
    
    for name, regex_t, matcha_t in results:
        ratio = matcha_t / regex_t
        print(f"{name:<20} {regex_t:<12.4f} {matcha_t:<12.4f} {ratio:<10.1f}x")
    
    print()
    print("Note: Matcha is a pure Python implementation focused on readability,")
    print("      while regex is a highly optimized C implementation.")
    print("      For most use cases, the performance difference is negligible.")


if __name__ == "__main__":
    run_benchmarks()
