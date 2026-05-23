import subprocess
import os
import shutil

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd} in {cwd or '.'}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

# Setup git config
run('git config user.name "Allen"')
run('git config user.email "allen@example.com"')

# Ensure branch
run("git checkout caresens_integration")

# Remove existing Loop
if os.path.exists("Loop"):
    run("git rm -rf Loop")
    run('git commit -m "Remove placeholder Loop submodule"')
    if os.path.exists(".gitmodules"):
        run("git rm -f .gitmodules")

# Remove .git/modules/Loop just in case
git_module_path = os.path.join(".git", "modules", "Loop")
if os.path.exists(git_module_path):
    import shutil
    shutil.rmtree(git_module_path, ignore_errors=True)

# Add new submodule
run("git submodule add -f https://github.com/allenst486dbxdripswift/Loop Loop")
run('git commit -m "Add new Loop submodule for caresens integration"')

# Inside Loop submodule
loop_dir = os.path.join(os.getcwd(), "Loop")
if os.path.exists(loop_dir):
    run('git config user.name "Allen"', cwd=loop_dir)
    run('git config user.email "allen@example.com"', cwd=loop_dir)
    
    # Try creating branch, if fails, just checkout
    run("git checkout caresens_integration || git checkout -b caresens_integration", cwd=loop_dir)
