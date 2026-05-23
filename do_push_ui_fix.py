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

# Stage the modified files
run("git add Modules/CareSensAirCGMPlugin.swift", cwd=loop_dir)
run("git add Loop/Managers/CGMManager.swift", cwd=loop_dir)

# Commit
run('git commit -m "Expose CareSens Air CGM plugin in UI (CGMManagerUIPlugin + static registration)"', cwd=loop_dir)

# Push the submodule
run("git push origin caresens_integration", cwd=loop_dir)

# Back to LoopWorkspace_test
run("git add Loop")
run('git commit -m "Update Loop submodule to latest commit with UI fix"')
run("git push origin caresens_integration")
