import subprocess
import shutil
from pathlib import Path
import sys

# -----------------------------
# CONFIGURATION
# -----------------------------
PYTHON_EXE = "python11"  # Change if different Python executable
PACKAGE_DIR = Path(__file__).parent
DIST_DIR = PACKAGE_DIR / "dist"
EGG_INFO_DIR = next(PACKAGE_DIR.glob("*.egg-info"), None)
TWINE_REPO = "testpypi"  # Change to 'pypi' for production
# -----------------------------

def run(cmd, check=True):
    """Run a shell command and stream output."""
    print(f"\n>>> Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=check)

def clean():
    """Delete old build artifacts."""
    if DIST_DIR.exists():
        print(f"Deleting old dist folder: {DIST_DIR}")
        shutil.rmtree(DIST_DIR)
    if EGG_INFO_DIR and EGG_INFO_DIR.exists():
        print(f"Deleting old egg-info folder: {EGG_INFO_DIR}")
        shutil.rmtree(EGG_INFO_DIR)

def build():
    """Build wheel and sdist without isolation."""
    run([PYTHON_EXE, "-m", "build", "--no-isolation"])

def upload():
    """Upload built distributions to TestPyPI (or PyPI)."""
    dist_files = list(DIST_DIR.glob("*"))
    if not dist_files:
        print("No distribution files found! Did the build fail?")
        sys.exit(1)
    run([PYTHON_EXE, "-m", "twine", "upload", "--verbose", "--repository", TWINE_REPO, str(DIST_DIR / "*")])

def main():
    clean()
    build()
    upload()
    print("\n✅ Distribution process complete!")

if __name__ == "__main__":
    main()
