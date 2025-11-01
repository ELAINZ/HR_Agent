# /mnt/d/Agent/run_all_tests.py
import subprocess

print("=== Running HR PoC tests ===")
subprocess.run(["python", "poc/hr/tests/run_eval.py"])
