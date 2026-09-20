from app.sandbox.docker_runner import run_sandboxed_code

def test_math():
    print("--- Test 1: Math Execution ---")
    script = """
a = 10.5
b = 5.2
print(f"Result: {a - b}")
"""
    result = run_sandboxed_code(script)
    print("Success:", result['success'])
    print("Output:", result['stdout'])

def test_network():
    print("\n--- Test 2: Network Blocked (Air-Gap) ---")
    script = """
import urllib.request
try:
    urllib.request.urlopen("http://google.com", timeout=2)
    print("Network call succeeded!")
except Exception as e:
    print(f"Network blocked: {e}")
"""
    result = run_sandboxed_code(script)
    print("Success:", result['success'])
    print("Output:", result['stdout'])
    print("Stderr:", result['stderr'])

if __name__ == "__main__":
    test_math()
    test_network()
