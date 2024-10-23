import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, BooleanVar, ttk
import os
import Code_Embedding.code_embedder as ce


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
        self.loc_to_inject = StringVar(value="main")  # Radio button option for 'loc_to_inject'
        self.wrap = BooleanVar(value=True)  # Radio button option for 'wrap'
        self.selected_function = StringVar()

        # Top Frame for file uploading and showing code
        top_frame = ttk.Frame(self.code_embedder_frame)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        # Original Code Section
        ttk.Label(top_frame, text="Original Code File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.original_file_btn = ttk.Button(top_frame, text="Upload Original Code", command=self.load_original_file)
        self.original_file_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.show_original_btn = ttk.Button(top_frame, text="Show Code", command=self.show_original_code)
        self.show_original_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Embed Code Section
        ttk.Label(top_frame, text="Embed Code File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.embed_file_btn = ttk.Button(top_frame, text="Upload Embed Code", command=self.load_embed_file)
        self.embed_file_btn.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.show_embed_btn = ttk.Button(top_frame, text="Show Code", command=self.show_embed_code)
        self.show_embed_btn.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

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

        # New File Name entry
        ttk.Label(middle_frame, text="New File Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.file_name_entry = ttk.Entry(middle_frame, textvariable=self.new_file_name)
        self.file_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Radio buttons for "Location to Inject"
        ttk.Label(middle_frame, text="Location to Inject:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        location_frame = ttk.Frame(middle_frame)
        location_frame.grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(location_frame, text="Main", variable=self.loc_to_inject, value="main").pack(side="left",
                                                                                                     padx=5)
        ttk.Radiobutton(location_frame, text="End", variable=self.loc_to_inject, value="end").pack(side="left", padx=5)

        # Radio buttons for "Wrap Main"
        ttk.Label(middle_frame, text="Wrap Main:").grid(row=3, column=0, sticky="e", padx=5, pady=5)

        wrap_frame = ttk.Frame(middle_frame)
        wrap_frame.grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(wrap_frame, text="Yes", variable=self.wrap, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(wrap_frame, text="No", variable=self.wrap, value=False).pack(side="left", padx=5)
        ttk.Label(middle_frame,
                  text="True/False Whether you want to wrap as an if else condition pre-running main() func").grid(
            row=3, column=2, sticky="e", padx=5, pady=5)

        # Submit button (sticks to the bottom)
        self.submit_btn = ttk.Button(self.code_embedder_frame, text="Submit", command=self.submit, padding=10)
        self.submit_btn.grid(row=3, column=0, pady=10, sticky="ew")

        # export display (resizable)
        self.result_box = tk.Text(self.code_embedder_frame, wrap=tk.WORD, background="#d9f0f0")
        self.result_box.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

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
        self.original_code_path = filedialog.askopenfilename(title="Select Original Code File",
                                                             filetypes=[("Python files", "*.py")])
        if self.original_code_path:
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Original Code File loaded successfully.\n")

    def load_embed_file(self):
        """Load the embed code file and populate the function dropdown."""
        self.embed_code_path = filedialog.askopenfilename(title="Select Embed Code File",
                                                          filetypes=[("Python files", "*.py")])
        if self.embed_code_path:
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Embed Code File loaded successfully.\n")
            # Extract functions and populate dropdown
            imports, functions = self.extract_functions_and_imports(self.embed_code_path)
            function_names = [func.name for func in functions]
            self.populate_dropdown(function_names)

    def show_original_code(self):
        """Display the content of the original code file."""
        if self.original_code_path:
            with open(self.original_code_path, 'r') as f:
                code_content = f.read()
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, code_content)
        else:
            messagebox.showerror("Error", "Original Code File is not loaded.")

    def show_embed_code(self):
        """Display the content of the embed code file."""
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

    def extract_functions_and_imports(self, filepath):
        """Extract function definitions from the uploaded code file."""
        return ce.extract_functions_and_imports(filepath)

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


# Main GUI execution
if __name__ == "__main__":
    root = tk.Tk()
    app = CodeEmbedderApp(root)
    root.mainloop()
