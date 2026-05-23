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

# Path to project
pbxproj_path = os.path.join("Loop", "Loop.xcodeproj", "project.pbxproj")

with open(pbxproj_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add to project.pbxproj if not present
if "CareSensAirCGMPlugin.swift" not in content:
    print("Modifying project.pbxproj to include CareSensAirCGMPlugin.swift")
    build_file = "FA3333333333333333333333 /* CareSensAirCGMPlugin.swift in Sources */ = {isa = PBXBuildFile; fileRef = FA4444444444444444444444 /* CareSensAirCGMPlugin.swift */; };"
    file_ref = 'FA4444444444444444444444 /* CareSensAirCGMPlugin.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = CareSensAirCGMPlugin.swift; path = Modules/CareSensAirCGMPlugin.swift; sourceTree = "<group>"; };'
    
    # Insert PBXBuildFile
    content = content.replace("/* Begin PBXBuildFile section */", "/* Begin PBXBuildFile section */\n\t\t" + build_file)
    # Insert PBXFileReference
    content = content.replace("/* Begin PBXFileReference section */", "/* Begin PBXFileReference section */\n\t\t" + file_ref)
    
    # Insert into PBXGroup (Find CGMManager.swift and insert ours after it)
    content = re.sub(r'(/\* CGMManager\.swift \*/,)', r'\1\n\t\t\t\tFA4444444444444444444444 /* CareSensAirCGMPlugin.swift */,', content)
    
    # Insert into PBXSourcesBuildPhase
    content = re.sub(r'(/\* CGMManager\.swift in Sources \*/,)', r'\1\n\t\t\t\tFA3333333333333333333333 /* CareSensAirCGMPlugin.swift in Sources */,', content)

    # Also add CURRENT_PROJECT_VERSION just in case
    if "CURRENT_PROJECT_VERSION" not in content:
        print("Adding CURRENT_PROJECT_VERSION = 19")
        content = re.sub(r'(INFOPLIST_FILE = "Loop/Info\.plist";)', r'\1\n\t\t\t\tCURRENT_PROJECT_VERSION = 19;', content)

    with open(pbxproj_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Modifications saved.")
else:
    print("CareSensAirCGMPlugin.swift already in project.pbxproj")

# Now commit
loop_dir = os.path.join(os.getcwd(), "Loop")
run("git add Loop.xcodeproj/project.pbxproj", cwd=loop_dir)
run("git add Modules/CareSensAirCGMPlugin.swift", cwd=loop_dir)
run('git commit -m "Add CareSensAirCGMPlugin.swift to Xcode project to fix scope errors"', cwd=loop_dir)
run('git push origin caresens_integration', cwd=loop_dir)

run("git add Loop")
run('git commit -m "Update Loop submodule with Xcode project fixes"')
run("git push origin caresens_integration")
