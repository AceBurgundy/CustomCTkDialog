from customtkinter import CTk, CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkFont, set_appearance_mode # type: ignore
from typing import Any, Dict, Optional, List, cast, Callable
from tkinter import PhotoImage, Tk, filedialog
from pathlib import Path
from enum import Enum
import subprocess
import time
import json
import os
import sys

MIN_WINDOW_WIDTH: int = 500
BUTTON_SPACING: int = 10
MESSAGE_MAX_LENGTH: int = 500
PACKAGE_DIR: Path = Path(__file__).parent
EXE_PATH: str = str(PACKAGE_DIR / "folder-picker-1.0.2.exe")

class AlertType(Enum):
    """
    Types of alerts for visual differentiation.
    
    >>> AlertType.INFO: # Informational alert.
    >>> AlertType.SUCCESS: # Success alert.
    >>> AlertType.WARNING: # Warning alert.
    >>> AlertType.ERROR: # Error alert.
    """
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

def folder_picker(
    initialdir: Optional[str] = None,
    return_full_paths: bool = True,
    title: Optional[str] = None,
    multi_folder: bool = True
) -> List[str]:
    """
    Runs the external multi-folder picking utility and returns selected folder paths.

    Arguments
    ------------
    initialdir (str | None): Initial directory path for the picker dialog.
    return_full_paths (bool): Whether to return full folder paths.
    title (str | None): Title of the picker dialog window.
    multi_folder (bool): Whether multiple folder selection is allowed.

    Returns
    ---------
    selected_paths (List[str]): List of selected folder paths.
    """
    command: List[str] = [EXE_PATH]

    if initialdir:
        command.append(f'--default_path={initialdir}')

    command.append(f"--return_full_paths={str(return_full_paths).lower()}")

    if title:
        command.append(f'--title={title}')

    command.append(f"--multi-folder={str(multi_folder).lower()}")

    try: 
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.stderr:
            print("--- Picker STDERR ---\n", result.stderr.strip(), "\n---------------------")            
        
        json_output: str = result.stdout.strip()  

        if not json_output:
            return []      
              
        parsed = json.loads(json_output)
        return parsed if isinstance(parsed, list) else []

    except FileNotFoundError:
        print(f"Picker EXE not found at {EXE_PATH}.")
        return []

    except subprocess.CalledProcessError as error:
        print(f"Error running folder picker: {error.stderr.strip() if error.stderr else error}")
        return []

    except json.JSONDecodeError:
        print("Picker output was not valid JSON.")
        return []

def file_picker(
    initialdir: str = os.getcwd(),
    title: str = "Select Files",
    return_full_paths: bool = True,
    preferred_icon_path: Optional[str] = None
) -> List[str]:
    """
    A wrapper around tkinter's filedialog to pick one or more files.
    Opens a file picker dialog and returns a list of selected file paths or names.

    Arguments
    ---------
        initialdir (str): The initial directory the dialog opens to.
        title (str): The title of the file picker window.
        return_full_paths (bool): If True, returns full paths. If False, returns only the base filename (basename).
        preferred_icon_path (Optional[str]): Path to a .png or .gif image file to use as the window icon.

    Returns
    -------
        List[str] - files chosen by the user, or [] if cancelled.
    """
    root_window: Tk = Tk()

    if preferred_icon_path:
        try:
            icon_image = PhotoImage(file=preferred_icon_path)
            root_window.iconphoto(True, icon_image)
        except Exception as error:
            print(f"Warning: Could not set icon from path '{preferred_icon_path}'. Error: {error}")

    root_window.withdraw()

    file_paths_tuple = filedialog.askopenfilenames(
        initialdir=initialdir,
        title=title,
    )        
    
    try:
        root_window.destroy()
    except:
        pass

    file_paths = list(file_paths_tuple)

    if not file_paths:
        return []

    return file_paths if return_full_paths else [os.path.basename(path) for path in file_paths]
        
class Dialog:

    @staticmethod
    def _destroy_silently(window: CTk) -> None:
        """
        Destroys the window while suppressing background Tcl error output.
        """
        # Save original stderr
        original_stderr = sys.stderr
        
        try:
            # Redirect stderr to nowhere
            sys.stderr = open(os.devnull, 'w')
            
            # Attempt to cancel any scheduled "after" events
            try:
                for after_id in window.tk.eval('after info').split():
                    window.after_cancel(after_id)
            except:
                pass
                
            window.destroy()
            
        except:
            pass
            
        finally:
            # Restore stderr
            sys.stderr = original_stderr

class Dialog:

    @staticmethod
    def _create_new_window(window_title: str) -> CTk:
        """
        Creates a CTk window without the white flash.
        """
        new_window: CTk = CTk()        
        new_window.withdraw()        
        set_appearance_mode("Dark")        
        new_window.configure(fg_color="#242424") 
        
        new_window.resizable(0, 0)
        new_window.title(window_title)
        
        return new_window
    
    @staticmethod
    def _force_foreground(window: CTk) -> None:
        """
        Forces the given window to the foreground with a custom fade-in animation
        to avoid white flashes and the lack of native OS animation.
        """
        # 1. Start completely transparent
        window.attributes("-alpha", 0.0)
        
        # 2. Map the window to the screen (it's invisible, so it flashes off-screen/transparently)
        window.deiconify()
        
        # 3. Force rendering while transparent
        window.update_idletasks()
        window.update() 
        
        # 4. Custom Fade-In Animation
        # We step from 0.0 to 1.0. 
        # Adjust 'steps' for smoothness and 'delay' for speed.
        steps = 10
        for i in range(1, steps + 1):
            alpha = i / steps
            window.attributes("-alpha", alpha)
            window.update() # Force the OS to redraw the window at this transparency
            time.sleep(0.01) # 10ms delay per frame (~100ms total animation)

        # 5. Ensure final state is opaque and focused
        window.attributes("-alpha", 1.0)
        window.lift()
        
        try:
            window.attributes("-topmost", True)
            window.update()
            window.attributes("-topmost", False)
        except:
            pass
        window.focus_force()

    @staticmethod
    def _safe_finish(window: CTk) -> None:
        """
        Cleanly exits and prevents the ghost window issue.
        """
        try:
            # Hide immediately so the user thinks it's closed
            window.withdraw() 
            
            # Silent background cleanup
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, 'w')
            
            try:
                # Cancel pending animations to stop Tcl errors
                for after_id in window.tk.eval('after info').split():
                    window.after_cancel(after_id)
                
                window.quit()
                window.destroy()
            finally:
                sys.stderr = original_stderr
        except:
            pass

    @staticmethod
    def _truncate_message(message: str, max_chars: int = MESSAGE_MAX_LENGTH) -> str:
        """
        Truncate the message to max_chars and add ellipsis if necessary.
        """
        if len(message) <= max_chars:
            return message
        
        return message[:max_chars - 3] + "..."

    @staticmethod
    def _center_app(app: CTk, dialog_width: int, dialog_height: int) -> None:
        """
        Centers the given app window on the screen with specified width and height.

        Arguments
        ---------
            app (CTk): The CTk application window to center.
            dialog_width (int): The width of the dialog window.
            dialog_height (int): The height of the dialog window.
        """
        screen_width, screen_height = app.winfo_screenwidth(), app.winfo_screenheight()
        center_x: int = int(screen_width / 2 - dialog_width / 2)
        center_y: int = int(screen_height / 2 - dialog_height / 2)
        
        app.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")

    @staticmethod
    def _block_process_until_result(flag_container: dict, key: str, app: CTk, poll_interval: float = 0.01) -> None:
        """
        Simple modal wait: process tkinter events until flag_container[key] is set.
        """
        Dialog._force_foreground(app)

        while flag_container.get(key, None) is None:
            try:
                app.update()
                time.sleep(poll_interval)
            except Exception:
                break

    @staticmethod
    def _apply_window_icon(app: CTk, window_icon_path: Optional[str]) -> None:
        """
        Apply a window icon for the current dialog.
        """
        if window_icon_path and os.path.exists(window_icon_path):
            try:
                app.iconbitmap(window_icon_path)
            except Exception as error:
                print(f"Failed to set window icon: {error}")

    @classmethod
    def _base_input_dialog(
        cls,
        message: str,
        *,
        is_input: bool = True,
        default_text: str = "",
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        window_title: Optional[str] = None,
        width: int = MIN_WINDOW_WIDTH,
        window_icon_path: Optional[str] = None,
    ) -> Optional[object]:
        """
        Shared private helper for input-like dialogs.
        """
        if not message:
            raise ValueError("A message must be provided for input dialogs.")

        CANCEL_SIGNAL = object()
        
        dialog_window: CTk = cls._create_new_window(window_title or "Application")
        
        cls._apply_window_icon(dialog_window, window_icon_path)

        dialog_window.grid_rowconfigure(0, weight=0)
        dialog_window.grid_rowconfigure(1, weight=1)
        dialog_window.grid_rowconfigure(2, weight=0)
        dialog_window.grid_columnconfigure(0, weight=1)

        result_container: Dict[Any, Optional[Any]] = {"value": None}

        def _do_cancel() -> None:
            result_container["value"] = CANCEL_SIGNAL

        def _do_confirm() -> None:
            if is_input and input_entry:
                value = input_entry.get().strip()
                result_container["value"] = value if value else ""
            else:
                result_container["value"] = True

        truncated_message: str = cls._truncate_message(message, MESSAGE_MAX_LENGTH)
        
        message_label: CTkLabel = CTkLabel(
            dialog_window, text=truncated_message, font=CTkFont(size=14),
            wraplength=width - 40, justify="left", fg_color="#242424"
        )
        
        message_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        input_entry: Optional[CTkEntry] = None
        
        if is_input:
            input_entry = CTkEntry(dialog_window, placeholder_text="Enter your required input here...", font=CTkFont(size=14), fg_color="#242424")
            input_entry.insert(0, default_text)
            input_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        button_frame: CTkFrame = CTkFrame(dialog_window, fg_color="#242424")
        button_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="se")

        CTkButton(button_frame, text=cancel_text, command=_do_cancel).grid(row=0, column=0, padx=(0, BUTTON_SPACING))
        CTkButton(button_frame, text=confirm_text, command=_do_confirm).grid(row=0, column=1)

        dialog_window.update_idletasks()

        requested_width = max(width, dialog_window.winfo_reqwidth())
        requested_height = dialog_window.winfo_reqheight()

        cls._center_app(dialog_window, requested_width, requested_height)

        dialog_window.protocol("WM_DELETE_WINDOW", _do_cancel)
        dialog_window.bind("<Return>", lambda e=None: _do_confirm())
        dialog_window.bind("<Escape>", lambda e=None: _do_cancel())
        
        if input_entry:
            input_entry.focus_set()

        cls._block_process_until_result(result_container, "value", dialog_window)
        
        final_value = result_container["value"]
        
        # Using the silent destruction logic here
        cls._safe_finish(dialog_window)
        
        if final_value is CANCEL_SIGNAL:
            if is_input:
                raise ValueError("Input required: Dialog was canceled.")
            return False

        if is_input:
            if not final_value and final_value != "":
                raise ValueError("Input required: blank input.")
            return final_value

        return bool(final_value)

    @classmethod
    def prompt(cls, message: str, default_text: str = "") -> str:
        """
        Show a prompt dialog to get text input from the user.
        """
        return cast(str, cls._base_input_dialog(
                message, is_input=True, default_text=default_text,
                confirm_text="Confirm", cancel_text="Cancel",
                window_title="Input Required"
            )
        )

    @classmethod
    def confirm(cls, message: str) -> bool:
        """
        Show a confirm (yes/no) dialog.
        """
        return cast(bool, cls._base_input_dialog(
                message, is_input=False,
                confirm_text="Yes", cancel_text="No",
                window_title="Confirm")
        )

    @classmethod
    def _base_alert_dialog(
        cls,
        title: Optional[str],
        message: str,
        *,
        icon: Optional[str] = None,
        kind: AlertType = AlertType.INFO,
        width: int = MIN_WINDOW_WIDTH,
    ) -> None:
        """
        Base alert dialog: draws message + single dismiss/ok button.
        """
        if message is None:
            raise ValueError("Alert message must be provided.")

        dialog_window: CTk = cls._create_new_window(title or kind.name.title())
        dialog_window.grid_columnconfigure(0, weight=1)

        default_icons = {AlertType.INFO: "ℹ️", AlertType.SUCCESS: "✅", AlertType.WARNING: "⚠️", AlertType.ERROR: "❌"}
        display_icon = icon if icon is not None else default_icons.get(kind, "")

        top_frame: CTkFrame = CTkFrame(dialog_window, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        if display_icon:
            CTkLabel(top_frame, text=display_icon, font=CTkFont(size=24)).grid(row=0, column=0, padx=(0, 10), sticky="nw")

        truncated_message = cls._truncate_message(message, MESSAGE_MAX_LENGTH)
        
        CTkLabel(top_frame, text=truncated_message, fg_color="#242424", font=CTkFont(size=14), wraplength=width-120, justify="left").grid(row=0, column=1, sticky="nw")

        button_frame: CTkFrame = CTkFrame(dialog_window, fg_color="#242424")
        button_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="se")

        result_container: Dict[str, Optional[bool]] = {"value": None}
        
        def _dismiss(): result_container["value"] = True
        
        CTkButton(button_frame, text="OK", command=_dismiss).grid(row=0, column=0)

        dialog_window.update_idletasks()

        cls._center_app(dialog_window, max(width, dialog_window.winfo_reqwidth()), dialog_window.winfo_reqheight())

        dialog_window.protocol("WM_DELETE_WINDOW", _dismiss)
        
        dialog_window.bind("<Return>", lambda e=None: _dismiss())
        dialog_window.bind("<Escape>", lambda e=None: _dismiss())

        cls._block_process_until_result(result_container, "value", dialog_window)
        
        # Using the silent destruction logic here
        cls._safe_finish(dialog_window)

        if dialog_window.winfo_exists():
            dialog_window.destroy()
            
    @classmethod
    def alert(cls, kind: AlertType, title: Optional[str], message: str, icon: Optional[str] = None) -> None:
        """
        Public alert helper.
        """
        cls._base_alert_dialog(title, message, icon=icon, kind=kind)