import os
import subprocess

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=r"f:\AI_Project\Anitigravity\Loop_addCS\LoopWorkspace_test")
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
    return result.returncode

def main():
    run_cmd("git add -A")
    run_cmd('git commit -m "Fix CI: remove invalid set_keychain_settings action"')
    run_cmd("git push origin caresens_integration")

if __name__ == "__main__":
    main()
