import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, BooleanVar, ttk, Checkbutton, IntVar
import os
import Code_Embedding.code_embedder as ce
import Quantum_Polymorphism.QMorph as qm
import glob  # For file pattern matching
# import Anti_Decompilation.CythonCompile.compiler as adc
from pathlib import Path
from Excel.embed_excel import embed_python_script_and_vba
from PDF import embed_pdf_rsa as pdf
from Anti_Decompilation.DynamicCipher import RunTimeDecrypt as dyc
from Anti_Decompilation.PyCCorruptor import PyCCorruptor as pyc
from Anti_Decompilation.CythonCompile.compile import compile_with_cython
import Fragmentation_Stego.encode as stego


class ToolTip:
    """Tooltip class to display tooltips for widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Show the tooltip."""
        if self.tooltip_window is not None:
            return  # Tooltip is already visible
        x = self.widget.winfo_rootx() + 20  # Offset for the tooltip
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Set a maximum width for the tooltip window
        max_width = 300  # Adjust this width as necessary
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            wraplength=max_width,
        )  # Added wraplength
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def extract_functions_and_imports(filepath):
    """Extract function definitions from the uploaded code file."""
    return ce.extract_functions_and_imports(filepath)


class CodeEmbedderApp:
    def __init__(self, main_root):
        self.root = main_root
        self.root.title("ObfusQrypt")

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

        # Main Notebook for tabs
        self.notebook = ttk.Notebook(main_root)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Allow notebook to expand and contract with window

        # Add the tabs
        self.create_code_embedder_tab()
        self.create_qmorph_tab()
        self.create_excel_macro_tab()
        self.create_embed_in_pdf_tab()
        self.create_cython_tab()
        self.create_py_compile_corrupt_tab()
        self.create_dynamic_cipher_tab()

    def create_code_embedder_tab(self):
        """Create the Code Embedder tab with subtabs for different modes."""
        self.code_embedder_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.code_embedder_frame, text="Code Embedder")

        # Ensure the frame itself can resize
        self.code_embedder_frame.columnconfigure(0, weight=1)
        self.code_embedder_frame.rowconfigure(1, weight=1)

        # Sub-Notebook for different embedding modes
        self.sub_notebook = ttk.Notebook(self.code_embedder_frame)
        self.sub_notebook.grid(row=0, column=0, sticky="nsew")

        # Create Subtabs
        self.create_self_destruct_subtab()
        self.create_check_vm_subtab()
        self.create_custom_subtab()

    def create_self_destruct_subtab(self):
        """Create the Self Destruct subtab."""
        self.self_destruct_frame = ttk.Frame(self.sub_notebook, padding="10")
        self.sub_notebook.add(self.self_destruct_frame, text="Self Destruct")

        # Variables specific to Self Destruct
        self.self_destruct_code_path = "Self_Destruct/self_destruct_script_poc.py"
        self.self_destruct_function = "secure_delete"

        # UI Elements

        # Malware Code Upload Section
        ttk.Label(self.self_destruct_frame, text="Upload Your Malware Code:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.upload_malware_btn_self_destruct = ttk.Button(
            self.self_destruct_frame, text="Upload Malware Code", command=self.upload_self_destruct_malware
        )
        self.upload_malware_btn_self_destruct.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Label to show upload status
        self.upload_status_self_destruct = ttk.Label(self.self_destruct_frame, text="No file uploaded.")
        self.upload_status_self_destruct.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Submit Button
        self.self_destruct_submit_btn = ttk.Button(
            self.self_destruct_frame, text="Embed Self Destruct", command=self.submit_self_destruct, padding=10
        )
        self.self_destruct_submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # Success Message Label
        self.success_label_self_destruct = ttk.Label(self.self_destruct_frame, text="", foreground="green")
        self.success_label_self_destruct.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        # Code Preview Title
        ttk.Label(self.self_destruct_frame, text="Code Preview", font=("Arial", 12, "bold")).grid(
            row=5, column=0, sticky="w", padx=5, pady=(10, 0)
        )

        # Code Preview Text Widget with Scrollbar
        self.code_preview_self_destruct = tk.Text(self.self_destruct_frame, wrap=tk.WORD, background="#f0f0f0",
                                                  height=18)
        self.code_preview_self_destruct.grid(row=6, column=0, sticky="nsew", padx=5, pady=5)

        # Configure Scrollbar for Code Preview
        self.scrollbar_self_destruct = ttk.Scrollbar(
            self.self_destruct_frame, orient="vertical", command=self.code_preview_self_destruct.yview
        )
        self.scrollbar_self_destruct.grid(row=6, column=1, sticky="ns", pady=5)
        self.code_preview_self_destruct.configure(yscrollcommand=self.scrollbar_self_destruct.set)

        # Configure resizing
        self.self_destruct_frame.columnconfigure(0, weight=1)
        self.self_destruct_frame.rowconfigure(6, weight=1)

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
            self.upload_status_self_destruct.config(text=f"Uploaded: {os.path.basename(filepath)}")
            # Clear previous success message and code preview
            self.success_label_self_destruct.config(text="")
            self.code_preview_self_destruct.delete(1.0, tk.END)

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
            func_names=[self.self_destruct_function],  # Pass as list
            src_code_filename=self.self_destruct_uploaded_malware,
            loc_to_inject="end",  # "main" or "end"
            wrap=False,  # Set to True to inject only after main()
            new_name=output_file,
        )

        if status == 0:
            self.success_label_self_destruct.config(text=f"Success! Embedded code saved to: {output_file}")
            try:
                with open(output_file, 'r') as f:
                    embedded_code = f.read()
                self.code_preview_self_destruct.delete(1.0, tk.END)
                self.code_preview_self_destruct.insert(tk.END, embedded_code)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the embedded code file: {e}")
        else:
            messagebox.showerror("Error", "An error occurred during embedding.")

    def create_check_vm_subtab(self):
        """Create the Check for VM subtab."""
        self.check_vm_frame = ttk.Frame(self.sub_notebook, padding="10")
        self.sub_notebook.add(self.check_vm_frame, text="Check for VM")

        # Variables specific to Check for VM
        self.anti_forensics_dir = "AntiForensics"
        self.vm_checks = []  # List to store selected VM checks
        self.vm_check_vars = {}  # Dictionary to store BooleanVars for checkboxes

        # UI Elements

        # Malware Code Upload Section
        ttk.Label(self.check_vm_frame, text="Upload Your Malware Code:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.upload_malware_btn_check_vm = ttk.Button(
            self.check_vm_frame, text="Upload Malware Code", command=self.upload_check_vm_malware
        )
        self.upload_malware_btn_check_vm.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Label to show upload status
        self.upload_status_check_vm = ttk.Label(self.check_vm_frame, text="No file uploaded.")
        self.upload_status_check_vm.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # VM Checks Selection
        ttk.Label(self.check_vm_frame, text="Select VM Detection Checks:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )

        # Frame to hold checkboxes
        self.vm_checks_frame = ttk.Frame(self.check_vm_frame)
        self.vm_checks_frame.grid(row=4, column=0, sticky="nw", padx=10, pady=10)

        # Dynamically load VM detection functions
        self.load_vm_checks()

        # Submit Button
        self.check_vm_submit_btn = ttk.Button(
            self.check_vm_frame, text="Embed VM Checks", command=self.submit_check_vm, padding=10
        )
        self.check_vm_submit_btn.grid(row=5, column=0, pady=10, sticky="ew")

        # Success Message Label
        self.success_label_check_vm = ttk.Label(self.check_vm_frame, text="", foreground="green")
        self.success_label_check_vm.grid(row=6, column=0, sticky="w", padx=5, pady=5)

        # Code Preview Text Widget with Scrollbar
        self.code_preview_check_vm = tk.Text(self.check_vm_frame, wrap=tk.WORD, background="#f0f0f0", height=15)
        self.code_preview_check_vm.grid(row=7, column=0, sticky="nsew", padx=5, pady=5)

        self.scrollbar_check_vm = ttk.Scrollbar(self.check_vm_frame, orient="vertical",
                                                command=self.code_preview_check_vm.yview)
        self.scrollbar_check_vm.grid(row=7, column=1, sticky="ns", pady=5)
        self.code_preview_check_vm.configure(yscrollcommand=self.scrollbar_check_vm.set)

        # Configure resizing
        self.check_vm_frame.columnconfigure(0, weight=1)
        self.check_vm_frame.rowconfigure(4, weight=1)
        self.check_vm_frame.rowconfigure(7, weight=1)

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
            self.upload_status_check_vm.config(text=f"Uploaded: {os.path.basename(filepath)}")
            # Clear previous success message and code preview
            self.success_label_check_vm.config(text="")
            self.code_preview_check_vm.delete(1.0, tk.END)

    def load_vm_checks(self):
        """Load VM detection functions from the AntiForensics directory."""
        python_files = glob.glob(os.path.join(self.anti_forensics_dir, "*.py"))
        if not python_files:
            ttk.Label(self.vm_checks_frame, text="No VM detection scripts found.").pack()
            return

        for filepath in python_files:
            filename = os.path.basename(filepath)
            if filename.endswith(".py"):
                func_name = f"call_{filename[:-3]}"  # e.g., detect_vmware_dir.py -> call_detect_vmware_dir
                display_name = filename[:-3]  # e.g., detect_vmware_dir
                description = f"Detects VM using {display_name.replace('_', ' ').title()} method."

                var = BooleanVar()
                cb = ttk.Checkbutton(self.vm_checks_frame, text=display_name, variable=var)
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
            self.success_label_check_vm.config(text=f"Success! Embedded code saved to: {output_file}")
            try:
                with open(output_file, 'r') as f:
                    embedded_code = f.read()
                self.code_preview_check_vm.delete(1.0, tk.END)
                self.code_preview_check_vm.insert(tk.END, embedded_code)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the embedded code file: {e}")
        else:
            messagebox.showerror("Error", "An error occurred during embedding.")

    def create_custom_subtab(self):
        """Create the Custom subtab."""
        self.custom_frame = ttk.Frame(self.sub_notebook, padding="10")
        self.sub_notebook.add(self.custom_frame, text="Custom")

        # Variables for user input
        self.original_code_path_custom = ""
        self.embed_code_path_custom = ""
        self.new_file_name_custom = StringVar()
        self.loc_to_inject_custom = StringVar(value="main")  # Default selection for location
        self.wrap_custom = BooleanVar(value=True)  # Default selection for wrap
        self.selected_function_custom = StringVar()

        # UI Elements

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.custom_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # Original Code Section
        ttk.Label(top_frame, text="Your Mal code:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.original_file_btn_custom = ttk.Button(
            top_frame, text="Upload Original Code", command=self.load_original_file_custom
        )
        self.original_file_btn_custom.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.show_original_btn_custom = ttk.Button(
            top_frame, text="Show Code", command=self.show_original_code_custom
        )
        self.show_original_btn_custom.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Create tooltip for the "Original Code" section
        original_tooltip_text = "This is where you put your original mal code like rev shells etc."
        ToolTip(info_icon, original_tooltip_text)

        # Spice Code Section
        ttk.Label(top_frame, text="Spice code:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.embed_file_btn_custom = ttk.Button(
            top_frame, text="Upload Embed Code", command=self.load_embed_file_custom
        )
        self.embed_file_btn_custom.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.show_embed_btn_custom = ttk.Button(
            top_frame, text="Show Code", command=self.show_embed_code_custom
        )
        self.show_embed_btn_custom.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        info_icon_spice = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_spice.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Create tooltip for the "Spice Code" section
        spice_tooltip_text = "This is the spice to be added to your malware (Self destruct feature/VM checker)"
        spice_tooltip = ToolTip(info_icon_spice, spice_tooltip_text)

        # Status Labels for uploads
        self.upload_status_original = ttk.Label(self.custom_frame, text="No original code uploaded.")
        self.upload_status_original.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.upload_status_embed = ttk.Label(self.custom_frame, text="No embed code uploaded.")
        self.upload_status_embed.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Middle Frame for function selection, file name, and options
        middle_frame = ttk.Frame(self.custom_frame)
        middle_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        middle_frame.columnconfigure(1, weight=1)

        # Function selection dropdown
        ttk.Label(middle_frame, text="Select Function to Inject:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.function_dropdown_custom = ttk.OptionMenu(middle_frame, self.selected_function_custom, "")
        self.function_dropdown_custom.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        info_icon_func = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_func.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Create tooltip for the function selection
        func_tooltip_text = "Function from your spice to be added to your malware code :)"
        func_tooltip = ToolTip(info_icon_func, func_tooltip_text)

        # New File Name entry
        ttk.Label(middle_frame, text="New File Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.file_name_entry_custom = ttk.Entry(middle_frame, textvariable=self.new_file_name_custom)
        self.file_name_entry_custom.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        info_icon_name = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_name.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # Create tooltip for the file name
        name_tooltip_text = "Name of the file it will be output to, default is Output/innocent.py"
        name_tooltip = ToolTip(info_icon_name, name_tooltip_text)

        # Button for "Location to Inject"
        ttk.Label(middle_frame, text="Location to Inject:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.location_frame_custom = ttk.Frame(middle_frame)
        self.location_frame_custom.grid(row=2, column=1, sticky="ew")

        self.main_button_custom = tk.Button(
            self.location_frame_custom,
            text="Main",
            command=lambda: self.select_location_custom("main"),
            bg="#4CAF50",
            fg="white",
            relief="raised",
        )
        self.main_button_custom.pack(side="left", fill="both", expand=True)  # Fill space and expand
        self.end_button_custom = tk.Button(
            self.location_frame_custom,
            text="End",
            command=lambda: self.select_location_custom("end"),
            bg="lightgray",
            fg="black",
            relief="raised",
        )
        self.end_button_custom.pack(side="left", fill="both", expand=True)  # Fill space and expand

        info_icon_loc = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_loc.grid(row=2, column=2, sticky="w", padx=5, pady=5)

        # Create tooltip for the "Location to Inject" section
        loc_tooltip_text = "Location in the code where you want to inject the selected function."
        loc_tooltip = ToolTip(info_icon_loc, loc_tooltip_text)

        # Button for "Wrap Main"
        ttk.Label(middle_frame, text="Wrap Main:").grid(row=3, column=0, sticky="e", padx=5, pady=5)

        self.wrap_frame_custom = ttk.Frame(middle_frame)
        self.wrap_frame_custom.grid(row=3, column=1, sticky="ew")

        self.yes_button_custom = tk.Button(
            self.wrap_frame_custom,
            text="Yes",
            command=lambda: self.select_wrap_custom(True),
            bg="#4CAF50",
            fg="white",
            relief="raised",
        )
        self.yes_button_custom.pack(side="left", fill="both", expand=True)  # Fill space and expand
        self.no_button_custom = tk.Button(
            self.wrap_frame_custom,
            text="No",
            command=lambda: self.select_wrap_custom(False),
            bg="lightgray",
            fg="black",
            relief="raised",
        )
        self.no_button_custom.pack(side="left", fill="both", expand=True)  # Fill space and expand

        # Create a label with an information icon
        info_icon_wrap = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_wrap.grid(row=3, column=2, sticky="w", padx=5, pady=5)

        # Create the tooltip for the wrap option
        wrap_tooltip_text = "Whether you want to wrap the injected function within an if-else condition pre-running main() function."
        wrap_tooltip = ToolTip(info_icon_wrap, wrap_tooltip_text)

        # Code Preview Title
        ttk.Label(self.custom_frame, text="Code Preview", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w",
                                                                                           padx=10, pady=(10, 0))

        # Code Display Box (for showing file content)
        self.code_display_box_custom = tk.Text(self.custom_frame, wrap=tk.WORD, background="#f0f0f0", height=10)
        self.code_display_box_custom.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

        # Submit button (sticks to the bottom)
        self.submit_btn_custom = ttk.Button(
            self.custom_frame, text="Submit", command=self.submit_custom, padding=10
        )
        self.submit_btn_custom.grid(row=6, column=0, pady=10, sticky="ew")

        # Result display (resizable) with Scrollbar
        self.result_box_custom = tk.Text(self.custom_frame, wrap=tk.WORD, background="#d9f0f0")
        self.result_box_custom.grid(row=7, column=0, sticky="nsew", padx=10, pady=10)

        self.scrollbar_custom = ttk.Scrollbar(self.custom_frame, orient="vertical",
                                              command=self.result_box_custom.yview)
        self.scrollbar_custom.grid(row=7, column=1, sticky="ns", pady=10)
        self.result_box_custom.configure(yscrollcommand=self.scrollbar_custom.set)

        # Configure resizing
        self.custom_frame.columnconfigure(0, weight=1)
        self.custom_frame.rowconfigure(5, weight=1)
        self.custom_frame.rowconfigure(7, weight=1)

        # Store uploaded file paths
        self.custom_uploaded_original = ""
        self.custom_uploaded_embed = ""

    def select_wrap_custom(self, wrap_value):
        """Select wrap option and update button colors for Custom mode."""
        self.wrap_custom.set(wrap_value)
        if wrap_value:
            self.yes_button_custom.config(bg="#4CAF50", fg="white")
            self.no_button_custom.config(bg="lightgray", fg="black")
        else:
            self.yes_button_custom.config(bg="lightgray", fg="black")
            self.no_button_custom.config(bg="#4CAF50", fg="white")

    def select_location_custom(self, location):
        """Select a location and update button colors for Custom mode."""
        self.loc_to_inject_custom.set(location)
        if location == "main":
            self.main_button_custom.config(bg="#4CAF50", fg="white")
            self.end_button_custom.config(bg="lightgray", fg="black")
        else:
            self.main_button_custom.config(bg="lightgray", fg="black")
            self.end_button_custom.config(bg="#4CAF50", fg="white")

    def create_dynamic_cipher_tab(self):
        """Create the Dynamic Cipher tab for runtime encryption and decryption of Python scripts."""
        self.dynamic_cipher_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.dynamic_cipher_frame, text="Dynamic Cipher")

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.dynamic_cipher_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # File Upload Section
        ttk.Label(top_frame, text="Your Python Code:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.upload_dynamic_cipher_btn = ttk.Button(
            top_frame, text="Upload Python Code", command=self.load_dynamic_cipher_file
        )
        self.upload_dynamic_cipher_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.show_dynamic_cipher_code_btn = ttk.Button(
            top_frame, text="Show Code", command=self.show_dynamic_cipher_code
        )
        self.show_dynamic_cipher_code_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tooltip for File Upload
        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        ToolTip(info_icon, "Upload a .py file for Dynamic Cipher encryption and decryption.")

        # Text box for displaying uploaded code (resizable)
        self.dynamic_cipher_code_display_box = tk.Text(self.dynamic_cipher_frame, wrap=tk.WORD, background="#f0f0f0",
                                                       height=10)
        self.dynamic_cipher_code_display_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Submit button for encryption and decryption script generation
        self.dynamic_cipher_submit_btn = ttk.Button(
            self.dynamic_cipher_frame, text="Encrypt and Generate Decryption Script",
            command=self.submit_dynamic_cipher, padding=10
        )
        self.dynamic_cipher_submit_btn.grid(row=2, column=0, pady=10, sticky="ew")

        # Result display area with Scrollbar
        self.dynamic_cipher_result_box = tk.Text(self.dynamic_cipher_frame, wrap=tk.WORD, background="#d9f0f0",
                                                 height=10)
        self.dynamic_cipher_result_box.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.dynamic_cipher_scrollbar = ttk.Scrollbar(
            self.dynamic_cipher_frame, orient="vertical", command=self.dynamic_cipher_result_box.yview
        )
        self.dynamic_cipher_scrollbar.grid(row=3, column=1, sticky="ns", pady=10)
        self.dynamic_cipher_result_box.configure(yscrollcommand=self.dynamic_cipher_scrollbar.set)

        # Configure resizing
        self.dynamic_cipher_frame.columnconfigure(0, weight=1)
        self.dynamic_cipher_frame.rowconfigure(1, weight=1)
        self.dynamic_cipher_frame.rowconfigure(3, weight=1)

    def load_dynamic_cipher_file(self):
        """Load the Python file for Dynamic Cipher encryption."""
        filepath = filedialog.askopenfilename(
            title="Select Python Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.dynamic_cipher_code_path = filepath
            self.dynamic_cipher_code_display_box.delete(1.0, tk.END)
            self.dynamic_cipher_code_display_box.insert(tk.END, f"Successfully uploaded: {os.path.basename(filepath)}")
            self.dynamic_cipher_result_box.delete(1.0, tk.END)

    def show_dynamic_cipher_code(self):
        """Display the content of the uploaded Python code file."""
        if self.dynamic_cipher_code_path:
            try:
                with open(self.dynamic_cipher_code_path, 'r') as f:
                    code_content = f.read()
                self.dynamic_cipher_code_display_box.delete(1.0, tk.END)
                self.dynamic_cipher_code_display_box.insert(tk.END, code_content)
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
            self.dynamic_cipher_result_box.delete(1.0, tk.END)
            self.dynamic_cipher_result_box.insert(
                tk.END, "Encryption and Decryption Script Generated Successfully!\n"
            )
            self.dynamic_cipher_result_box.insert(
                tk.END, f"File output to {status}\n"
            )
        else:
            self.dynamic_cipher_result_box.delete(1.0, tk.END)
            self.dynamic_cipher_result_box.insert(
                tk.END, "Encryption Failed! \n Please Debug this"
            )

    def create_py_compile_corrupt_tab(self):
        """Create the Corrupt Magic number of python script using magic number tab."""
        self.pyc_corrupt_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.pyc_corrupt_frame, text="PyCompile Corrupt Magic")

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.pyc_corrupt_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # File Upload Section
        ttk.Label(top_frame, text="Your Python Code:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.upload_pyc_corrupt_btn = ttk.Button(
            top_frame, text="Upload Python Code", command=self.load_pyc_corrupt_file
        )
        self.upload_pyc_corrupt_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.show_pyc_corrupt_code_btn = ttk.Button(
            top_frame, text="Show Code", command=self.show_pyc_corrupt_code
        )
        self.show_pyc_corrupt_code_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tooltip for File Upload
        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        ToolTip(info_icon, "Upload a .py file to corrupt the magic number.")

        # XOR Value Input
        ttk.Label(top_frame, text="XOR Value (Hex):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.xor_value_entry = ttk.Entry(top_frame)
        self.xor_value_entry.insert(0, "0xFF")  # Default value
        self.xor_value_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Tooltip for xor value
        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        ToolTip(info_icon, "XOR magic number value to xor compile your py file with.")

        # Text box for displaying uploaded code (resizable)
        self.pyc_corrupt_code_display_box = tk.Text(self.pyc_corrupt_frame, wrap=tk.WORD, background="#f0f0f0",
                                                    height=10)
        self.pyc_corrupt_code_display_box.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Submit button for corruption action
        self.pyc_corrupt_submit_btn = ttk.Button(
            self.pyc_corrupt_frame, text="Corrupt Magic Number", command=self.submit_pyc_corrupt, padding=10
        )
        self.pyc_corrupt_submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # Result display area with Scrollbar
        self.pyc_corrupt_result_box = tk.Text(self.pyc_corrupt_frame, wrap=tk.WORD, background="#d9f0f0", height=10)
        self.pyc_corrupt_result_box.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        self.pyc_corrupt_scrollbar = ttk.Scrollbar(
            self.pyc_corrupt_frame, orient="vertical", command=self.pyc_corrupt_result_box.yview
        )
        self.pyc_corrupt_scrollbar.grid(row=4, column=1, sticky="ns", pady=10)
        self.pyc_corrupt_result_box.configure(yscrollcommand=self.pyc_corrupt_scrollbar.set)

        # Configure resizing
        self.pyc_corrupt_frame.columnconfigure(0, weight=1)
        self.pyc_corrupt_frame.rowconfigure(2, weight=1)
        self.pyc_corrupt_frame.rowconfigure(4, weight=1)

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

        self.pyc_corrupt_result_box.delete(1.0, tk.END)
        if status:
            self.pyc_corrupt_result_box.insert(tk.END, f"Corruption Successful!\nOutput saved to: {output_file}\n")
        else:
            self.pyc_corrupt_result_box.insert(tk.END, "An error occurred during corruption.\n")

    def load_pyc_corrupt_file(self):
        """Load the Python file for PyCompile corruption."""
        filepath = filedialog.askopenfilename(
            title="Select Python Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.pyc_corrupt_code_path = filepath
            self.pyc_corrupt_code_display_box.delete(1.0, tk.END)
            self.pyc_corrupt_code_display_box.insert(tk.END, f"Successfully uploaded: {os.path.basename(filepath)}")
            self.pyc_corrupt_result_box.delete(1.0, tk.END)

    def show_pyc_corrupt_code(self):
        """Display the content of the uploaded Python code file."""
        if self.pyc_corrupt_code_path:
            try:
                with open(self.pyc_corrupt_code_path, 'r') as f:
                    code_content = f.read()
                self.pyc_corrupt_code_display_box.delete(1.0, tk.END)
                self.pyc_corrupt_code_display_box.insert(tk.END, code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read code file: {e}")
        else:
            messagebox.showerror("Error", "No Python code file uploaded.")

    def create_excel_macro_tab(self):
        """Create the Macro Excel Embedder tab."""
        self.excel_macro_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.excel_macro_frame, text="Macro Excel Embedder")

        # Configure dynamic resizing
        self.excel_macro_frame.columnconfigure(0, weight=1)
        self.excel_macro_frame.rowconfigure(3, weight=1)

        # Variables to store file paths
        self.malicious_python_path_excel_macro = ""
        self.excel_file_path_excel_macro = ""
        self.vba_macro_path_excel_macro = ""

        # Top Frame for uploading files
        top_frame = ttk.Frame(self.excel_macro_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        # Malicious Python Script Upload
        ttk.Label(top_frame, text="Malicious Python Script:").grid(row=0, column=0, sticky="w")
        self.upload_malicious_python_btn_excel_macro = ttk.Button(
            top_frame, text="Upload Script", command=self.load_malicious_python_excel_macro
        )
        self.upload_malicious_python_btn_excel_macro.grid(row=0, column=1, sticky="ew", padx=5)
        self.show_malicious_python_btn_excel_macro = ttk.Button(
            top_frame, text="Show", command=self.show_malicious_python_excel_macro
        )
        self.show_malicious_python_btn_excel_macro.grid(row=0, column=2, sticky="ew", padx=5)

        info_icon_script = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_script.grid(row=0, column=3, sticky="w", padx=5)
        ToolTip(info_icon_script, "Upload the Python script to embed as malicious code in the Excel file.")

        # Excel File Upload
        ttk.Label(top_frame, text="Excel File:").grid(row=1, column=0, sticky="w")
        self.upload_excel_file_btn_excel_macro = ttk.Button(
            top_frame, text="Upload Excel", command=self.load_excel_file_excel_macro
        )
        self.upload_excel_file_btn_excel_macro.grid(row=1, column=1, sticky="ew", padx=5)
        self.show_excel_file_btn_excel_macro = ttk.Button(
            top_frame, text="Show", command=self.show_excel_file_excel_macro
        )
        self.show_excel_file_btn_excel_macro.grid(row=1, column=2, sticky="ew", padx=5)

        info_icon_excel = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_excel.grid(row=1, column=3, sticky="w", padx=5)
        ToolTip(info_icon_excel, "Select the Excel file to embed the malicious code into.")

        # VBA Macro File Upload
        ttk.Label(top_frame, text="VBA Macro File:").grid(row=2, column=0, sticky="w")
        self.upload_vba_macro_btn_excel_macro = ttk.Button(
            top_frame, text="Upload Macro", command=self.load_vba_macro_excel_macro
        )
        self.upload_vba_macro_btn_excel_macro.grid(row=2, column=1, sticky="ew", padx=5)
        self.show_vba_macro_btn_excel_macro = ttk.Button(
            top_frame, text="Show", command=self.show_vba_macro_excel_macro
        )
        self.show_vba_macro_btn_excel_macro.grid(row=2, column=2, sticky="ew", padx=5)

        info_icon_macro = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_macro.grid(row=2, column=3, sticky="w", padx=5)
        ToolTip(info_icon_macro, "Upload the VBA macro script to embed along with the Python script in the Excel file.")

        # Text box for displaying file contents
        self.file_content_display_excel_macro = tk.Text(self.excel_macro_frame, wrap=tk.WORD, background="#f0f0f0",
                                                        height=10)
        self.file_content_display_excel_macro.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Submit Button
        self.submit_excel_macro_btn = ttk.Button(
            self.excel_macro_frame, text="Embed in Excel", command=self.submit_excel_macro, padding=10
        )
        self.submit_excel_macro_btn.grid(row=4, column=0, pady=10, sticky="ew")

    def load_malicious_python_excel_macro(self):
        """Load the malicious Python script file."""
        self.malicious_python_path_excel_macro = filedialog.askopenfilename(
            title="Select Python Script",
            filetypes=[("Python files", "*.py")],
        )
        if self.malicious_python_path_excel_macro:
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            self.file_content_display_excel_macro.insert(
                tk.END, f"Uploaded: {os.path.basename(self.malicious_python_path_excel_macro)}\n"
            )

    def show_malicious_python_excel_macro(self):
        """Display the content of the uploaded Python script file."""
        if self.malicious_python_path_excel_macro:
            with open(self.malicious_python_path_excel_macro, 'r') as f:
                content = f.read()
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            self.file_content_display_excel_macro.insert(tk.END, content)
        else:
            messagebox.showerror("Error", "No Python script uploaded.")

    def load_excel_file_excel_macro(self):
        """Load the Excel file to embed malicious code."""
        self.excel_file_path_excel_macro = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xls;*.xlsx")],
        )
        if self.excel_file_path_excel_macro:
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            self.file_content_display_excel_macro.insert(
                tk.END, f"Uploaded: {os.path.basename(self.excel_file_path_excel_macro)}\n"
            )

    def show_excel_file_excel_macro(self):
        """Display the content of the uploaded Excel file path."""
        if self.excel_file_path_excel_macro:
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            self.file_content_display_excel_macro.insert(
                tk.END, f"Excel File Path: {self.excel_file_path_excel_macro}\n"
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
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            self.file_content_display_excel_macro.insert(
                tk.END, f"Uploaded: {os.path.basename(self.vba_macro_path_excel_macro)}\n"
            )

    def show_vba_macro_excel_macro(self):
        """Display the content of the uploaded VBA macro file."""
        if self.vba_macro_path_excel_macro:
            with open(self.vba_macro_path_excel_macro, 'r') as f:
                content = f.read()
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            self.file_content_display_excel_macro.insert(tk.END, content)
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
            self.file_content_display_excel_macro.delete(1.0, tk.END)
            if result:
                self.file_content_display_excel_macro.insert(
                    tk.END, f"Embedding successful!\nOutput saved to: {output_excel_path}"
                )
            else:
                self.file_content_display_excel_macro.insert(
                    tk.END, f"Embedding Failed!\n"
                )

    def create_embed_in_pdf_tab(self):
        """Create the PDF Embedder tab with independent display for PDF embed process."""
        self.pdf_embed_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.pdf_embed_frame, text="PDF Embedder")

        # Ensure the main frame resizes correctly
        self.pdf_embed_frame.columnconfigure(0, weight=1)
        self.pdf_embed_frame.rowconfigure(1, weight=1)
        self.pdf_embed_frame.rowconfigure(3, weight=1)

        # Variables for PDF embedder inputs
        self.malware_code_path_pdf = ""
        self.public_key_path_pdf = ""
        self.pdf_folder_path = ""
        self.pdf_files_selected = {}

        # Top frame for malware file upload in PDF Embedder
        top_frame_pdf = ttk.Frame(self.pdf_embed_frame)
        top_frame_pdf.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame_pdf.columnconfigure(1, weight=1)
        top_frame_pdf.columnconfigure(3, weight=0)

        # Malware File upload section
        ttk.Label(top_frame_pdf, text="Malware File:").grid(row=0, column=0, sticky="w")
        self.malware_upload_btn_pdf = ttk.Button(top_frame_pdf, text="Upload Malware File",
                                                 command=self.load_malware_file_pdf)
        self.malware_upload_btn_pdf.grid(row=0, column=1, sticky="ew", padx=5)
        self.show_malware_btn_pdf = ttk.Button(top_frame_pdf, text="Show Malware Code",
                                               command=self.show_malware_code_pdf)
        self.show_malware_btn_pdf.grid(row=0, column=2, sticky="ew", padx=5)

        # Tooltip for Malware File upload
        info_icon_malware_pdf = tk.Label(top_frame_pdf, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_malware_pdf.grid(row=0, column=3, sticky="w", padx=5)
        malware_tooltip_text_pdf = "Upload a .py malware file to embed in PDF files."
        ToolTip(info_icon_malware_pdf, malware_tooltip_text_pdf)

        # Status Label for upload success/failure
        self.upload_status_label_pdf = ttk.Label(top_frame_pdf, text="No file uploaded.", foreground="blue")
        self.upload_status_label_pdf.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=5)

        # Subtab notebook for PEM Key Encryption Option
        subtab_notebook = ttk.Notebook(self.pdf_embed_frame)
        subtab_notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.pdf_embed_frame.rowconfigure(1, weight=1)  # Ensure notebook expands

        # PEM Key Encryption Subtab
        pdf_embed_subtab = ttk.Frame(subtab_notebook, padding="10")
        subtab_notebook.add(pdf_embed_subtab, text="PEM Key Encryption")

        # Configure rows and columns for dynamic resizing within PEM Key Encryption subtab
        pdf_embed_subtab.columnconfigure(0, weight=1)
        pdf_embed_subtab.rowconfigure(2, weight=1)
        pdf_embed_subtab.rowconfigure(4, weight=1)

        # Public Key PEM File Upload
        ttk.Label(pdf_embed_subtab, text="Public Key (PEM):").grid(row=0, column=0, sticky="w")
        self.upload_public_key_btn_pdf = ttk.Button(pdf_embed_subtab, text="Upload Public Key",
                                                    command=self.load_public_key_pdf)
        self.upload_public_key_btn_pdf.grid(row=0, column=1, sticky="ew", padx=5)
        self.show_public_key_btn_pdf = ttk.Button(pdf_embed_subtab, text="Show Public Key",
                                                  command=self.show_public_key_pdf)
        self.show_public_key_btn_pdf.grid(row=0, column=2, sticky="ew", padx=5)

        # Tooltip for Public Key
        info_icon_key_pdf = tk.Label(pdf_embed_subtab, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_key_pdf.grid(row=0, column=3, sticky="w", padx=5)
        public_key_tooltip_text_pdf = "Select an existing PEM public key to embed in PDFs."
        ToolTip(info_icon_key_pdf, public_key_tooltip_text_pdf)

        # PDF Folder selection for input files
        ttk.Label(pdf_embed_subtab, text="PDF Input Folder:").grid(row=1, column=0, sticky="w")
        self.folder_select_btn_pdf = ttk.Button(pdf_embed_subtab, text="Select Folder",
                                                command=self.select_pdf_folder_pdf)
        self.folder_select_btn_pdf.grid(row=1, column=1, sticky="ew", padx=5)

        # Tooltip for PDF Input Folder selection
        info_icon_folder_pdf = tk.Label(pdf_embed_subtab, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon_folder_pdf.grid(row=1, column=3, sticky="w", padx=5)
        folder_tooltip_text_pdf = "Choose the folder containing PDF files to embed the malware into."
        ToolTip(info_icon_folder_pdf, folder_tooltip_text_pdf)

        # PDF Checkboxes frame for file selection
        self.pdf_checkboxes_frame_pdf = ttk.Frame(pdf_embed_subtab)
        self.pdf_checkboxes_frame_pdf.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # Submit button and output result box
        self.submit_pdf_embed_btn = ttk.Button(pdf_embed_subtab, text="Submit", command=self.submit_pdf_embed,
                                               padding=10)
        self.submit_pdf_embed_btn.grid(row=3, column=0, columnspan=4, sticky="ew", pady=10)

        # Result Text box in Embedding Options subtab
        self.result_box_pdf_embed = tk.Text(pdf_embed_subtab, wrap=tk.WORD, background="#d9f0f0", height=10)
        self.result_box_pdf_embed.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # Status area in Embedding Options subtab
        self.keygen_status_label_pdf = ttk.Label(pdf_embed_subtab, text="", foreground="green")
        self.keygen_status_label_pdf.grid(row=5, column=0, columnspan=4, sticky="w", padx=10, pady=5)

        # Image Embedding Options Subtab
        image_embed_subtab = ttk.Frame(subtab_notebook, padding="10")
        subtab_notebook.add(image_embed_subtab, text="Image Steganography")

        # Configure rows and columns for dynamic resizing within Image Embedding Options subtab
        image_embed_subtab.columnconfigure(0, weight=1)
        image_embed_subtab.rowconfigure(1, weight=1)
        image_embed_subtab.rowconfigure(3, weight=1)

        # Image Input Folder selection
        ttk.Label(image_embed_subtab, text="Image Input Folder:").grid(row=0, column=0, sticky="w")
        self.folder_select_btn_image = ttk.Button(image_embed_subtab, text="Select Folder",
                                                  command=self.select_input_image_folder)
        self.folder_select_btn_image.grid(row=0, column=1, sticky="ew", padx=5)

        # Image Checkboxes frame for file selection
        self.image_checkboxes_frame = ttk.Frame(image_embed_subtab)
        self.image_checkboxes_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # Submit button and output result box
        self.submit_image_embed_btn = ttk.Button(image_embed_subtab, text="Submit", command=self.submit_image_embed,
                                                 padding=10)
        self.submit_image_embed_btn.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)

        # Result Text box in Image Embedding Options subtab
        self.result_box_image_embed = tk.Text(image_embed_subtab, wrap=tk.WORD, background="#d9f0f0", height=10)
        self.result_box_image_embed.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

    def load_malware_file_pdf(self):
        """Load the malware code file specifically for PDF Embedder."""
        self.malware_code_path_pdf = filedialog.askopenfilename(
            title="Select Malware File",
            filetypes=[("Python files", "*.py")]
        )
        if self.malware_code_path_pdf:
            self.upload_status_label_pdf.config(text=f"Uploaded: {os.path.basename(self.malware_code_path_pdf)}")
            with open(self.malware_code_path_pdf, 'r') as f:
                code_content = f.read()

            # Check if result_box_pdf_embed is visible before updating it
            if self.result_box_pdf_embed.winfo_viewable():
                self.result_box_pdf_embed.delete(1.0, tk.END)
                self.result_box_pdf_embed.insert(tk.END, f"Loaded Malware Code for PDF Embed:\n{code_content}\n")
            elif self.result_box_image_embed.winfo_viewable():
                self.result_box_image_embed.delete(1.0, tk.END)
                self.result_box_image_embed.insert(tk.END, f"Loaded Malware Code for PDF Embed:\n{code_content}\n")

    def load_public_key_pdf(self):
        """Load the PEM public key file for PDF Embedder."""
        self.public_key_path_pdf = filedialog.askopenfilename(
            title="Select Public Key",
            filetypes=[("PEM files", "*.pem")]
        )
        if self.public_key_path_pdf:
            self.keygen_status_label_pdf.config(text=f"Uploaded: {os.path.basename(self.public_key_path_pdf)}")

    def show_public_key_pdf(self):
        """Display the content of the uploaded PEM public key file."""
        if self.public_key_path_pdf:
            with open(self.public_key_path_pdf, 'r') as f:
                key_content = f.read()
            self.result_box_pdf_embed.delete(1.0, tk.END)
            self.result_box_pdf_embed.insert(tk.END, f"Loaded Public Key:\n{key_content}\n")
        else:
            messagebox.showerror("Error", "No public key file uploaded.")

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
            output_files = [output_folder / pdf for pdf in selected_pdfs]
            self.result_box_pdf_embed.delete(1.0, tk.END)
            self.result_box_pdf_embed.insert(tk.END, "Embedding successful!\nFiles saved to:\n")
            for file in output_files:
                self.result_box_pdf_embed.insert(tk.END, f"{file}\n")
            self.result_box_pdf_embed.insert(tk.END, "\nTo extract the malware, use:\n")
            self.result_box_pdf_embed.insert(tk.END,
                                             "Usage:\npython extract_pdf_rsa.py <private_key.pem> <pdf_file_1> <pdf_file_2> ... <output_python_file>\n")
        else:
            self.result_box_pdf_embed.insert(tk.END, "An error occurred during PDF embedding.")

    def show_malware_code_pdf(self):
        """Display the malware code in a text box."""
        if self.malware_code_path_pdf:
            with open(self.malware_code_path_pdf, 'r') as f:
                code_content = f.read()
            self.result_box_pdf_embed.delete(1.0, tk.END)
            self.result_box_pdf_embed.insert(tk.END, code_content)
        else:
            messagebox.showerror("Error", "No malware file uploaded.")

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
                checkbox = ttk.Checkbutton(self.pdf_checkboxes_frame_pdf, text=pdf_file, variable=var)
                checkbox.grid(row=i, column=0, sticky="w")
                full_path = os.path.join(self.pdf_folder_path, pdf_file)
                self.pdf_files_selected[full_path] = var

    def select_input_image_folder(self):
        """Select folder containing PDFs and display available files as checkboxes."""
        self.image_folder_path = filedialog.askdirectory(title="Select Image Folder")
        if self.image_folder_path:
            # Clear existing checkboxes in the pdf_checkboxes_frame
            for widget in self.image_checkboxes_frame.winfo_children():
                widget.destroy()

            # Display PDFs as checkboxes with full path stored
            image_files = [f for f in os.listdir(self.image_folder_path)
                           if (f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png"))]
            self.image_files_selected = {}
            for i, image_file in enumerate(image_files):
                var = IntVar(value=0)
                # Display filename only, store full path
                checkbox = ttk.Checkbutton(self.image_checkboxes_frame, text=image_file, variable=var)
                checkbox.grid(row=i, column=0, sticky="w")
                full_path = os.path.join(self.image_folder_path, image_file)
                self.image_files_selected[full_path] = var

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

        self.result_box_image_embed.delete(1.0, tk.END)
        # self.result_box_image_embed.insert(tk.END, f"Input values: {selected_images}\n{output_file_list}\n{input_secret_file}\n{output_pdf_file}\n")

        self.result_box_image_embed.insert(tk.END, "Encoding process started")
        res = stego.encode(selected_images, output_file_list, input_secret_file, output_pdf_file)
        if res:
            self.result_box_image_embed.insert(tk.END,
                                               f"\n\nDone! PDF path: {res} containing the stego image has been saved.")
        else:
            self.result_box_image_embed.insert(tk.END, "Image steganography/PDF Embedding failed due to error")

    def create_cython_tab(self):
        """Create the Compile with CythonCompile tab for taking a Python file input, showing code, and compiling with
        CythonCompile."""
        self.cython_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.cython_frame, text="Compile with CythonCompile")

        # Ensure the frame itself can resize
        self.cython_frame.columnconfigure(0, weight=1)
        self.cython_frame.rowconfigure(1, weight=1)
        self.cython_frame.rowconfigure(4, weight=1)

        # Initialize variables
        self.cython_code_path = ""
        self.cython_output_file_name = StringVar(value="")

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.cython_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # Python File Upload Section
        ttk.Label(top_frame, text="Python File to Compile:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.upload_cython_file_btn = ttk.Button(top_frame, text="Upload Python File", command=self.load_cython_file)
        self.upload_cython_file_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Info Icon and Tooltip for Upload
        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        cython_tooltip_text = "Upload a .py file to compile with CythonCompile. Only .py files are accepted."
        ToolTip(info_icon, cython_tooltip_text)

        # Display Box for code preview
        self.code_display_box_cython = tk.Text(self.cython_frame, wrap=tk.WORD, background="#f0f0f0", height=10)
        self.code_display_box_cython.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Middle Frame for output file name and options
        middle_frame = ttk.Frame(self.cython_frame)
        middle_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        middle_frame.columnconfigure(1, weight=1)

        # Output File Name Entry
        ttk.Label(middle_frame, text="Output File Name (.pyc):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.file_name_entry_cython = ttk.Entry(middle_frame, textvariable=self.cython_output_file_name)
        self.file_name_entry_cython.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Submit Button
        self.cython_submit_btn = ttk.Button(self.cython_frame, text="Submit", command=self.submit_cython, padding=10)
        self.cython_submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # Result display box for compilation output
        self.result_box_cython = tk.Text(self.cython_frame, wrap=tk.WORD, background="#d9f0f0", height=10)
        self.result_box_cython.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

    def load_cython_file(self):
        """Load the Python file for CythonCompile compilation."""
        self.cython_code_path = filedialog.askopenfilename(
            title="Select Python File to Compile",
            filetypes=[("Python files", "*.py")]
        )
        if self.cython_code_path:
            with open(self.cython_code_path, 'r') as f:
                code_content = f.read()
            self.code_display_box_cython.delete(1.0, tk.END)
            self.code_display_box_cython.insert(tk.END, code_content)

    def submit_cython(self):
        """Submit the file for compilation with CythonCompile."""
        input_file = self.cython_code_path
        output_file = self.cython_output_file_name.get().strip()

        if not input_file:
            messagebox.showerror("Error", "Please upload a Python file to compile.")
            return

        # Check if output file has .pyc extension, if not, add it
        if not output_file.endswith(".pyc"):
            output_file += ".pyc"

        # If no output file name specified, generate default unique name
        if not output_file or output_file == ".pyc":
            base_name = "CythonCompiled"
            counter = 0
            while os.path.exists(f"Output/{base_name}{counter}.pyc"):
                counter += 1
            output_file = f"{base_name}{counter}.pyc"

        # Create output directory if it doesn't exist
        os.makedirs("Output", exist_ok=True)
        output_path = os.path.join("Output", output_file)

        # Run the cython compiler
        success, location = self.cython_compiler(input_file, output_path)
        # success = adc.compile_with_cython(input_file, output_path)

        # Display results
        self.result_box_cython.delete(1.0, tk.END)
        if success:
            self.result_box_cython.insert(tk.END, f"Compilation Successful!\nOutput saved to: {output_path}")
        else:
            self.result_box_cython.insert(tk.END, "An error occurred during compilation.")

    def cython_compiler(self, input_file, output_file):
        """Compile a Python file using CythonCompile to produce a .pyc output."""
        try:
            # Actual CythonCompile compilation call, replace with your import and actual call from compile.py
            location = compile_with_cython(input_file, output_file)  # Replace with actual function call
            if location is not None:
                return True, location
            else:
                return False, None
        except Exception as e:
            print(f"Compilation Error: {e}")
            return False, None

    def create_qmorph_tab(self):
        """Create the QMorph Malware tab."""
        self.qmorph_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.qmorph_frame, text="QMorph Malware")

        # Initialize variables
        self.malware_code_path_qmorph = ""

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.qmorph_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # Malware Code Upload Section
        ttk.Label(top_frame, text="Your Malware Code:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.upload_malware_btn = ttk.Button(
            top_frame, text="Upload Malware Code", command=self.load_malware_file
        )
        self.upload_malware_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.show_malware_btn = ttk.Button(
            top_frame, text="Show Code", command=self.show_malware_code_qmorph
        )
        self.show_malware_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tooltip for Malware Code section
        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        malware_tooltip_text = "Upload your custom malware code (.py) for QMorph obfuscation."
        malware_tooltip = ToolTip(info_icon, malware_tooltip_text)

        # Code Preview title
        ttk.Label(self.qmorph_frame, text="Code Preview", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w",
                                                                                           padx=5, pady=(10, 2))

        # Text box to display uploaded code (resizable)
        self.code_display_box_qmorph = tk.Text(self.qmorph_frame, wrap=tk.WORD, background="#f0f0f0", height=10)
        self.code_display_box_qmorph.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # Submit button
        self.qmorph_submit_btn = ttk.Button(
            self.qmorph_frame, text="Submit", command=self.submit_qmorph, padding=10
        )
        self.qmorph_submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # Result display (resizable) with Scrollbar
        self.result_box_qmorph = tk.Text(self.qmorph_frame, wrap=tk.WORD, background="#d9f0f0", height=10)
        self.result_box_qmorph.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        self.scrollbar_qmorph = ttk.Scrollbar(self.qmorph_frame, orient="vertical",
                                              command=self.result_box_qmorph.yview)
        self.scrollbar_qmorph.grid(row=4, column=1, sticky="ns", pady=10)
        self.result_box_qmorph.configure(yscrollcommand=self.scrollbar_qmorph.set)

        # Configure resizing
        self.qmorph_frame.columnconfigure(0, weight=1)
        self.qmorph_frame.rowconfigure(2, weight=1)  # Ensures code display box is resizable
        self.qmorph_frame.rowconfigure(4, weight=1)  # Ensures result box is resizable

    def load_malware_file(self):
        """Load the malware code file for QMorph obfuscation."""
        filepath = filedialog.askopenfilename(
            title="Select Malware Code File",
            filetypes=[("Python files", "*.py")],
        )
        if filepath:
            self.malware_code_path_qmorph = filepath
            self.code_display_box_qmorph.delete(1.0, tk.END)
            self.code_display_box_qmorph.insert(tk.END,
                                                f"Successfully uploaded: {os.path.basename(self.malware_code_path_qmorph)}")
            # Clear previous result
            self.result_box_qmorph.delete(1.0, tk.END)

    def show_malware_code_qmorph(self):
        """Display the content of the uploaded malware code file in QMorph tab."""
        if self.malware_code_path_qmorph:
            try:
                with open(self.malware_code_path_qmorph, 'r') as f:
                    code_content = f.read()
                self.code_display_box_qmorph.delete(1.0, tk.END)
                self.code_display_box_qmorph.insert(tk.END, code_content)
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
        self.result_box_qmorph.delete(1.0, tk.END)
        if success:
            try:
                with open(output_file, 'r') as f:
                    result_content = f.read()
                self.result_box_qmorph.insert(
                    tk.END,
                    f"QMorph Obfuscation Successful!\nOutput saved to: {output_file}\n\n{result_content}",
                )
            except Exception as e:
                self.result_box_qmorph.insert(
                    tk.END,
                    f"QMorph Obfuscation Successful!\nOutput saved to: {output_file}\n\nError reading output file: {e}",
                )
        else:
            self.result_box_qmorph.insert(tk.END, "An error occurred during QMorph obfuscation.\n")
            self.result_box_qmorph.insert(tk.END, f"Error Message: {output_file}")

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
                self.result_box_custom.delete(1.0, tk.END)
                self.result_box_custom.insert(tk.END,
                                              f"Success! Embedded code saved to: {output_path}\n\n{result_code}")
            except Exception as e:
                self.result_box_custom.delete(1.0, tk.END)
                self.result_box_custom.insert(
                    tk.END, f"Success! Embedded code saved to: {output_path}\n\nError reading output file: {e}"
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
            self.upload_status_original.config(text=f"Uploaded: {os.path.basename(filepath)}")
            # Clear previous success message and code preview
            self.result_box_custom.delete(1.0, tk.END)

    def show_original_code_custom(self):
        """Display the content of the uploaded original code file in Custom mode."""
        if self.original_code_path_custom:
            try:
                with open(self.original_code_path_custom, 'r') as f:
                    code_content = f.read()
                self.code_display_box_custom.delete(1.0, tk.END)
                self.code_display_box_custom.insert(tk.END, code_content)
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
            self.upload_status_embed.config(text=f"Uploaded: {os.path.basename(filepath)}")

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
                self.code_display_box_custom.delete(1.0, tk.END)
                self.code_display_box_custom.insert(tk.END, code_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read embed code file: {e}")
        else:
            messagebox.showerror("Error", "No embed code file uploaded for Custom mode.")

    def populate_dropdown_custom(self, function_names):
        """Populate the dropdown with the extracted function names for Custom mode."""
        if not function_names:
            self.selected_function_custom.set("")
            menu = self.function_dropdown_custom["menu"]
            menu.delete(0, "end")
            return

        self.selected_function_custom.set(function_names[0])  # Set default selection
        menu = self.function_dropdown_custom["menu"]
        menu.delete(0, "end")
        for name in function_names:
            menu.add_command(label=name, command=lambda value=name: self.selected_function_custom.set(value))


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeEmbedderApp(root)
    root.mainloop()
