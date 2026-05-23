import subprocess
import os

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd} in {cwd or '.'}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

# Inside Loop submodule
loop_dir = os.path.join(os.getcwd(), "Loop")

run("git add Modules/CareSensAirCGMPlugin.swift", cwd=loop_dir)
run('git commit -m "Fix CareSensAirCGMPlugin compile errors (NewGlucoseSample & rawState)"', cwd=loop_dir)

# Back to LoopWorkspace_test
run("git add Loop")
run('git commit -m "Update Loop submodule with compile error fixes"')
