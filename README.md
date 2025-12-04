# 🎉 **CustomCTkDialog**

### *Beautiful dialogs, alerts, and native file pickers for CustomTkinter — powered by a lightweight executable.*

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/customtkinter-5.2%2B-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/platform-windows-lightgray?style=for-the-badge" />
</p>

## ✨ Features

✔️ **Modern dialogs** that blend perfectly with CustomTkinter
✔️ **Custom alert boxes** with multiple alert types
✔️ **Native-feeling folder picker** powered by a bundled executable
✔️ Plug-and-play — no configuration required
✔️ Clean, Pythonic API

## 🚀 Installation

```
pip install CustomCTkDialog
```

## 📦 Project Structure

```
CustomCTkDialog/
│
├── CustomCTkDialog/              # Python package
│   ├── __init__.py
│   ├── custom_ctk_dialog.py      # Main dialog system
│   ├── folder_picker.exe         # Bundled native file-picker
│
├── js-file-picker/               # JS workspace (NOT included in final PyPI package)
│   ├── file-picker.js
│   ├── package.json
│   ├── node_modules/
│   └── build scripts
│
├── example/
│   └── app.py                    # Example usage
│
├── README.md
└── pyproject.toml
```

📝 **Note:**
Everything inside `js-file-picker/` is for **developers only**.
The published Python package includes **only** the dialog system and the built executable.

## 🧪 Example Usage

```python
from CustomCTkDialog import Dialog, folder_picker, file_picker, AlertType

def main():
    # test prompt
    try:
        name = Dialog.prompt("Enter your name:", default_text="Alice")
        print("Prompt returned:", name)
    except ValueError as error:
        print("Prompt canceled:", error)

    # test confirm
    confirmed = Dialog.confirm("Do you want to continue?")
    print("Confirm returned:", confirmed)

    # test alert
    Dialog.alert(AlertType.SUCCESS, "Test Alert", "This is a success alert!")

    # test file picker
    files = file_picker(initialdir="D:/")
    print("Selected files:", files)

    # test folder picker
    directories = folder_picker(default_path="D:/")
    print("Selected folders:", directories)

if __name__ == "__main__":
    main()
```

## 🧰 API Reference

### `Dialog` class

| Method      | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `prompt()`  | Shows an input dialog, returns string or raises `ValueError`. |
| `confirm()` | Shows a yes/no dialog, returns boolean.                       |
| `alert()`   | Shows an alert with `AlertType`.                              |

### `folder_picker()`

Opens a native-feeling folder picker powered by a lightweight executable.

```python
paths = folder_picker()
```

### `file_picker()`

Simple wrapper around `tkinter.filedialog.askopenfilenames`.

```python
files = file_picker()
```

## 🛠 Development

### 1. Install Python dependencies

```
pip install -r requirements.txt
```

### 2. Run the example app

```
python example/app.py
```

### 3. Rebuild the JS file-picker (optional, developers only)

```
cd js-file-picker
npm install
npm run build
```

Copy the resulting executable to:

```
CustomCTkDialog/folder_picker.exe
```

## 📦 Build & Publish (for maintainers only)

### Build the package

```
python -m build
```

## 🔒 TestPyPI & PyPI Upload Permissions (Important)

Only the **project owner** and any **maintainers they explicitly add** can upload new versions of this package to:

* **TestPyPI**
* **PyPI**

Other users **cannot upload**, even if they have:

❌ Their own API token
❌ Their own TestPyPI/PyPI account
❌ A local project with the same name

Publishing requires **project-level permissions**, not just an account.

If someone wants to help publish new versions or become a maintainer, they can:

👉 Open an issue
👉 Contact the project developer
👉 Request to be added under **Settings → Collaborators**

Once added as a maintainer, they can upload using **their own API token**.

## 🤝 Contributing

Pull requests are welcome!
If you're improving the JS file-picker, make changes in:

```
/js-file-picker/
```

Then rebuild and replace the executable inside the Python package.

## 📝 License

### **Creative Commons Attribution–NonCommercial 4.0 (CC BY-NC 4.0)**
