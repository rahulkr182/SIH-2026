import tempfile
import subprocess
import os

def run_sandboxed_code(script_str: str, timeout: int = 10) -> dict:
    """
    Writes a python script to a temp file, mounts it in a Docker container with --network none,
    runs it, and returns stdout/stderr.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        script_path = os.path.join(temp_dir, "script.py")
        with open(script_path, "w") as f:
            f.write(script_str)
        
        # Build docker command
        # Using python:3.11-slim, no network, memory cap, cpu cap
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1.0",
            "-v", f"{temp_dir}:/sandbox",
            "-w", "/sandbox",
            "python:3.11-slim",
            "python", "script.py"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }
