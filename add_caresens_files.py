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

# 1. Fix CareSensAirCGMPlugin.swift sourceTree
old_ref = 'FA4444444444444444444444 /* CareSensAirCGMPlugin.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = CareSensAirCGMPlugin.swift; path = Modules/CareSensAirCGMPlugin.swift; sourceTree = "<group>"; };'
new_ref = 'FA4444444444444444444444 /* CareSensAirCGMPlugin.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = CareSensAirCGMPlugin.swift; path = Modules/CareSensAirCGMPlugin.swift; sourceTree = SOURCE_ROOT; };'
content = content.replace(old_ref, new_ref)

files_to_add = [
    ("CareSensAirCrypto.swift", "Modules/CareSensAirCrypto.swift", "FA5555555555555555555551", "FA6666666666666666666661"),
    ("CareSensAirPeripheralManager.swift", "Modules/CareSensAirPeripheralManager.swift", "FA5555555555555555555552", "FA6666666666666666666662"),
    ("PacketParser.swift", "Parsers/PacketParser.swift", "FA5555555555555555555553", "FA6666666666666666666663"),
    ("GlucoseConverter.swift", "Modules/GlucoseConverter.swift", "FA5555555555555555555554", "FA6666666666666666666664"),
]

for name, path, build_uuid, ref_uuid in files_to_add:
    if name not in content:
        build_str = f"{build_uuid} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {ref_uuid} /* {name} */; }};"
        ref_str = f'{ref_uuid} /* {name} */ = {{isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = {name}; path = {path}; sourceTree = SOURCE_ROOT; }};'
        
        content = content.replace("/* Begin PBXBuildFile section */", f"/* Begin PBXBuildFile section */\n\t\t{build_str}")
        content = content.replace("/* Begin PBXFileReference section */", f"/* Begin PBXFileReference section */\n\t\t{ref_str}")
        
        # Add to PBXGroup (same group as CGMManager)
        content = re.sub(r'(/\* CGMManager\.swift \*/,)', f'\\1\n\t\t\t\t{ref_uuid} /* {name} */,', content)
        
        # Add to PBXSourcesBuildPhase
        content = re.sub(r'(/\* CGMManager\.swift in Sources \*/,)', f'\\1\n\t\t\t\t{build_uuid} /* {name} in Sources */,', content)

with open(pbxproj_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated project.pbxproj with all CareSens files")

# Commit
loop_dir = os.path.join(os.getcwd(), "Loop")
run("git add Loop.xcodeproj/project.pbxproj", cwd=loop_dir)
run('git add Modules/CareSensAirCrypto.swift Modules/CareSensAirPeripheralManager.swift Modules/GlucoseConverter.swift Parsers/PacketParser.swift', cwd=loop_dir)
run('git commit -m "Fix project file references and add missing CareSens files"', cwd=loop_dir)
run('git push origin caresens_integration', cwd=loop_dir)

run("git add Loop")
run('git commit -m "Update Loop submodule after fixing Xcode project files"')
run("git push origin caresens_integration")
