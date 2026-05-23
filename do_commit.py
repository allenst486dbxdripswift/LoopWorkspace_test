import subprocess

def run(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

run('git add OverrideAssetsLoop.xcassets/AppIcon.appiconset/*')
run('git commit -m "Fix AppIcon files for App Store validation"')
run('git push origin caresens_integration')
