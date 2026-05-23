import os
import re
import subprocess

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd} in {cwd or '.'}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

pbxproj_path = os.path.join("Loop", "Loop.xcodeproj", "project.pbxproj")

with open(pbxproj_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the incorrect sourceTree = "<group>" with sourceTree = SOURCE_ROOT
old_ref = 'FA4444444444444444444444 /* CareSensAirCGMPlugin.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = CareSensAirCGMPlugin.swift; path = Modules/CareSensAirCGMPlugin.swift; sourceTree = "<group>"; };'
new_ref = 'FA4444444444444444444444 /* CareSensAirCGMPlugin.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = CareSensAirCGMPlugin.swift; path = Modules/CareSensAirCGMPlugin.swift; sourceTree = SOURCE_ROOT; };'

if old_ref in content:
    content = content.replace(old_ref, new_ref)
    with open(pbxproj_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed CareSensAirCGMPlugin.swift sourceTree to SOURCE_ROOT in project.pbxproj")
else:
    print("Could not find the old reference. Checking if it's already fixed...")
    if new_ref in content:
        print("Already fixed.")
    else:
        print("Warning: FA4444444444444444444444 not found at all.")

# Commit changes
loop_dir = os.path.join(os.getcwd(), "Loop")
run("git add Loop.xcodeproj/project.pbxproj", cwd=loop_dir)
run('git commit -m "Fix CareSensAirCGMPlugin path resolution in project.pbxproj"', cwd=loop_dir)
run('git push origin caresens_integration', cwd=loop_dir)

run("git add Loop")
run('git commit -m "Update Loop submodule for path resolution fix"')
run("git push origin caresens_integration")
