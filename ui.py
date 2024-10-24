import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, BooleanVar, ttk
import os
import Code_Embedding.code_embedder as ce


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
        label = tk.Label(self.tooltip_window, text=self.text, background="lightyellow",
                         relief="solid", borderwidth=1, wraplength=max_width)  # Added wraplength
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class CodeEmbedderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Malware Tool Suite")

        # Make the window resizable
        self.root.columnconfigure(0, weight=1)  # Allow the main notebook to expand horizontally
        self.root.rowconfigure(0, weight=1)  # Allow the notebook to expand vertically

        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Allow notebook to expand and contract with window

        # Add the tabs
        self.create_code_embedder_tab()
        self.create_excel_macro_tab()
        self.create_qmorph_tab()
        self.create_cython_tab()

    def extract_functions_and_imports(self, filepath):
        """Extract function definitions from the uploaded code file."""
        return ce.extract_functions_and_imports(filepath)

    def create_code_embedder_tab(self):
        """Create the Code Embedder tab."""
        self.code_embedder_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.code_embedder_frame, text="Code Embedder")

        # Ensure the frame itself can resize
        self.code_embedder_frame.columnconfigure(0, weight=1)
        self.code_embedder_frame.rowconfigure(1, weight=1)

        # Variables for user input
        self.original_code_path = ""
        self.embed_code_path = ""
        self.new_file_name = StringVar()
        self.loc_to_inject = StringVar(value="main")  # Default selection for location
        self.wrap = BooleanVar(value=True)  # Default selection for wrap
        self.selected_function = StringVar()

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.code_embedder_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # Original Code Section
        ttk.Label(top_frame, text="Your Mal code:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.original_file_btn = ttk.Button(top_frame, text="Upload Original Code", command=self.load_original_file)
        self.original_file_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.show_original_btn = ttk.Button(top_frame, text="Show Code", command=self.show_original_code)
        self.show_original_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Create tooltip for the "End" button
        original_tooltip_text = "This is where you put your original mal code like rev shells etc."
        original_tooltip = ToolTip(info_icon, original_tooltip_text)

        # Spice Code Section
        ttk.Label(top_frame, text="Spice code:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.embed_file_btn = ttk.Button(top_frame, text="Upload Embed Code", command=self.load_embed_file)
        self.embed_file_btn.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.show_embed_btn = ttk.Button(top_frame, text="Show Code", command=self.show_embed_code)
        self.show_embed_btn.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        info_icon = tk.Label(top_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Create tooltip for the "End" button
        spice_tooltip_text = "This is the spice to be added to your malware (Self destruct feature/VM checker)"
        spice_tooltip = ToolTip(info_icon, spice_tooltip_text)

        # Text box to display code content (resizable)
        self.code_display_box = tk.Text(self.code_embedder_frame, wrap=tk.WORD, background="#f0f0f0")
        self.code_display_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Middle Frame for function selection, file name, and options
        middle_frame = ttk.Frame(self.code_embedder_frame)
        middle_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        middle_frame.columnconfigure(1, weight=1)

        # Function selection dropdown
        ttk.Label(middle_frame, text="Select Function to Inject:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.function_dropdown = ttk.OptionMenu(middle_frame, self.selected_function, "")
        self.function_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        info_icon = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Create tooltip for the "End" button
        func_tooltip_text = "Function from your the spice to be added to your malware code :)"
        func_tooltip = ToolTip(info_icon, func_tooltip_text)

        # New File Name entry
        # Initialize the StringVar with the default value
        self.new_file_name = StringVar(value="Output\innocent.py")

        # New File Name entry
        ttk.Label(middle_frame, text="New File Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.file_name_entry = ttk.Entry(middle_frame, textvariable=self.new_file_name)  # Use StringVar here
        self.file_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        info_icon = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # Create tooltip for the "End" button
        name_tooltip_text = "Name of the file it will be output to, default is Output/innocent.py"
        name_tooltip = ToolTip(info_icon, name_tooltip_text)

        # Button for "Location to Inject"
        ttk.Label(middle_frame, text="Location to Inject:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.location_frame = ttk.Frame(middle_frame)
        self.location_frame.grid(row=2, column=1, sticky="ew")

        self.main_button = tk.Button(self.location_frame, text="Main", command=lambda: self.select_location("main"),
                                     bg="#4CAF50", fg="white", relief="raised")
        self.main_button.pack(side="left", fill="both", expand=True)  # Fill space and expand
        self.end_button = tk.Button(self.location_frame, text="End", command=lambda: self.select_location("end"),
                                    bg="lightgray", fg="black", relief="raised")
        self.end_button.pack(side="left", fill="both", expand=True)  # Fill space and expand

        info_icon = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=2, column=2, sticky="w", padx=5, pady=5)

        # Create tooltip for the "End" button
        end_tooltip_text = "Main/end the loc of code where you want to put the injected function"
        end_tooltip = ToolTip(info_icon, end_tooltip_text)

        # Button for "Wrap Main"
        ttk.Label(middle_frame, text="Wrap Main:").grid(row=3, column=0, sticky="e", padx=5, pady=5)

        self.wrap_frame = ttk.Frame(middle_frame)
        self.wrap_frame.grid(row=3, column=1, sticky="ew")

        self.yes_button = tk.Button(self.wrap_frame, text="Yes", command=lambda: self.select_wrap(True), bg="#4CAF50",
                                    fg="white", relief="raised")
        self.yes_button.pack(side="left", fill="both", expand=True)  # Fill space and expand
        self.no_button = tk.Button(self.wrap_frame, text="No", command=lambda: self.select_wrap(False), bg="lightgray",
                                   fg="black", relief="raised")
        self.no_button.pack(side="left", fill="both", expand=True)  # Fill space and expand
        # Create a label with an information icon
        info_icon = tk.Label(middle_frame, text="ℹ️", font=("Arial", 14), cursor="hand2")
        info_icon.grid(row=3, column=2, sticky="w", padx=5, pady=5)

        # Create the tooltip for the info icon
        tooltip_text = "True/False Whether you want to wrap as an if else condition pre-running main() func"
        tooltip = ToolTip(info_icon, tooltip_text)

        # Submit button (sticks to the bottom)
        self.submit_btn = ttk.Button(self.code_embedder_frame, text="Submit", command=self.submit, padding=10)
        self.submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # export display (resizable)
        self.result_box = tk.Text(self.code_embedder_frame, wrap=tk.WORD, background="#d9f0f0")
        self.result_box.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

        # Set default selections to the first buttons
        self.select_location("main")
        self.select_wrap(True)

    def select_location(self, location):
        """Select a location and update button colors."""
        self.loc_to_inject.set(location)
        if location == "main":
            self.main_button.config(bg="#4CAF50", fg="white")
            self.end_button.config(bg="lightgray", fg="black")
        else:
            self.main_button.config(bg="lightgray", fg="black")
            self.end_button.config(bg="#4CAF50", fg="white")

    def select_wrap(self, wrap_value):
        """Select wrap option and update button colors."""
        self.wrap.set(wrap_value)
        if wrap_value:
            self.yes_button.config(bg="#4CAF50", fg="white")
            self.no_button.config(bg="lightgray", fg="black")
        else:
            self.yes_button.config(bg="lightgray", fg="black")
            self.no_button.config(bg="#4CAF50", fg="white")

    def update_button_colors(self, value, button_type):
        """Update button colors based on selection."""
        if button_type == "location":
            if value == "main":
                self.main_button.config(bg="lightblue")
                self.end_button.config(bg="lightgray")
            else:
                self.main_button.config(bg="lightgray")
                self.end_button.config(bg="lightblue")
        elif button_type == "wrap":
            if value:
                self.wrap_yes_button.config(bg="lightblue")
                self.wrap_no_button.config(bg="lightgray")
            else:
                self.wrap_yes_button.config(bg="lightgray")
                self.wrap_no_button.config(bg="lightblue")

    def create_excel_macro_tab(self):
        """Create the Macro Excel Creator tab (Placeholder)."""
        self.excel_macro_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.excel_macro_frame, text="Macro Excel Creator")
        ttk.Label(self.excel_macro_frame, text="Excel Macro Creator will go here.").grid(row=0, column=0, sticky="nsew")

    def create_qmorph_tab(self):
        """Create the QMorph Malware tab (Placeholder)."""
        self.qmorph_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.qmorph_frame, text="QMorph Malware")
        ttk.Label(self.qmorph_frame, text="QMorph Malware obfuscation will go here.").grid(row=0, column=0,
                                                                                           sticky="nsew")

    def create_cython_tab(self):
        """Create the Compile with Cython tab (Placeholder)."""
        self.cython_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.cython_frame, text="Compile with Cython")
        ttk.Label(self.cython_frame, text="Cython compilation will go here.").grid(row=0, column=0, sticky="nsew")

    def load_original_file(self):
        """Load the original code file."""
        self.original_code_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.py")])
        if self.original_code_path:
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Original Code File loaded successfully.\n")

    def load_embed_file(self):
        """Load the embed code file."""
        self.embed_code_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.py")])
        if self.embed_code_path:
            print(f"Embed code loaded: {self.embed_code_path}")
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Embed Code File loaded successfully.\n")
            # Extract functions and populate dropdown
            imports, functions = self.extract_functions_and_imports(self.embed_code_path)
            function_names = [func.name for func in functions]
            self.populate_dropdown(function_names)

    def show_original_code(self):
        """Show the original code in the text box."""
        if self.original_code_path:
            with open(self.original_code_path, 'r') as f:
                code_content = f.read()
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, code_content)
        else:
            messagebox.showerror("Error", "Original Code File is not loaded.")

    def show_embed_code(self):
        """Show the embed code in the text box."""
        if self.embed_code_path:
            with open(self.embed_code_path, 'r') as f:
                code_content = f.read()
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, code_content)
        else:
            messagebox.showerror("Error", "Embed Code File is not loaded.")

    def populate_dropdown(self, function_names):
        """Populate the dropdown with the extracted function names."""
        self.selected_function.set(function_names[0] if function_names else "")
        menu = self.function_dropdown["menu"]
        menu.delete(0, "end")
        for name in function_names:
            menu.add_command(label=name, command=lambda value=name: self.selected_function.set(value))

    def submit(self):
        """Perform the embedding process and display the final code output."""
        new_name = self.new_file_name.get()
        loc_to_inject = self.loc_to_inject.get()
        func_name = self.selected_function.get()
        wrap = self.wrap.get()

        if not self.original_code_path or not self.embed_code_path:
            messagebox.showerror("Error", "Please upload both the original and embed code files.")
            return

        if not new_name:
            messagebox.showerror("Error", "Please specify a new name for the output file.")
            return

        # Perform embedding using the code_embedder module
        status = ce.embed_code(embed_code_filename=self.embed_code_path, src_code_filename=self.original_code_path,
                               loc_to_inject=loc_to_inject, func_name=func_name, wrap=wrap, new_name=new_name)

        if status == 0:
            output_path = os.path.join(os.getcwd(), new_name if new_name.endswith(".py") else new_name + ".py")
            with open(output_path, 'r') as f:
                result_code = f.read()
            self.result_box.delete(1.0, tk.END)
            self.result_box.insert(tk.END, f"Final Code Output (saved to {output_path}):\n{result_code}\n")
        else:
            messagebox.showerror("Error", "An error occurred during code embedding.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeEmbedderApp(root)
    root.mainloop()
