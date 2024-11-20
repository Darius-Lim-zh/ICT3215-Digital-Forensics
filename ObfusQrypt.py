import sys

import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, BooleanVar, IntVar
import os
from PIL import Image, ImageTk
import Code_Embedding.code_embedder as ce
import Quantum_Polymorphism.QMorph as qm
import glob  # For file pattern matching
from pathlib import Path
from Excel.embed_excel import embed_python_script_and_vba
from PDF import embed_pdf_rsa as pdf
from Anti_Decompilation.DynamicCipher import RunTimeDecrypt as dyc
from Anti_Decompilation.PyCCorruptor import PyCCorruptor as pyc
from Anti_Decompilation.CythonCompile import Cython_compiler as cc

from Anti_Decompilation.CythonCompile.compile import compile_with_cython
import Fragmentation_Stego.encode as stego


# To compile into exe
# pyinstaller --onefile --paths=venv/Lib/site-packages --hidden-import customtkinter --hidden-import qiskit --collect-all customtkinter --collect-all qiskit --add-data "assets/ObfusQrypt.ico:assets" --add-data "venv/Lib/site-packages/qiskit_aer/VERSION.txt:qiskit_aer" --noconsole --icon=assets/ObfusQrypt.ico ObfusQrypt.py

class ToolTip:
    """Tooltip class to display tooltips for CustomTkinter widgets with boundary checks and theme awareness."""

    def __init__(self, widget, text, wraplength=300, delay=500):
        """
        Initialize the tooltip with the target widget and the display text.

        :param widget: The widget to which the tooltip is attached.
        :param text: The text to display inside the tooltip.
        :param wraplength: The maximum width of the tooltip in pixels before wrapping.
        :param delay: Delay in milliseconds before showing the tooltip.
        """
        self.widget = widget
        self.text = text
        self.wraplength = wraplength
        self.delay = delay  # Delay before showing tooltip
        self.tooltip_window = None
        self.after_id = None

        # Define colors based on themes
        self.light_bg = "#FFFFE0"  # Light Yellow
        self.dark_bg = "#333333"  # Dark Gray
        self.text_color_light = "black"
        self.text_color_dark = "white"

        # Bind events
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def schedule_tooltip(self, event=None):
        """Schedule the tooltip to be shown after a delay."""
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def show_tooltip(self):
        """Display the tooltip, ensuring it stays within screen boundaries."""
        if self.tooltip_window is not None:
            return  # Tooltip is already visible

        # Get screen dimensions
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()

        # Get widget position and size
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()

        # Create the tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.overrideredirect(True)  # Remove window decorations
        self.tooltip_window.attributes("-topmost", True)  # Keep tooltip above other windows

        # Determine current theme
        current_theme = ctk.get_appearance_mode()  # "Light" or "Dark"

        if current_theme == "Light":
            bg_color = self.light_bg
            text_color = self.text_color_light
        else:
            bg_color = self.dark_bg
            text_color = self.text_color_dark

        # Create the tooltip label with theme-specific colors
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            fg_color=bg_color,  # Background color based on theme
            text_color=text_color,  # Text color based on theme
            wraplength=self.wraplength,
            corner_radius=4,
            padx=5,
            pady=5,
        )
        label.pack()

        # Update the tooltip window to calculate its size
        self.tooltip_window.update_idletasks()

        # Get tooltip size
        tooltip_width = self.tooltip_window.winfo_width()
        tooltip_height = self.tooltip_window.winfo_height()

        # Define larger offsets to prevent overlap
        offset_x = 70  # Increased from 50 to 70
        offset_y = 70  # Increased from 50 to 70

        # Default position: to the right and below the widget
        x = widget_x + widget_width + offset_x
        y = widget_y + offset_y

        # Adjust horizontal position if tooltip goes beyond screen width
        if x + tooltip_width > screen_width:
            x = widget_x - tooltip_width - offset_x

        # Adjust vertical position if tooltip goes beyond screen height
        if y + tooltip_height > screen_height:
            y = widget_y - tooltip_height - offset_y

        # Ensure tooltip does not go off the left or top edge
        if x < 0:
            x = 10  # Small padding from the edge
        if y < 0:
            y = 10  # Small padding from the edge

        # Set the final position of the tooltip
        self.tooltip_window.geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        """Hide and destroy the tooltip window."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def extract_functions_and_imports(filepath):
    """Extract function definitions from the uploaded code file."""
    return ce.extract_functions_and_imports(filepath)


class SplashScreen(ctk.CTkToplevel):
    """Splash Screen Window."""

    def __init__(self, parent, image_path, wait_time=2000):
        super().__init__(parent)
        self.parent = parent
        self.wait_time = wait_time  # Time in milliseconds

        # Remove window decorations
        self.overrideredirect(True)

        # Set window size
        width, height = 400, 300
        self.geometry(f"{width}x{height}")

        # Center the splash screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Set background color
        self.configure(bg="#2B2B2B")  # Dark background

        # Load and display the logo/image
        try:
            image_path = resource_path(image_path)  # Get the correct path
            image = Image.open(image_path)
            image = image.resize((200, 200), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            logo_label = ctk.CTkLabel(self, image=self.photo, text="")
            logo_label.pack(expand=True)
        except Exception as e:
            print(f"Failed to load splash image: {e}")

        # Schedule the splash screen to close and open the main app
        self.after(self.wait_time, self.close_splash)

    def close_splash(self):
        """Close the splash screen and show the main window."""
        self.destroy()
        self.parent.deiconify()  # Show the main window


def resource_path(relative_path):
    """Get the absolute path to a resource. Works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller stores resources in the _MEIPASS folder during runtime
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class CodeEmbedderApp:
    def __init__(self, main_root):
        self.root = main_root
        self.root.title("ObfusQrypt")
        ctk.set_appearance_mode("Dark")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

        # self.root.iconbitmap("assets/ObfusQrypt.ico")
        icon_path = resource_path("assets/ObfusQrypt.ico")
        self.root.iconbitmap(icon_path)

        # Get screen height and set the window max height to the screen height
        screen_height = self.root.winfo_screenheight()
        screen_width = self.root.winfo_screenwidth()

        # Set initial window size (e.g., width: 80% of screen width, height: screen height)
        initial_width = int(screen_width * 0.8)
        self.root.geometry(f"{initial_width}x{screen_height}")

        # Restrict maximum window size to screen dimensions
        self.root.maxsize(screen_width, screen_height)

        # Make the window resizable
        self.root.columnconfigure(0, weight=1)  # Allow the main notebook to expand horizontally
        self.root.rowconfigure(0, weight=1)  # Allow the notebook to expand vertically

        # Main Tabview for tabs
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        # Add the tabs
        self.tabview.add("Code Embedder")
        self.tabview.add("QMorph Malware")
        self.tabview.add("Macro Excel Embedder")
        self.tabview.add("PDF Embedder")
        self.tabview.add("PyCompile Corrupt Magic")
        self.tabview.add("Dynamic Cipher")
        self.tabview.add("Compile with CythonCompile")

        # Switch to first tab
        self.tabview.set("Code Embedder")

        # Add content to each tab
        self.create_code_embedder_tab()
        self.create_qmorph_tab()
        self.create_excel_macro_tab()
        self.create_embed_in_pdf_tab()
        self.create_py_compile_corrupt_tab()
        self.create_dynamic_cipher_tab()
        self.create_cython_tab()

    def create_code_embedder_tab(self):
        """Create the Code Embedder tab with subtabs for different modes."""
        code_embedder_tab = self.tabview.tab("Code Embedder")
        code_embedder_tab.columnconfigure(0, weight=1)
        code_embedder_tab.rowconfigure(0, weight=1)

        # Sub Tabview for different embedding modes
        self.sub_tabview = ctk.CTkTabview(code_embedder_tab)
        self.sub_tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.sub_tabview.add("Self Destruct")
        self.sub_tabview.add("Check for VM")
        self.sub_tabview.add("Custom")

        self.create_self_destruct_subtab()
        self.create_check_vm_subtab()
        self.create_custom_subtab()

    def create_self_destruct_subtab(self):
        """Create the Self Destruct subtab."""
        self.self_destruct_frame = self.sub_tabview.tab("Self Destruct")
        self.self_destruct_frame.columnconfigure(0, weight=1)
        self.self_destruct_frame.rowconfigure(6, weight=1)

        # Variables specific to Self Destruct
        self.self_destruct_code_path = "Self_Destruct/self_destruct_script_poc.py"

        # Malware Code Upload Section
        upload_label = ctk.CTkLabel(self.self_destruct_frame, text="Upload Your Malware Code:")
        upload_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.upload_malware_btn_self_destruct = ctk.CTkButton(
            self.self_destruct_frame, text="Upload Malware Code", command=self.upload_self_destruct_malware
        )
        self.upload_malware_btn_self_destruct.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Tooltip for Upload Button
        info_icon = ctk.CTkLabel(self.self_destruct_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        upload_tooltip_text = "Upload the original malware Python script (.py) that you want to embed with a self-destruct function."
        ToolTip(info_icon, upload_tooltip_text)

        # Label to show upload status
        self.upload_status_self_destruct = ctk.CTkLabel(self.self_destruct_frame, text="No file uploaded.")
        self.upload_status_self_destruct.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Submit Button
        self.self_destruct_submit_btn = ctk.CTkButton(
            self.self_destruct_frame, text="Embed Self Destruct", command=self.submit_self_destruct, width=200
        )
        self.self_destruct_submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # Tooltip for Submit Button
        info_icon_submit = ctk.CTkLabel(self.self_destruct_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_submit.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        submit_tooltip_text = "Click to embed the self-destruct function into the uploaded malware code. The output file will contain the embedded code."
        ToolTip(info_icon_submit, submit_tooltip_text)

        # Success Message Label
        self.success_label_self_destruct = ctk.CTkLabel(self.self_destruct_frame, text="", text_color="white")
        self.success_label_self_destruct.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        # Code Preview Title
        code_preview_title = ctk.CTkLabel(self.self_destruct_frame, text="Code Preview", font=("Arial", 12, "bold"))
        code_preview_title.grid(row=5, column=0, sticky="w", padx=5, pady=(10, 0))

        # Code Preview Text Widget with Scrollbar
        self.code_preview_self_destruct = ctk.CTkTextbox(self.self_destruct_frame, wrap="word", height=18)
        self.code_preview_self_destruct.grid(row=6, column=0, sticky="nsew", padx=5, pady=5)

        self.scrollbar_self_destruct = ctk.CTkScrollbar(self.self_destruct_frame, orientation="vertical",
                                                        command=self.code_preview_self_destruct.yview)

        # Store the uploaded malware path
        self.self_destruct_uploaded_malware = ""

    def upload_self_destruct_malware(self):
        """Handle malware code upload for Self Destruct mode."""
        filepath = filedialog.askopenfilename(
            title="Select Original Malware Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.self_destruct_uploaded_malware = filepath
            self.upload_status_self_destruct.configure(text=f"Uploaded: {os.path.basename(filepath)}")
            # Clear previous success message and code preview
            self.success_label_self_destruct.configure(text="")
            with open(filepath, 'r') as f:
                code = f.read()
            self.code_preview_self_destruct.delete("0.0", "end")
            self.code_preview_self_destruct.insert("0.0", code)

    def submit_self_destruct(self):
        """Embed the self-destruct code into the original malware."""
        if not self.self_destruct_uploaded_malware:
            messagebox.showerror("Error", "Please upload the original malware code file.")
            return

        # Define output file name
        output_file = filedialog.asksaveasfilename(
            title="Save Obfuscated Malware Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
        )
        if not output_file:
            messagebox.showerror("Error", "No output file selected.")
            return

        # Embed the self-destruct function
        status = ce.embed_code(
            embed_code_filenames=[self.self_destruct_code_path],  # Pass as list
            func_names=["secure_delete"],  # Pass as list
            src_code_filename=self.self_destruct_uploaded_malware,
            loc_to_inject="end",  # "main" or "end"
            wrap=False,  # Set to True to inject only after main()
            new_name=output_file,
        )

        if status == 0:
            self.success_label_self_destruct.configure(text=f"Success! Embedded code saved to: {output_file}")
            try:
                with open(output_file, 'r') as f:
                    embedded_code = f.read()
                self.code_preview_self_destruct.delete("0.0", "end")
                self.code_preview_self_destruct.insert("0.0", embedded_code)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the embedded code file: {e}")
        else:
            messagebox.showerror("Error", "An error occurred during embedding.")

    def create_check_vm_subtab(self):
        """Create the Check for VM subtab with tooltips added."""
        self.check_vm_frame = self.sub_tabview.tab("Check for VM")
        self.check_vm_frame.columnconfigure(0, weight=1)
        self.check_vm_frame.rowconfigure(7, weight=1)

        # Variables specific to Check for VM
        self.anti_forensics_dir = "AntiForensics"
        self.vm_checks = []  # List to store selected VM checks
        self.vm_check_vars = {}  # Dictionary to store BooleanVars for checkboxes

        # Malware Code Upload Section
        upload_label = ctk.CTkLabel(self.check_vm_frame, text="Upload Your Malware Code:")
        upload_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.upload_malware_btn_check_vm = ctk.CTkButton(
            self.check_vm_frame, text="Upload Malware Code", command=self.upload_check_vm_malware
        )
        self.upload_malware_btn_check_vm.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Tooltip for Upload Button
        info_icon_upload = ctk.CTkLabel(
            self.check_vm_frame, text="ℹ️", font=("Arial", 14), cursor="hand2"
        )
        info_icon_upload.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        upload_tooltip_text = "Upload the original malware Python script (.py) that you want to embed with VM detection checks."
        ToolTip(info_icon_upload, upload_tooltip_text)

        # Label to show upload status
        self.upload_status_check_vm = ctk.CTkLabel(self.check_vm_frame, text="No file uploaded.")
        self.upload_status_check_vm.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # VM Checks Selection
        vm_checks_label = ctk.CTkLabel(self.check_vm_frame, text="Select VM Detection Checks:")
        vm_checks_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        # Tooltip for VM Checks Selection
        info_icon_vm_checks = ctk.CTkLabel(
            self.check_vm_frame, text="ℹ️", font=("Arial", 14), cursor="hand2"
        )
        info_icon_vm_checks.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        vm_checks_tooltip_text = "Choose the VM detection methods you want to embed into the malware script."
        ToolTip(info_icon_vm_checks, vm_checks_tooltip_text)

        # Frame to hold checkboxes
        self.vm_checks_frame = ctk.CTkFrame(self.check_vm_frame)
        self.vm_checks_frame.grid(row=4, column=0, sticky="nw", padx=10, pady=10)

        # Dynamically load VM detection functions
        self.load_vm_checks()

        # Submit Button
        self.check_vm_submit_btn = ctk.CTkButton(
            self.check_vm_frame, text="Embed VM Checks", command=self.submit_check_vm, width=200
        )
        self.check_vm_submit_btn.grid(row=5, column=0, pady=10, sticky="ew", padx=5)

        # Tooltip for Submit Button
        info_icon_submit = ctk.CTkLabel(
            self.check_vm_frame, text="ℹ️", font=("Arial", 14), cursor="hand2"
        )
        info_icon_submit.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        submit_tooltip_text = "Click to embed the selected VM detection checks into the uploaded malware code. The " \
                              "output file will contain the embedded code."
        ToolTip(info_icon_submit, submit_tooltip_text)

        # Success Message Label
        self.success_label_check_vm = ctk.CTkLabel(self.check_vm_frame, text="", text_color="white")
        self.success_label_check_vm.grid(row=6, column=0, sticky="w", padx=5, pady=5)

        # Code Preview Text Widget with Scrollbar
        self.code_preview_check_vm = ctk.CTkTextbox(self.check_vm_frame, wrap="word", height=15)
        self.code_preview_check_vm.grid(row=7, column=0, sticky="nsew", padx=5, pady=5)

        self.scrollbar_check_vm = ctk.CTkScrollbar(
            self.check_vm_frame, orientation="vertical", command=self.code_preview_check_vm.yview
        )

        # Store the uploaded malware path
        self.check_vm_uploaded_malware = ""

    def upload_check_vm_malware(self):
        """Handle malware code upload for Check for VM mode."""
        filepath = filedialog.askopenfilename(
            title="Select Original Malware Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.check_vm_uploaded_malware = filepath
            self.upload_status_check_vm.configure(text=f"Uploaded: {os.path.basename(filepath)}")
            # Clear previous success message and code preview
            self.success_label_check_vm.configure(text="")
            self.code_preview_check_vm.delete("0.0", "end")

    def load_vm_checks(self):
        """Load VM detection functions from the AntiForensics directory."""
        python_files = glob.glob(os.path.join(self.anti_forensics_dir, "*.py"))
        if not python_files:
            no_checks_label = ctk.CTkLabel(self.vm_checks_frame, text="No VM detection scripts found.")
            no_checks_label.pack()
            return

        for filepath in python_files:
            filename = os.path.basename(filepath)
            if filename.endswith(".py"):
                func_name = f"call_{filename[:-3]}"  # e.g., detect_vmware_dir.py -> call_detect_vmware_dir
                display_name = filename[:-3]  # e.g., detect_vmware_dir
                description = f"Detects VM using {display_name.replace('_', ' ').title()} method."

                var = BooleanVar()
                cb = ctk.CTkCheckBox(self.vm_checks_frame, text=display_name, variable=var)
                cb.pack(anchor="w")
                cb_tooltip = ToolTip(cb, description)
                self.vm_check_vars[func_name] = var

    def submit_check_vm(self):
        """Embed the selected VM checks into the original malware."""
        if not self.check_vm_uploaded_malware:
            messagebox.showerror("Error", "Please upload the original malware code file.")
            return

        # Gather selected VM checks
        selected_checks = [func for func, var in self.vm_check_vars.items() if var.get()]
        if not selected_checks:
            messagebox.showerror("Error", "No VM checks selected.")
            return

        # Define output file name
        output_file = filedialog.asksaveasfilename(
            title="Save Obfuscated Malware Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
        )
        if not output_file:
            messagebox.showerror("Error", "No output file selected.")
            return

        # Prepare lists of embed code filenames and function names
        embed_code_filenames = [os.path.join(self.anti_forensics_dir, f"{func.split('call_')[1]}.py") for func in
                                selected_checks]
        print(f"{embed_code_filenames} ")
        func_names = [func for func in selected_checks]  # Assuming func is already the function name

        # Validate that embed code files exist
        missing_files = [f for f in embed_code_filenames if not os.path.isfile(f)]
        if missing_files:
            messagebox.showerror("Error", f"The following embed code files are missing:\n{', '.join(missing_files)}")
            return

        # Decide on injection parameters based on desired behavior
        loc_to_inject = "main"  # or "end" based on user input
        wrap = True  # Set to True to inject only at specified location

        # Perform embedding using the code_embedder module
        status = ce.embed_code(
            embed_code_filenames=embed_code_filenames,  # Pass as list
            func_names=func_names,  # Pass as list
            src_code_filename=self.check_vm_uploaded_malware,
            loc_to_inject=loc_to_inject,  # "main" or "end"
            wrap=wrap,  # True to inject only at specified location
            new_name=output_file,
        )

        if status == 0:
            self.success_label_check_vm.configure(text=f"Success! Embedded code saved to: {output_file}")
            try:
                with open(output_file, 'r') as f:
                    embedded_code = f.read()
                self.code_preview_check_vm.delete("0.0", "end")
                self.code_preview_check_vm.insert("0.0", embedded_code)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the embedded code file: {e}")
        else:
            messagebox.showerror("Error", "An error occurred during embedding.")

    def create_custom_subtab(self):
        """Create the Custom subtab."""
        self.custom_frame = self.sub_tabview.tab("Custom")
        self.custom_frame.columnconfigure(0, weight=1)
        self.custom_frame.rowconfigure(5, weight=1)
        self.custom_frame.rowconfigure(7, weight=1)

        # Variables for user input
        self.original_code_path_custom = ""
        self.embed_code_path_custom = ""
        self.new_file_name_custom = StringVar()
        self.loc_to_inject_custom = StringVar(value="main")  # Default selection for location
        self.wrap_custom = BooleanVar(value=True)  # Default selection for wrap
        self.selected_function_custom = StringVar()

        # Top Frame for file uploading and showing code
        top_frame = ctk.CTkFrame(self.custom_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        # Original Code Section
        original_label = ctk.CTkLabel(top_frame, text="Your Mal code:")
        original_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.original_file_btn_custom = ctk.CTkButton(
            top_frame, text="Upload Original Code", command=self.load_original_file_custom
        )
        self.original_file_btn_custom.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.show_original_btn_custom = ctk.CTkButton(
            top_frame, text="Show Code", command=self.show_original_code_custom
        )
        self.show_original_btn_custom.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        info_icon = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        original_tooltip_text = "This is where you put your original mal code like rev shells etc."
        ToolTip(info_icon, original_tooltip_text)

        # Spice Code Section
        spice_label = ctk.CTkLabel(top_frame, text="Spice code:")
        spice_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.embed_file_btn_custom = ctk.CTkButton(
            top_frame, text="Upload Embed Code", command=self.load_embed_file_custom
        )
        self.embed_file_btn_custom.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.show_embed_btn_custom = ctk.CTkButton(
            top_frame, text="Show Code", command=self.show_embed_code_custom
        )
        self.show_embed_btn_custom.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        info_icon_spice = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_spice.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        spice_tooltip_text = "This is the spice to be added to your malware (Self destruct feature/VM checker)"
        ToolTip(info_icon_spice, spice_tooltip_text)

        # Status Labels for uploads
        self.upload_status_original = ctk.CTkLabel(self.custom_frame, text="No original code uploaded.")
        self.upload_status_original.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.upload_status_embed = ctk.CTkLabel(self.custom_frame, text="No embed code uploaded.")
        self.upload_status_embed.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Middle Frame for function selection, file name, and options
        middle_frame = ctk.CTkFrame(self.custom_frame)
        middle_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        middle_frame.columnconfigure(1, weight=1)

        # Function selection dropdown
        func_label = ctk.CTkLabel(middle_frame, text="Select Function to Inject:")
        func_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

        self.function_dropdown_custom = ctk.CTkOptionMenu(middle_frame, values=["Menu"])
        self.function_dropdown_custom.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        info_icon_func = ctk.CTkLabel(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_func.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        func_tooltip_text = "Function from your spice to be added to your malware code :)"
        ToolTip(info_icon_func, func_tooltip_text)

        # New File Name entry
        name_label = ctk.CTkLabel(middle_frame, text="New File Name:")
        name_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.file_name_entry_custom = ctk.CTkEntry(middle_frame, textvariable=self.new_file_name_custom)
        self.file_name_entry_custom.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        info_icon_name = ctk.CTkLabel(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_name.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        name_tooltip_text = "Name of the file it will be output to, default is Output/innocent.py"
        ToolTip(info_icon_name, name_tooltip_text)

        # Location to Inject
        loc_label = ctk.CTkLabel(middle_frame, text="Location to Inject:")
        loc_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        self.location_frame_custom = ctk.CTkFrame(middle_frame)
        self.location_frame_custom.grid(row=2, column=1, sticky="ew")

        self.main_button_custom = ctk.CTkButton(
            self.location_frame_custom,
            text="Main",
            command=lambda: self.select_location_custom("main"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            width=80
        )
        self.main_button_custom.pack(side="left", fill="both", expand=True, padx=(0, 2))

        self.end_button_custom = ctk.CTkButton(
            self.location_frame_custom,
            text="End",
            command=lambda: self.select_location_custom("end"),
            fg_color="lightgray",
            hover_color="gray",
            text_color="black",
            width=80
        )
        self.end_button_custom.pack(side="left", fill="both", expand=True, padx=(2, 0))

        info_icon_loc = ctk.CTkLabel(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_loc.grid(row=2, column=2, sticky="w", padx=5, pady=5)
        loc_tooltip_text = "Location in the code where you want to inject the selected function."
        ToolTip(info_icon_loc, loc_tooltip_text)

        # Wrap Main
        wrap_label = ctk.CTkLabel(middle_frame, text="Wrap Main:")
        wrap_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)

        self.wrap_frame_custom = ctk.CTkFrame(middle_frame)
        self.wrap_frame_custom.grid(row=3, column=1, sticky="ew")

        self.yes_button_custom = ctk.CTkButton(
            self.wrap_frame_custom,
            text="Yes",
            command=lambda: self.select_wrap_custom(True),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            width=80
        )
        self.yes_button_custom.pack(side="left", fill="both", expand=True, padx=(0, 2))

        self.no_button_custom = ctk.CTkButton(
            self.wrap_frame_custom,
            text="No",
            command=lambda: self.select_wrap_custom(False),
            fg_color="lightgray",
            hover_color="gray",
            text_color="black",
            width=80
        )
        self.no_button_custom.pack(side="left", fill="both", expand=True, padx=(2, 0))

        info_icon_wrap = ctk.CTkLabel(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_wrap.grid(row=3, column=2, sticky="w", padx=5, pady=5)
        wrap_tooltip_text = "Whether you want to wrap the injected function within an if-else condition pre-running main() function."
        ToolTip(info_icon_wrap, wrap_tooltip_text)

        # Code Preview Title
        code_preview_title = ctk.CTkLabel(self.custom_frame, text="Code Preview", font=("Arial", 12, "bold"))
        code_preview_title.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))

        # Code Display Box (for showing file content)
        self.code_display_box_custom = ctk.CTkTextbox(self.custom_frame, wrap="word", height=10)
        self.code_display_box_custom.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

        # Submit button
        self.submit_btn_custom = ctk.CTkButton(
            self.custom_frame, text="Submit", command=self.submit_custom, width=200
        )
        self.submit_btn_custom.grid(row=6, column=0, pady=10, sticky="ew")

        # Result display (resizable) with Scrollbar
        self.result_box_custom = ctk.CTkTextbox(self.custom_frame, wrap="word", height=10)
        self.result_box_custom.grid(row=7, column=0, sticky="nsew", padx=10, pady=10)

        self.scrollbar_custom = ctk.CTkScrollbar(self.custom_frame, orientation="vertical",
                                                 command=self.result_box_custom.yview)
        # self.scrollbar_custom.grid(row=7, column=1, sticky="ns", pady=10)
        # self.result_box_custom.configure(yscrollcommand=self.scrollbar_custom.set)

        # Store uploaded file paths
        self.custom_uploaded_original = ""
        self.custom_uploaded_embed = ""

    def select_wrap_custom(self, wrap_value):
        """Select wrap option and update button colors for Custom mode."""
        self.wrap_custom.set(wrap_value)
        if wrap_value:
            self.yes_button_custom.configure(fg_color="#4CAF50", text_color="white")
            self.no_button_custom.configure(fg_color="lightgray", text_color="black")
        else:
            self.yes_button_custom.configure(fg_color="lightgray", text_color="black")
            self.no_button_custom.configure(fg_color="#4CAF50", text_color="white")

    def select_location_custom(self, location):
        """Select a location and update button colors for Custom mode."""
        self.loc_to_inject_custom.set(location)
        if location == "main":
            self.main_button_custom.configure(fg_color="#4CAF50", text_color="white")
            self.end_button_custom.configure(fg_color="lightgray", text_color="black")
        else:
            self.main_button_custom.configure(fg_color="lightgray", text_color="black")
            self.end_button_custom.configure(fg_color="#4CAF50", text_color="white")

    def create_dynamic_cipher_tab(self):
        """Create the Dynamic Cipher tab for runtime encryption and decryption of Python scripts."""
        self.dynamic_cipher_frame = self.tabview.tab("Dynamic Cipher")
        self.dynamic_cipher_frame.columnconfigure(0, weight=1)
        self.dynamic_cipher_frame.columnconfigure(1, weight=0)  # Reserved for scrollbar
        self.dynamic_cipher_frame.rowconfigure(2, weight=1)  # Code preview
        self.dynamic_cipher_frame.rowconfigure(5, weight=1)  # Result preview

        # Top Frame for file uploading and showing code
        top_frame = ctk.CTkFrame(self.dynamic_cipher_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        # File Upload Section
        upload_label = ctk.CTkLabel(top_frame, text="Your Python Code:")
        upload_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)

        self.upload_dynamic_cipher_btn = ctk.CTkButton(
            top_frame, text="Upload Python Code", command=self.load_dynamic_cipher_file
        )
        self.upload_dynamic_cipher_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.show_dynamic_cipher_code_btn = ctk.CTkButton(
            top_frame, text="Show Code", command=self.show_dynamic_cipher_code
        )
        self.show_dynamic_cipher_code_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tooltip for File Upload
        info_icon_upload = ctk.CTkLabel(
            top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2"
        )
        info_icon_upload.grid(row=0, column=3, sticky="w", padx=(5, 0), pady=5)
        upload_tooltip_text = "Upload a .py file for Dynamic Cipher encryption and decryption."
        ToolTip(info_icon_upload, upload_tooltip_text)

        # Section 1: Code Preview Title
        code_preview_title = ctk.CTkLabel(
            self.dynamic_cipher_frame, text="Code Preview", font=("Arial", 12, "bold")
        )
        code_preview_title.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 2))

        # Code Preview Text Widget with Scrollbar
        self.dynamic_cipher_code_display_box = ctk.CTkTextbox(
            self.dynamic_cipher_frame, wrap="word", height=15
        )
        self.dynamic_cipher_code_display_box.grid(row=2, column=0, sticky="nsew", padx=(10, 0), pady=5)

        self.dynamic_cipher_code_scrollbar = ctk.CTkScrollbar(
            self.dynamic_cipher_frame, orientation="vertical",
            command=self.dynamic_cipher_code_display_box.yview
        )
        self.dynamic_cipher_code_scrollbar.grid(row=2, column=1, sticky="ns", padx=(0, 10), pady=5)
        self.dynamic_cipher_code_display_box.configure(yscrollcommand=self.dynamic_cipher_code_scrollbar.set)

        # Submit button for encryption and decryption script generation
        self.dynamic_cipher_submit_btn = ctk.CTkButton(
            self.dynamic_cipher_frame, text="Encrypt and Generate Decryption Script",
            command=self.submit_dynamic_cipher, width=300
        )
        self.dynamic_cipher_submit_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew", padx=10)

        # Section 2: Result Preview Title
        result_preview_title = ctk.CTkLabel(
            self.dynamic_cipher_frame, text="Result Preview", font=("Arial", 12, "bold")
        )
        result_preview_title.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 2))

        # Result display area with Scrollbar
        self.dynamic_cipher_result_box = ctk.CTkTextbox(
            self.dynamic_cipher_frame, wrap="word", height=15
        )
        self.dynamic_cipher_result_box.grid(row=5, column=0, sticky="nsew", padx=(10, 0), pady=5)

        self.dynamic_cipher_result_scrollbar = ctk.CTkScrollbar(
            self.dynamic_cipher_frame, orientation="vertical",
            command=self.dynamic_cipher_result_box.yview
        )
        self.dynamic_cipher_result_scrollbar.grid(row=5, column=1, sticky="ns", padx=(0, 10), pady=5)
        self.dynamic_cipher_result_box.configure(yscrollcommand=self.dynamic_cipher_result_scrollbar.set)

        # Success Message Label
        self.success_label_dynamic_cipher = ctk.CTkLabel(
            self.dynamic_cipher_frame, text="", text_color="green"
        )
        self.success_label_dynamic_cipher.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Store the uploaded malware path
        self.dynamic_cipher_uploaded_file = ""

    def load_dynamic_cipher_file(self):
        """Load the Python file for Dynamic Cipher encryption."""
        filepath = filedialog.askopenfilename(
            title="Select Python Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.dynamic_cipher_code_path = filepath
            self.dynamic_cipher_code_display_box.delete("0.0", "end")
            self.dynamic_cipher_code_display_box.insert("0.0", f"Successfully uploaded: {os.path.basename(filepath)}")
            self.dynamic_cipher_result_box.delete("0.0", "end")

    def show_dynamic_cipher_code(self):
        """Display the content of the uploaded Python code file."""
        if self.dynamic_cipher_code_path:
            try:
                with open(self.dynamic_cipher_code_path, 'r') as f:
                    code_content = f.read()
                self.dynamic_cipher_code_display_box.delete("0.0", "end")
                self.dynamic_cipher_code_display_box.insert("0.0", code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read code file: {e}")
        else:
            messagebox.showerror("Error", "No Python code file uploaded.")

    def submit_dynamic_cipher(self):
        """Encrypt the Python code and generate a decryption script."""
        if not self.dynamic_cipher_code_path:
            messagebox.showerror("Error", "Please upload the Python code file before submitting.")
            return

        # Perform the encryption and decryption script generation
        status = dyc.runtime_decrypt(self.dynamic_cipher_code_path)
        if status:
            # Display a success message
            self.dynamic_cipher_result_box.delete("0.0", "end")
            self.dynamic_cipher_result_box.insert(
                "0.0", f"Encryption and Decryption Script Generated Successfully!\nFile output to {status}\n"
            )
        else:
            self.dynamic_cipher_result_box.delete("0.0", "end")
            self.dynamic_cipher_result_box.insert(
                "0.0", "Encryption Failed! \n Please Debug this"
            )

    def create_py_compile_corrupt_tab(self):
        """Create the Corrupt Magic number of python script using magic number tab."""
        self.pyc_corrupt_frame = self.tabview.tab("PyCompile Corrupt Magic")
        self.pyc_corrupt_frame.columnconfigure(0, weight=1)
        self.pyc_corrupt_frame.columnconfigure(1, weight=0)  # For scrollbar
        # Configure rows to allow textboxes to expand
        for i in range(6):
            self.pyc_corrupt_frame.rowconfigure(i, weight=0)
        self.pyc_corrupt_frame.rowconfigure(2, weight=1)  # Code display
        self.pyc_corrupt_frame.rowconfigure(5, weight=1)  # Result display

        # Variables to store file paths
        self.pyc_corrupt_code_path = ""

        # Top Frame for file uploading and showing code
        top_frame = ctk.CTkFrame(self.pyc_corrupt_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=0)

        # File Upload Section
        upload_label = ctk.CTkLabel(top_frame, text="Your Python Code:")
        upload_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.upload_pyc_corrupt_btn = ctk.CTkButton(
            top_frame, text="Upload Python Code", command=self.load_pyc_corrupt_file
        )
        self.upload_pyc_corrupt_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.show_pyc_corrupt_code_btn = ctk.CTkButton(
            top_frame, text="Show Code", command=self.show_pyc_corrupt_code
        )
        self.show_pyc_corrupt_code_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tooltip for File Upload
        info_icon = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        ToolTip(info_icon, "Upload a .py file to corrupt the magic number.")

        # XOR Value Input
        xor_label = ctk.CTkLabel(top_frame, text="XOR Value (Hex):")
        xor_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.xor_value_entry = ctk.CTkEntry(top_frame)
        self.xor_value_entry.insert(0, "0xFF")  # Default value
        self.xor_value_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Tooltip for XOR value
        info_icon_xor = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_xor.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        ToolTip(info_icon_xor, "XOR magic number value to XOR compile your .py file with.")

        # Preview Header for Uploaded Code
        code_preview_header = ctk.CTkLabel(
            self.pyc_corrupt_frame, text="Uploaded Code Preview", font=("Arial", 12, "bold")
        )
        code_preview_header.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))

        # Text box for displaying uploaded code (resizable)
        self.pyc_corrupt_code_display_box = ctk.CTkTextbox(
            self.pyc_corrupt_frame, wrap="word", height=20
        )
        self.pyc_corrupt_code_display_box.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5
        )

        # Submit button for corruption action
        self.pyc_corrupt_submit_btn = ctk.CTkButton(
            self.pyc_corrupt_frame, text="Corrupt Magic Number", command=self.submit_pyc_corrupt, width=200
        )
        self.pyc_corrupt_submit_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew", padx=10)

        # Tooltip for Submit Button
        ToolTip(
            self.pyc_corrupt_submit_btn,
            "Click to corrupt the magic number in your uploaded Python script."
        )

        # Preview Header for Corruption Results
        result_preview_header = ctk.CTkLabel(
            self.pyc_corrupt_frame, text="Corruption Results", font=("Arial", 12, "bold")
        )
        result_preview_header.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))

        # Result display area with Scrollbar
        self.pyc_corrupt_result_box = ctk.CTkTextbox(
            self.pyc_corrupt_frame, wrap="word", height=20
        )
        self.pyc_corrupt_result_box.grid(
            row=5, column=0, sticky="nsew", padx=10, pady=5
        )

        self.pyc_corrupt_scrollbar = ctk.CTkScrollbar(
            self.pyc_corrupt_frame, orientation="vertical", command=self.pyc_corrupt_result_box.yview
        )
        self.pyc_corrupt_scrollbar.grid(row=5, column=1, sticky="ns", pady=5)
        self.pyc_corrupt_result_box.configure(yscrollcommand=self.pyc_corrupt_scrollbar.set)

        # Ensure the result box expands properly
        self.pyc_corrupt_frame.rowconfigure(5, weight=1)
        self.pyc_corrupt_frame.columnconfigure(0, weight=1)

    def load_pyc_corrupt_file(self):
        """Load the Python file for PyCompile corruption."""
        filepath = filedialog.askopenfilename(
            title="Select Python Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.pyc_corrupt_code_path = filepath
            self.pyc_corrupt_code_display_box.delete("0.0", "end")
            self.pyc_corrupt_code_display_box.insert("0.0", f"Successfully uploaded: {os.path.basename(filepath)}")
            self.pyc_corrupt_result_box.delete("0.0", "end")

    def show_pyc_corrupt_code(self):
        """Display the content of the uploaded Python code file."""
        if self.pyc_corrupt_code_path:
            try:
                with open(self.pyc_corrupt_code_path, 'r') as f:
                    code_content = f.read()
                self.pyc_corrupt_code_display_box.delete("0.0", "end")
                self.pyc_corrupt_code_display_box.insert("0.0", code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read code file: {e}")
        else:
            messagebox.showerror("Error", "No Python code file uploaded.")

    def submit_pyc_corrupt(self):
        """Execute the magic number corruption and display results."""
        if not self.pyc_corrupt_code_path:
            messagebox.showerror("Error", "Please upload the Python code file before submitting.")
            return

        # Get XOR value from the input field
        try:
            xor_value = int(self.xor_value_entry.get(), 16)  # Parse as hexadecimal
        except ValueError:
            messagebox.showerror("Error", "Invalid XOR value. Please enter a valid hexadecimal number.")
            return

        # Perform the corruption process
        status, output_file = pyc.pyc_corrupt_source_with_xor(self.pyc_corrupt_code_path, xor_value=xor_value)

        self.pyc_corrupt_result_box.delete("0.0", "end")
        if status:
            self.pyc_corrupt_result_box.insert("0.0", f"Corruption Successful!\nOutput saved to: {output_file}\n")
        else:
            self.pyc_corrupt_result_box.insert("0.0", "An error occurred during corruption.\n")

    def create_excel_macro_tab(self):
        """Create the Macro Excel Embedder tab."""
        self.excel_macro_frame = self.tabview.tab("Macro Excel Embedder")
        self.excel_macro_frame.columnconfigure(0, weight=1)
        self.excel_macro_frame.rowconfigure(3, weight=1)

        # Variables to store file paths
        self.malicious_python_path_excel_macro = ""
        self.excel_file_path_excel_macro = ""
        self.vba_macro_path_excel_macro = ""

        # Top Frame for uploading files
        top_frame = ctk.CTkFrame(self.excel_macro_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        # Malicious Python Script Upload
        malicious_label = ctk.CTkLabel(top_frame, text="Malicious Python Script:")
        malicious_label.grid(row=0, column=0, sticky="w")

        self.upload_malicious_python_btn_excel_macro = ctk.CTkButton(
            top_frame, text="Upload Script", command=self.load_malicious_python_excel_macro
        )
        self.upload_malicious_python_btn_excel_macro.grid(row=0, column=1, sticky="ew", padx=5, pady=1)

        self.show_malicious_python_btn_excel_macro = ctk.CTkButton(
            top_frame, text="Show", command=self.show_malicious_python_excel_macro
        )
        self.show_malicious_python_btn_excel_macro.grid(row=0, column=2, sticky="ew", padx=5)

        info_icon_script = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_script.grid(row=0, column=3, sticky="w", padx=5)
        ToolTip(info_icon_script, "Upload the Python script to embed as malicious code in the Excel file.")

        # Excel File Upload
        excel_label = ctk.CTkLabel(top_frame, text="Excel File:")
        excel_label.grid(row=1, column=0, sticky="w")

        self.upload_excel_file_btn_excel_macro = ctk.CTkButton(
            top_frame, text="Upload Excel", command=self.load_excel_file_excel_macro
        )
        self.upload_excel_file_btn_excel_macro.grid(row=1, column=1, sticky="ew", padx=5, pady=1)

        self.show_excel_file_btn_excel_macro = ctk.CTkButton(
            top_frame, text="Show", command=self.show_excel_file_excel_macro
        )
        self.show_excel_file_btn_excel_macro.grid(row=1, column=2, sticky="ew", padx=5)

        info_icon_excel = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_excel.grid(row=1, column=3, sticky="w", padx=5)
        ToolTip(info_icon_excel, "Select the Excel file to embed the malicious code into.")

        # VBA Macro File Upload
        vba_label = ctk.CTkLabel(top_frame, text="VBA Macro File:")
        vba_label.grid(row=2, column=0, sticky="w")

        self.upload_vba_macro_btn_excel_macro = ctk.CTkButton(
            top_frame, text="Upload Macro", command=self.load_vba_macro_excel_macro
        )
        self.upload_vba_macro_btn_excel_macro.grid(row=2, column=1, sticky="ew", padx=5, pady=1)

        self.show_vba_macro_btn_excel_macro = ctk.CTkButton(
            top_frame, text="Show", command=self.show_vba_macro_excel_macro
        )
        self.show_vba_macro_btn_excel_macro.grid(row=2, column=2, sticky="ew", padx=5)

        info_icon_macro = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_macro.grid(row=2, column=3, sticky="w", padx=5)
        ToolTip(info_icon_macro, "Upload the VBA macro script to embed along with the Python script in the Excel file.")

        # Text box for displaying file contents
        self.file_content_display_excel_macro = ctk.CTkTextbox(self.excel_macro_frame, wrap="word", height=10)
        self.file_content_display_excel_macro.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Submit Button
        self.submit_excel_macro_btn = ctk.CTkButton(
            self.excel_macro_frame, text="Embed in Excel", command=self.submit_excel_macro, width=200
        )
        self.submit_excel_macro_btn.grid(row=4, column=0, pady=10, sticky="ew")

    def load_malicious_python_excel_macro(self):
        """Load the malicious Python script file."""
        self.malicious_python_path_excel_macro = filedialog.askopenfilename(
            title="Select Python Script",
            filetypes=[("Python files", "*.py")],
        )
        if self.malicious_python_path_excel_macro:
            self.file_content_display_excel_macro.delete("0.0", "end")
            self.file_content_display_excel_macro.insert(
                "0.0", f"Uploaded: {os.path.basename(self.malicious_python_path_excel_macro)}\n"
            )

    def show_malicious_python_excel_macro(self):
        """Display the content of the uploaded Python script file."""
        if self.malicious_python_path_excel_macro:
            with open(self.malicious_python_path_excel_macro, 'r') as f:
                content = f.read()
            self.file_content_display_excel_macro.delete("0.0", "end")
            self.file_content_display_excel_macro.insert("0.0", content)
        else:
            messagebox.showerror("Error", "No Python script uploaded.")

    def load_excel_file_excel_macro(self):
        """Load the Excel file to embed malicious code."""
        self.excel_file_path_excel_macro = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xls;*.xlsx")],
        )
        if self.excel_file_path_excel_macro:
            self.file_content_display_excel_macro.delete("0.0", "end")
            self.file_content_display_excel_macro.insert(
                "0.0", f"Uploaded: {os.path.basename(self.excel_file_path_excel_macro)}\n"
            )

    def show_excel_file_excel_macro(self):
        """Display the content of the uploaded Excel file path."""
        if self.excel_file_path_excel_macro:
            self.file_content_display_excel_macro.delete("0.0", "end")
            self.file_content_display_excel_macro.insert(
                "0.0", f"Excel File Path: {self.excel_file_path_excel_macro}\n"
            )
        else:
            messagebox.showerror("Error", "No Excel file uploaded.")

    def load_vba_macro_excel_macro(self):
        """Load the VBA macro file."""
        self.vba_macro_path_excel_macro = filedialog.askopenfilename(
            title="Select VBA Macro File",
            filetypes=[("Text files", "*.txt")],
        )
        if self.vba_macro_path_excel_macro:
            self.file_content_display_excel_macro.delete("0.0", "end")
            self.file_content_display_excel_macro.insert(
                "0.0", f"Uploaded: {os.path.basename(self.vba_macro_path_excel_macro)}\n"
            )

    def show_vba_macro_excel_macro(self):
        """Display the content of the uploaded VBA macro file."""
        if self.vba_macro_path_excel_macro:
            with open(self.vba_macro_path_excel_macro, 'r') as f:
                content = f.read()
            self.file_content_display_excel_macro.delete("0.0", "end")
            self.file_content_display_excel_macro.insert("0.0", content)
        else:
            messagebox.showerror("Error", "No VBA macro file uploaded.")

    def submit_excel_macro(self):
        """Embed Python script and VBA macro in Excel file."""
        if not (
                self.malicious_python_path_excel_macro and self.excel_file_path_excel_macro and self.vba_macro_path_excel_macro):
            messagebox.showerror("Error", "Please upload all required files before submitting.")
            return

        output_excel_path = filedialog.asksaveasfilename(
            title="Save Output Excel File",
            defaultextension=".xlsm",
            filetypes=[("Excel files", "*.xlsm")],
        )
        if output_excel_path:
            result = embed_python_script_and_vba(
                self.excel_file_path_excel_macro,
                self.malicious_python_path_excel_macro,
                output_excel_path,
                self.vba_macro_path_excel_macro
            )
            self.file_content_display_excel_macro.delete("0.0", "end")
            if result:
                self.file_content_display_excel_macro.insert(
                    "0.0", f"Embedding successful!\nOutput saved to: {output_excel_path}"
                )
            else:
                self.file_content_display_excel_macro.insert(
                    "0.0", f"Embedding Failed!\n"
                )

    def create_embed_in_pdf_tab(self):
        """Create the PDF Embedder tab with independent display for PDF embed process."""
        self.pdf_embed_frame = self.tabview.tab("PDF Embedder")
        self.pdf_embed_frame.columnconfigure(0, weight=1)
        self.pdf_embed_frame.rowconfigure(5, weight=1)

        # Variables for PDF embedder inputs
        self.malware_code_path_pdf = ""
        self.public_key_path_pdf = ""
        self.pdf_folder_path = ""
        self.pdf_files_selected = {}

        # Top frame for malware file upload in PDF Embedder
        top_frame_pdf = ctk.CTkFrame(self.pdf_embed_frame)
        top_frame_pdf.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame_pdf.columnconfigure(1, weight=1)
        top_frame_pdf.columnconfigure(3, weight=0)

        # Malware File upload section
        malware_label = ctk.CTkLabel(top_frame_pdf, text="Malware File:")
        malware_label.grid(row=0, column=0, sticky="w")

        self.malware_upload_btn_pdf = ctk.CTkButton(top_frame_pdf, text="Upload Malware File",
                                                    command=self.load_malware_file_pdf)
        self.malware_upload_btn_pdf.grid(row=0, column=1, sticky="ew", padx=5)

        self.show_malware_btn_pdf = ctk.CTkButton(top_frame_pdf, text="Show Malware Code",
                                                  command=self.show_malware_code_pdf)
        self.show_malware_btn_pdf.grid(row=0, column=2, sticky="ew", padx=5)

        # Tooltip for Malware File upload
        info_icon_malware_pdf = ctk.CTkLabel(top_frame_pdf, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_malware_pdf.grid(row=0, column=3, sticky="w", padx=5)
        malware_tooltip_text_pdf = "Upload a .py malware file to embed in PDF files."
        ToolTip(info_icon_malware_pdf, malware_tooltip_text_pdf)

        # Status Label for upload success/failure
        self.upload_status_label_pdf = ctk.CTkLabel(top_frame_pdf, text="No file uploaded.", text_color="white")
        self.upload_status_label_pdf.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=5)

        # Subtab notebook for PEM Key Encryption Option
        subtab_notebook = ctk.CTkTabview(self.pdf_embed_frame)
        subtab_notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.pdf_embed_frame.rowconfigure(1, weight=1)  # Ensure notebook expands

        # PEM Key Encryption Subtab
        pdf_embed_subtab = subtab_notebook.add("PEM Key Encryption")

        pdf_embed_subtab.columnconfigure(0, weight=1)
        pdf_embed_subtab.rowconfigure(4, weight=1)

        # Public Key PEM File Upload
        public_key_label = ctk.CTkLabel(pdf_embed_subtab, text="Public Key (PEM):")
        public_key_label.grid(row=0, column=0, sticky="w")

        self.upload_public_key_btn_pdf = ctk.CTkButton(pdf_embed_subtab, text="Upload Public Key",
                                                       command=self.load_public_key_pdf)
        self.upload_public_key_btn_pdf.grid(row=0, column=1, sticky="ew", padx=5, pady=1)

        self.show_public_key_btn_pdf = ctk.CTkButton(pdf_embed_subtab, text="Show Public Key",
                                                     command=self.show_public_key_pdf)
        self.show_public_key_btn_pdf.grid(row=0, column=2, sticky="ew", padx=5)

        # Tooltip for Public Key
        info_icon_key_pdf = ctk.CTkLabel(pdf_embed_subtab, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_key_pdf.grid(row=0, column=3, sticky="w", padx=5)
        public_key_tooltip_text_pdf = "Select an existing PEM public key to embed in PDFs."
        ToolTip(info_icon_key_pdf, public_key_tooltip_text_pdf)

        # PDF Folder selection for input files
        folder_label_pdf = ctk.CTkLabel(pdf_embed_subtab, text="PDF Input Folder:")
        folder_label_pdf.grid(row=1, column=0, sticky="w")

        self.folder_select_btn_pdf = ctk.CTkButton(pdf_embed_subtab, text="Select Folder",
                                                   command=self.select_pdf_folder_pdf)
        self.folder_select_btn_pdf.grid(row=1, column=1, sticky="ew", padx=5)

        # Tooltip for PDF Input Folder selection
        info_icon_folder_pdf = ctk.CTkLabel(pdf_embed_subtab, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_folder_pdf.grid(row=1, column=3, sticky="w", padx=5)
        folder_tooltip_text_pdf = "Choose the folder containing PDF files to embed the malware into."
        ToolTip(info_icon_folder_pdf, folder_tooltip_text_pdf)

        # PDF Checkboxes frame for file selection
        self.pdf_checkboxes_frame_pdf = ctk.CTkFrame(pdf_embed_subtab)
        self.pdf_checkboxes_frame_pdf.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # Submit button and output result box
        self.submit_pdf_embed_btn = ctk.CTkButton(pdf_embed_subtab, text="Submit", command=self.submit_pdf_embed,
                                                  width=200)
        self.submit_pdf_embed_btn.grid(row=3, column=0, columnspan=4, sticky="ew", pady=10)

        # Result Text box in Embedding Options subtab
        self.result_box_pdf_embed = ctk.CTkTextbox(pdf_embed_subtab, wrap="word", height=10)
        self.result_box_pdf_embed.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # Status area in Embedding Options subtab
        self.keygen_status_label_pdf = ctk.CTkLabel(pdf_embed_subtab, text="", text_color="white")
        self.keygen_status_label_pdf.grid(row=5, column=0, columnspan=4, sticky="w", padx=10, pady=5)

        # Image Embedding Options Subtab
        image_embed_subtab = subtab_notebook.add("Image Steganography")

        image_embed_subtab.columnconfigure(0, weight=1)
        image_embed_subtab.rowconfigure(3, weight=1)

        # Image Input Folder selection
        image_folder_label = ctk.CTkLabel(image_embed_subtab, text="Image Input Folder:")
        image_folder_label.grid(row=0, column=0, sticky="w")

        self.folder_select_btn_image = ctk.CTkButton(image_embed_subtab, text="Select Folder",
                                                     command=self.select_input_image_folder)
        self.folder_select_btn_image.grid(row=0, column=1, sticky="ew", padx=5)

        # Image Checkboxes frame for file selection
        self.image_checkboxes_frame = ctk.CTkFrame(image_embed_subtab)
        self.image_checkboxes_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # Submit button and output result box
        self.submit_image_embed_btn = ctk.CTkButton(image_embed_subtab, text="Submit", command=self.submit_image_embed,
                                                    width=200)
        self.submit_image_embed_btn.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)

        # Result Text box in Image Embedding Options subtab
        self.result_box_image_embed = ctk.CTkTextbox(image_embed_subtab, wrap="word", height=10)
        self.result_box_image_embed.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

    def load_malware_file_pdf(self):
        """Load the malware code file specifically for PDF Embedder."""
        self.malware_code_path_pdf = filedialog.askopenfilename(
            title="Select Malware File",
            filetypes=[("Python files", "*.py")]
        )
        if self.malware_code_path_pdf:
            self.upload_status_label_pdf.configure(text=f"Uploaded: {os.path.basename(self.malware_code_path_pdf)}")
            with open(self.malware_code_path_pdf, 'r') as f:
                code_content = f.read()

            # Check if result_box_pdf_embed is visible before updating it
            if self.result_box_pdf_embed.winfo_viewable():
                self.result_box_pdf_embed.delete("0.0", "end")
                self.result_box_pdf_embed.insert("0.0", f"Loaded Malware Code for PDF Embed:\n{code_content}\n")
            elif self.result_box_image_embed.winfo_viewable():
                self.result_box_image_embed.delete("0.0", "end")
                self.result_box_image_embed.insert("0.0", f"Loaded Malware Code for PDF Embed:\n{code_content}\n")

    def load_public_key_pdf(self):
        """Load the PEM public key file for PDF Embedder."""
        self.public_key_path_pdf = filedialog.askopenfilename(
            title="Select Public Key",
            filetypes=[("PEM files", "*.pem")]
        )
        if self.public_key_path_pdf:
            self.keygen_status_label_pdf.configure(text=f"Uploaded: {os.path.basename(self.public_key_path_pdf)}")

    def show_public_key_pdf(self):
        """Display the content of the uploaded PEM public key file."""
        if self.public_key_path_pdf:
            with open(self.public_key_path_pdf, 'r') as f:
                key_content = f.read()
            self.result_box_pdf_embed.delete("0.0", "end")
            self.result_box_pdf_embed.insert("0.0", f"Loaded Public Key:\n{key_content}\n")
        else:
            messagebox.showerror("Error", "No public key file uploaded.")

    def select_pdf_folder_pdf(self):
        """Select folder containing PDFs and display available files as checkboxes."""
        self.pdf_folder_path = filedialog.askdirectory(title="Select PDF Folder")
        if self.pdf_folder_path:
            # Clear existing checkboxes in the pdf_checkboxes_frame
            for widget in self.pdf_checkboxes_frame_pdf.winfo_children():
                widget.destroy()

            # Display PDFs as checkboxes with full path stored
            pdf_files = [f for f in os.listdir(self.pdf_folder_path) if f.endswith(".pdf")]
            self.pdf_files_selected = {}
            for i, pdf_file in enumerate(pdf_files):
                var = IntVar(value=0)
                # Display filename only, store full path
                checkbox = ctk.CTkCheckBox(self.pdf_checkboxes_frame_pdf, text=pdf_file, variable=var)
                checkbox.grid(row=i, column=0, sticky="w")
                full_path = os.path.join(self.pdf_folder_path, pdf_file)
                self.pdf_files_selected[full_path] = var

    def select_input_image_folder(self):
        """Select folder containing images and display available files as checkboxes."""
        self.image_folder_path = filedialog.askdirectory(title="Select Image Folder")
        if self.image_folder_path:
            # Clear existing checkboxes in the image_checkboxes_frame
            for widget in self.image_checkboxes_frame.winfo_children():
                widget.destroy()

            # Display images as checkboxes with full path stored
            image_files = [f for f in os.listdir(self.image_folder_path)
                           if (f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png"))]
            self.image_files_selected = {}
            for i, image_file in enumerate(image_files):
                var = IntVar(value=0)
                # Display filename only, store full path
                checkbox = ctk.CTkCheckBox(self.image_checkboxes_frame, text=image_file, variable=var)
                checkbox.grid(row=i, column=0, sticky="w")
                full_path = os.path.join(self.image_folder_path, image_file)
                self.image_files_selected[full_path] = var

    def submit_pdf_embed(self):
        """Submit the PDF files for embedding."""
        selected_pdfs = [f for f, var in self.pdf_files_selected.items() if var.get() == 1]
        if not self.malware_code_path_pdf:
            messagebox.showerror("Error", "Please upload a malware file.")
            return
        if not selected_pdfs:
            messagebox.showerror("Error", "Please select at least one PDF file.")
            return
        if not self.public_key_path_pdf:
            messagebox.showerror("Error", "Please select a PEM public key file.")
            return

        output_folder = Path("Output/embedded_pdf_files")
        output_folder.mkdir(parents=True, exist_ok=True)

        # Call your embed_in_pdf function here
        success = pdf.embed_python_in_multiple_pdfs(self.malware_code_path_pdf, selected_pdfs, self.public_key_path_pdf)

        if success:
            output_files = [output_folder / os.path.basename(pdf) for pdf in selected_pdfs]
            self.result_box_pdf_embed.delete("0.0", "end")
            self.result_box_pdf_embed.insert("0.0",
                                             "Usage:\npython extract_pdf_rsa.py <private_key.pem> <pdf_file_1> "
                                             "<pdf_file_2> ... <output_python_file>\n")
            self.result_box_pdf_embed.insert("0.0", "\nTo extract the malware, use:\n")

            for file in output_files:
                self.result_box_pdf_embed.insert("0.0", f"{file}\n")
            self.result_box_pdf_embed.insert("0.0", "Embedding successful!\nFiles saved to:\n")

        else:
            self.result_box_pdf_embed.insert("0.0", "An error occurred during PDF embedding.")

    def show_malware_code_pdf(self):
        """Display the malware code in a text box."""
        if self.malware_code_path_pdf:
            with open(self.malware_code_path_pdf, 'r') as f:
                code_content = f.read()
            self.result_box_pdf_embed.delete("0.0", "end")
            self.result_box_pdf_embed.insert("0.0", code_content)
        else:
            messagebox.showerror("Error", "No malware file uploaded.")

    def submit_image_embed(self):
        """Submit the image files for embedding. Also outputs PDF file"""
        input_secret_file = self.malware_code_path_pdf
        selected_images = [f for f, var in self.image_files_selected.items() if var.get() == 1]
        if not input_secret_file:
            messagebox.showerror("Error", "No malware file uploaded.")
            return
        if not selected_images:
            messagebox.showerror("Error", "Please select at least one image file.")
            return

        output_folder_str = "Output/PDF_with_images"
        output_folder = Path(output_folder_str)
        output_folder.mkdir(parents=True, exist_ok=True)

        # Create a list of new paths with filenames in the output folder
        output_file_list = [os.path.join(output_folder_str, os.path.basename(path)) for path in selected_images]
        output_pdf_file = os.path.join(output_folder_str, "out.pdf")

        self.result_box_image_embed.delete("0.0", "end")
        self.result_box_image_embed.insert("0.0", "Encoding process started")
        res = stego.encode(selected_images, output_file_list, input_secret_file, output_pdf_file)
        if res:
            self.result_box_image_embed.insert("0.0",
                                               f"\n\nDone! PDF path: {res} containing the stego image has been saved.")
        else:
            self.result_box_image_embed.insert("0.0", "Image steganography/PDF Embedding failed due to error")

    def create_cython_tab(self):
        """Create the Compile with CythonCompile tab for taking a Python file input, showing code, and compiling with
        CythonCompile."""
        self.cython_frame = self.tabview.tab("Compile with CythonCompile")
        # Configure grid rows and columns with appropriate weights
        self.cython_frame.columnconfigure(0, weight=1)
        # Define row weights: higher weights for rows with textboxes to allow expansion
        for i in range(7):
            if i in [2, 6]:  # Rows with textboxes
                self.cython_frame.rowconfigure(i, weight=1)
            else:
                self.cython_frame.rowconfigure(i, weight=0)

        # Initialize variables
        self.cython_code_path = ""
        self.cython_output_file_name = StringVar(value="")

        # Top Frame for file uploading and showing code
        top_frame = ctk.CTkFrame(self.cython_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_frame.columnconfigure(1, weight=1)

        # Python File Upload Section
        cython_upload_label = ctk.CTkLabel(top_frame, text="Python File to Compile:")
        cython_upload_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.upload_cython_file_btn = ctk.CTkButton(
            top_frame, text="Upload Python File", command=self.load_cython_file
        )
        self.upload_cython_file_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Info Icon and Tooltip for Upload
        info_icon = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        cython_tooltip_text = "Upload a .py file to compile with CythonCompile. Only .py files are accepted."
        ToolTip(info_icon, cython_tooltip_text)

        # Code Preview Header
        code_preview_header = ctk.CTkLabel(
            self.cython_frame, text="Code Preview", font=("Arial", 12, "bold")
        )
        code_preview_header.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))

        # Display Box for code preview
        self.code_display_box_cython = ctk.CTkTextbox(
            self.cython_frame, wrap="word", height=20
        )
        self.code_display_box_cython.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)


        # Submit Button
        self.cython_submit_btn = ctk.CTkButton(
            self.cython_frame, text="Submit", command=self.submit_cython, width=200
        )
        self.cython_submit_btn.grid(row=3, column=0, pady=10, sticky="ew", padx=10)

        # Attach a tooltip to the submit button
        ToolTip(
            self.cython_submit_btn,
            "Click to compile the uploaded Python file into a .pyc file using CythonCompile."
        )

        # Compilation Results Header
        compilation_results_header = ctk.CTkLabel(
            self.cython_frame, text="Compilation Results", font=("Arial", 12, "bold")
        )
        compilation_results_header.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))

        # Result display box for compilation output
        self.result_box_cython = ctk.CTkTextbox(
            self.cython_frame, wrap="word", height=20
        )
        self.result_box_cython.grid(row=6, column=0, sticky="nsew", padx=10, pady=5)

    def load_cython_file(self):
        """Load the Python file for CythonCompile compilation."""
        self.cython_code_path = filedialog.askopenfilename(
            title="Select Python File to Compile",
            filetypes=[("Python files", "*.py")]
        )
        if self.cython_code_path:
            with open(self.cython_code_path, 'r') as f:
                code_content = f.read()
            self.code_display_box_cython.delete("0.0", "end")
            self.code_display_box_cython.insert("0.0", code_content)

    def submit_cython(self):
        """Submit the file for compilation with CythonCompile."""
        input_file = self.cython_code_path

        if not input_file:
            messagebox.showerror("Error", "Please upload a Python file to compile.")
            return

        # Create output directory if it doesn't exist
        os.makedirs("Output", exist_ok=True)

        # Run the cython compiler
        success, location = self.cython_compiler(input_file)

        # Display results
        self.result_box_cython.delete("0.0", "end")
        if success:
            self.result_box_cython.insert("0.0", f"Compilation Successful!\nOutput saved to: {location}")
        else:
            self.result_box_cython.insert("0.0", "An error occurred during compilation.")

    def cython_compiler(input_file):
        return cc.cython_compilation(input_file)

    # def cython_compiler(self, input_file, output_file):
    #     """Compile a Python file using CythonCompile to produce a .pyc output."""
    #     try:
    #         # Actual CythonCompile compilation call, replace with your import and actual call from compile.py
    #         location = compile_with_cython(input_file, output_file)  # Replace with actual function call
    #         if location is not None:
    #             return True, location
    #         else:
    #             return False, None
    #     except Exception as e:
    #         print(f"Compilation Error: {e}")
    #         return False, None

    def create_qmorph_tab(self):
        """Create the QMorph Malware tab."""
        # Initialize variables
        self.malware_code_path_qmorph = ""

        self.qmorph_frame = self.tabview.tab("QMorph Malware")
        self.qmorph_frame.columnconfigure(0, weight=1)
        self.qmorph_frame.rowconfigure(2, weight=1)  # Added weight for row 2
        self.qmorph_frame.rowconfigure(4, weight=1)

        # Top Frame for file uploading and showing code
        top_frame = ctk.CTkFrame(self.qmorph_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        # Malware Code Upload Section
        malware_label = ctk.CTkLabel(top_frame, text="Your Malware Code:")
        malware_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.upload_malware_btn = ctk.CTkButton(
            top_frame, text="Upload Malware Code", command=self.load_malware_file
        )
        self.upload_malware_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.show_malware_btn = ctk.CTkButton(
            top_frame, text="Show Code", command=self.show_malware_code_qmorph
        )
        self.show_malware_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tooltip for Malware Code section
        info_icon = ctk.CTkLabel(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        malware_tooltip_text = "Upload your custom malware code (.py) for QMorph obfuscation."
        ToolTip(info_icon, malware_tooltip_text)

        # Code Preview title
        code_preview_title = ctk.CTkLabel(self.qmorph_frame, text="Code Preview", font=("Arial", 12, "bold"))
        code_preview_title.grid(row=1, column=0, sticky="w", padx=5, pady=(10, 2))

        # Text box to display uploaded code (resizable)
        self.code_display_box_qmorph = ctk.CTkTextbox(self.qmorph_frame, wrap="word", height=20)  # Increased height
        self.code_display_box_qmorph.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Submit button
        self.qmorph_submit_btn = ctk.CTkButton(
            self.qmorph_frame, text="Submit", command=self.submit_qmorph, width=200
        )
        self.qmorph_submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # Result display (resizable) with Scrollbar
        self.result_box_qmorph = ctk.CTkTextbox(self.qmorph_frame, wrap="word", height=20)  # Increased height
        self.result_box_qmorph.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        self.scrollbar_qmorph = ctk.CTkScrollbar(self.qmorph_frame, orientation="vertical",
                                                 command=self.result_box_qmorph.yview)
        self.scrollbar_qmorph.grid(row=4, column=1, sticky="ns", pady=10)
        self.result_box_qmorph.configure(yscrollcommand=self.scrollbar_qmorph.set)

    def load_malware_file(self):
        """Load the malware code file for QMorph obfuscation."""
        filepath = filedialog.askopenfilename(
            title="Select Malware Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.malware_code_path_qmorph = filepath
            self.code_display_box_qmorph.delete("0.0", "end")
            self.code_display_box_qmorph.insert("0.0",
                                                f"Successfully uploaded: {os.path.basename(self.malware_code_path_qmorph)}")
            # Clear previous result
            self.result_box_qmorph.delete("0.0", "end")

    def show_malware_code_qmorph(self):
        """Display the content of the uploaded malware code file in QMorph tab."""
        if self.malware_code_path_qmorph:
            try:
                with open(self.malware_code_path_qmorph, 'r') as f:
                    code_content = f.read()
                self.code_display_box_qmorph.delete("0.0", "end")
                self.code_display_box_qmorph.insert("0.0", code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read malware code file: {e}")
        else:
            messagebox.showerror("Error", "No malware code file uploaded.")

    def submit_qmorph(self):
        """Process the QMorph obfuscation and display the result."""
        if not self.malware_code_path_qmorph:
            messagebox.showerror("Error", "Please upload the malware code file before submitting.")
            return

        success, output_file = qm.QMorph(self.malware_code_path_qmorph)

        # Display the result
        self.result_box_qmorph.delete("0.0", "end")
        if success:
            try:
                with open(output_file, 'r') as f:
                    result_content = f.read()
                self.result_box_qmorph.insert(
                    "0.0",
                    f"QMorph Obfuscation Successful!\nOutput saved to: {output_file}\n\n{result_content}",
                )
            except Exception as e:
                self.result_box_qmorph.insert(
                    "0.0",
                    f"QMorph Obfuscation Successful!\nOutput saved to: {output_file}\n\nError reading output file: {e}",
                )
        else:
            self.result_box_qmorph.insert("0.0", "An error occurred during QMorph obfuscation.\n")
            self.result_box_qmorph.insert("0.0", f"Error Message: {output_file}")

    def submit_custom(self):
        """Perform the embedding process and display the final code output for Custom mode."""
        new_name = self.new_file_name_custom.get()
        if new_name != "Output/Innocent.py" and new_name != "":
            new_name = "Output/" + new_name
        loc_to_inject = self.loc_to_inject_custom.get()
        func_name = self.selected_function_custom.get()
        wrap = self.wrap_custom.get()

        if not self.original_code_path_custom or not self.embed_code_path_custom:
            messagebox.showerror("Error", "Please upload both the original and embed code files for Custom mode.")
            return

        if not new_name:
            messagebox.showerror("Error", "Please specify a new name for the output file.")
            return

        # Ensure func_name is not empty
        if not func_name:
            messagebox.showerror("Error", "Please select a function to inject.")
            return

        # Prepare lists for embed_code function
        embed_code_filenames = [self.embed_code_path_custom]
        func_names = [func_name]

        # Perform embedding using the code_embedder module
        status = ce.embed_code(
            embed_code_filenames=embed_code_filenames,  # Pass as list
            func_names=func_names,  # Pass as list
            src_code_filename=self.original_code_path_custom,
            loc_to_inject=loc_to_inject,
            wrap=wrap,
            new_name=new_name,
        )

        if status == 0:
            output_path = os.path.abspath(new_name if new_name.endswith(".py") else new_name + ".py")
            try:
                with open(output_path, 'r') as f:
                    result_code = f.read()
                self.result_box_custom.delete("0.0", "end")
                self.result_box_custom.insert("0.0",
                                              f"Success! Embedded code saved to: {output_path}\n\n{result_code}")
            except Exception as e:
                self.result_box_custom.delete("0.0", "end")
                self.result_box_custom.insert(
                    "0.0", f"Success! Embedded code saved to: {output_path}\n\nError reading output file: {e}"
                )
        else:
            messagebox.showerror("Error", "An error occurred during code embedding.")

    def load_original_file_custom(self):
        """Load the original code file for the Custom mode."""
        filepath = filedialog.askopenfilename(
            title="Select Original Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.original_code_path_custom = filepath
            self.upload_status_original.configure(text=f"Uploaded: {os.path.basename(filepath)}")
            # Clear previous success message and code preview
            self.result_box_custom.delete("0.0", "end")

    def show_original_code_custom(self):
        """Display the content of the uploaded original code file in Custom mode."""
        if self.original_code_path_custom:
            try:
                with open(self.original_code_path_custom, 'r') as f:
                    code_content = f.read()
                self.code_display_box_custom.delete("0.0", "end")
                self.code_display_box_custom.insert("0.0", code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read original code file: {e}")
        else:
            messagebox.showerror("Error", "No original code file uploaded for Custom mode.")

    def load_embed_file_custom(self):
        """Load the embed code file for the Custom mode."""
        filepath = filedialog.askopenfilename(
            title="Select Embed Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.embed_code_path_custom = filepath
            self.upload_status_embed.configure(text=f"Uploaded: {os.path.basename(filepath)}")

            # Extract functions and populate dropdown
            imports, functions = extract_functions_and_imports(filepath)
            function_names = [func.name for func in functions]
            self.populate_dropdown_custom(function_names)

    def show_embed_code_custom(self):
        """Display the embed code in the text box for Custom mode."""
        if self.embed_code_path_custom:
            try:
                with open(self.embed_code_path_custom, 'r') as f:
                    code_content = f.read()
                self.code_display_box_custom.delete("0.0", "end")
                self.code_display_box_custom.insert("0.0", code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read embed code file: {e}")
        else:
            messagebox.showerror("Error", "No embed code file uploaded for Custom mode.")

    def populate_dropdown_custom(self, function_names):
        """Populate the dropdown with the extracted function names for Custom mode."""
        if not function_names:
            self.selected_function_custom.set("")
            self.function_dropdown_custom.configure(values=["menu"])
            return

        self.function_dropdown_custom.configure(values=function_names)
        self.selected_function_custom.set(function_names[0])  # Set default selection


if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    splash = SplashScreen(app, image_path='./assets/ObfusQrypt.ico', wait_time=2000)

    app.geometry("1200x800")  # Set a default size or adjust as needed
    code_embedder_app = CodeEmbedderApp(app)
    app.mainloop()
