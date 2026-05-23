import subprocess
import os

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd} in {cwd or '.'}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

# Push the submodule
loop_dir = os.path.join(os.getcwd(), "Loop")
run("git push origin caresens_integration", cwd=loop_dir)

# Push the outer repo
run("git push origin caresens_integration")
