# setup.py

import os
import sys
from setuptools import setup
from setuptools.command.install import install as _install
 
# --- Configuration ---
ELECTRON_EXE_NAME = "folder-picker.exe"
ELECTRON_RELEASE_URL = "https://github.com/AceBurgundy/CustomCTkDialog/releases/download/v1.0.0/folder-picker-1.0.0.zip"
# ---------------------

class CustomInstall(_install):
    """Custom install command that downloads the electron binary."""
    def run(self):
        self.execute(self.download_electron_binary, (), msg="Downloading Electron binary...")
        _install.run(self)
        
    def download_electron_binary(self):
        """
        Downloads and extracts the electron binary (ZIP).
        This runs BEFORE the setuptools installation process.
        """
        try:
            import requests # We will need to ensure this is available
            import zipfile
            import io
        except ImportError:
            # This is a key requirement for the custom script to work
            print("ERROR: requests and zipfile are required for custom installation.")
            sys.exit(1)

        print(f"Starting download from: {ELECTRON_RELEASE_URL}")
        
        # 1. Download the ZIP file content
        response = requests.get(ELECTRON_RELEASE_URL, stream=True)
        response.raise_for_status() 

        # 2. Extract the EXE from the ZIP directly into the package directory
        target_dir = os.path.join(self.install_lib, 'CustomCTkDialog')
        os.makedirs(target_dir, exist_ok=True)
        
        # Use io.BytesIO to handle the downloaded content in memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # The executable must be the only thing in the ZIP or we must know its exact name
            # Assuming the EXE is directly inside the ZIP
            try:
                # Assuming the EXE name is the same as the name inside the ZIP
                z.extract(ELECTRON_EXE_NAME, target_dir) 
                print(f"Successfully extracted {ELECTRON_EXE_NAME} to {target_dir}")
            except KeyError:
                print(f"ERROR: Could not find {ELECTRON_EXE_NAME} inside the downloaded ZIP file.")
                sys.exit(1)


# The setup call only needs to define the custom command
setup(
    cmdclass={
        'install': CustomInstall,
    },
)