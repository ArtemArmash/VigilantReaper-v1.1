import subprocess
import os

class Executor:
    
    @staticmethod
    def run_command(command: list) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                check=True
            )
            if result.stderr and not result.stdout:
                return result.stderr.strip()
            return result.stdout
        except Exception as e:
            print(f"[!] Critical failure executing {' '.join(command)}: {e}")
            return ""
