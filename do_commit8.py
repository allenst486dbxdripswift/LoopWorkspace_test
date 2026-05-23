import os
import subprocess

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd} in {cwd or '.'}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

loop_dir = os.path.join(os.getcwd(), "Loop")

run('git add Modules/CareSensAirCGMPlugin.swift', cwd=loop_dir)
run('git commit -m "Add missing glucoseDisplay and debugDescription properties to conform to CGMManager"', cwd=loop_dir)
run('git push origin caresens_integration', cwd=loop_dir)

run('git add Loop')
run('git commit -m "Update Loop submodule with additional CGMManager protocol conformances"')
run('git push origin caresens_integration')
