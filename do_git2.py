import subprocess
import os

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd} in {cwd or '.'}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

# Reset to restore .gitmodules
run("git reset --hard HEAD~1")
run("git checkout .gitmodules")

# Ensure .gitmodules exists
if not os.path.exists(".gitmodules"):
    run("git checkout main -- .gitmodules")

run("git submodule add -f https://github.com/allenst486dbxdripswift/Loop Loop")
run('git commit -m "Add new Loop submodule for caresens integration"')

# Inside Loop submodule
loop_dir = os.path.join(os.getcwd(), "Loop")
if os.path.exists(loop_dir):
    run('git config user.name "Allen"', cwd=loop_dir)
    run('git config user.email "allen@example.com"', cwd=loop_dir)
    
    # Try creating branch, if fails, just checkout
    run("git checkout caresens_integration || git checkout -b caresens_integration", cwd=loop_dir)
