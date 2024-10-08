import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, BooleanVar, ttk
import ast
import astor
import os
import code_embedder as ce

class CodeEmbedderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Embedder")

        # Make the window resizable
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(7, weight=1)  # Allow the result box to expand

        # Apply a theme for a modern look
        self.root.tk.call('lappend', 'auto_path', '/usr/local/ttk')
        self.root.tk.call('package', 'require', 'tile')
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Set the theme (clam, alt, etc.)

        # Define variables to store file paths and options
        self.original_code_path = ""
        self.embed_code_path = ""
        self.new_file_name = StringVar()
        self.loc_to_inject = StringVar(value="main")
        self.wrap = BooleanVar(value=True)
        self.selected_function = StringVar()

        # Top Frame for file uploading
        self.top_frame = ttk.Frame(root, padding="10")
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")


        ttk.Label(self.top_frame, text="Original Code File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.original_file_btn = ttk.Button(self.top_frame, text="Upload Original Code", command=self.load_original_file,
                                            width=20)
        self.original_file_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.show_original_btn = ttk.Button(self.top_frame, text="Show Original Code", command=self.show_original_code, width=20)
        self.show_original_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        ttk.Label(self.top_frame, text="Embed Code File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.embed_file_btn = ttk.Button(self.top_frame, text="Upload Embed Code", command=self.load_embed_file, width=20)
        self.embed_file_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.show_embed_btn = ttk.Button(self.top_frame, text="Show Embed Code", command=self.show_embed_code, width=20)
        self.show_embed_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")


        # Buttons to display original and embed code
        self.show_original_btn = ttk.Button(self.top_frame, text="Show Original Code", command=self.show_original_code)
        self.show_original_btn.grid(row=0, column=2)

        self.show_embed_btn = ttk.Button(self.top_frame, text="Show Embed Code", command=self.show_embed_code)
        self.show_embed_btn.grid(row=1, column=2)

        # Display Box for showing the code files
        self.code_display_box = tk.Text(root, height=10, width=80, wrap=tk.WORD, background="#f0f0f0")
        self.code_display_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # # Middle Frame for function selection, file name, and options
        # self.middle_frame = ttk.Frame(root, padding="10")
        # self.middle_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        #
        # # Function selection dropdown
        # ttk.Label(self.middle_frame, text="Select Function to Inject:").grid(row=0, column=0, sticky="w")
        # self.function_dropdown = ttk.OptionMenu(self.middle_frame, self.selected_function, "")
        # self.function_dropdown.grid(row=0, column=1)
        #
        # # New File Name entry
        # ttk.Label(self.middle_frame, text="New File Name:").grid(row=1, column=0, sticky="w")
        # self.file_name_entry = ttk.Entry(self.middle_frame, textvariable=self.new_file_name, width=30)
        # self.file_name_entry.grid(row=1, column=1)
        #
        # # Location to Inject option
        # ttk.Label(self.middle_frame, text="Location to Inject:").grid(row=2, column=0, sticky="w")
        # ttk.Radiobutton(self.middle_frame, text="Main", variable=self.loc_to_inject, value="main").grid(row=2, column=1)
        # ttk.Radiobutton(self.middle_frame, text="End", variable=self.loc_to_inject, value="end").grid(row=2, column=2)
        #
        # # Toggle for wrapping main
        # ttk.Label(self.middle_frame, text="Wrap Main:").grid(row=3, column=0, sticky="w")
        # ttk.Radiobutton(self.middle_frame, text="Yes", variable=self.wrap, value=True).grid(row=3, column=1)
        # ttk.Radiobutton(self.middle_frame, text="No", variable=self.wrap, value=False).grid(row=3, column=2)
        # Middle Frame for function selection, file name, and options
        self.middle_frame = ttk.Frame(root, padding="10")
        self.middle_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Function selection dropdown
        ttk.Label(self.middle_frame, text="Select Function to Inject:").grid(row=0, column=0, sticky="e", padx=5,
                                                                             pady=5)
        self.function_dropdown = ttk.OptionMenu(self.middle_frame, self.selected_function, "")
        self.function_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # New File Name entry
        ttk.Label(self.middle_frame, text="New File Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.file_name_entry = ttk.Entry(self.middle_frame, textvariable=self.new_file_name, width=30)
        self.file_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Location to Inject option
        ttk.Label(self.middle_frame, text="Location to Inject:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        location_frame = ttk.Frame(self.middle_frame)
        location_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(location_frame, text="Main", variable=self.loc_to_inject, value="main").pack(side="left",
                                                                                                     padx=5)
        ttk.Radiobutton(location_frame, text="End", variable=self.loc_to_inject, value="end").pack(side="left", padx=5)

        # Toggle for wrapping main
        ttk.Label(self.middle_frame, text="Wrap Main:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        wrap_frame = ttk.Frame(self.middle_frame)
        wrap_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(wrap_frame, text="Yes", variable=self.wrap, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(wrap_frame, text="No", variable=self.wrap, value=False).pack(side="left", padx=5)

        # Submit button
        self.submit_btn = ttk.Button(root, text="Submit", command=self.submit, padding=10)
        self.submit_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Progress bar for the submission process
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=2, pady=10)

        # Final result display box
        self.result_box = tk.Text(root, height=10, width=80, wrap=tk.WORD, background="#d9f0f0")
        self.result_box.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def load_original_file(self):
        """
        Load the original code file.
        """
        self.original_code_path = filedialog.askopenfilename(title="Select Original Code File",
                                                             filetypes=[("Python files", "*.py")])
        if self.original_code_path:
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Original Code File loaded successfully.")

    def load_embed_file(self):
        """
        Load the embed code file and populate the function dropdown.
        """
        self.embed_code_path = filedialog.askopenfilename(title="Select Embed Code File",
                                                          filetypes=[("Python files", "*.py")])
        if self.embed_code_path:
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Embed Code File loaded successfully.")
            # Extract functions and populate dropdown
            imports, functions = self.extract_functions_and_imports(self.embed_code_path)
            function_names = [func.name for func in functions]
            self.populate_dropdown(function_names)

    def show_original_code(self):
        """
        Display original code.
        """
        if self.original_code_path:
            with open(self.original_code_path, 'r') as f:
                code = f.read()
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Original Code:\n{code}\n")
        else:
            messagebox.showerror("Error", "Please upload the original code file.")

    def show_embed_code(self):
        """
        Display embed code.
        """
        if self.embed_code_path:
            with open(self.embed_code_path, 'r') as f:
                code = f.read()
            self.code_display_box.delete(1.0, tk.END)
            self.code_display_box.insert(tk.END, f"Embed Code:\n{code}\n")
        else:
            messagebox.showerror("Error", "Please upload the embed code file.")

    def populate_dropdown(self, function_names):
        """
        Populate the dropdown with the extracted function names.
        """
        self.selected_function.set(function_names[0] if function_names else "")
        menu = self.function_dropdown["menu"]
        menu.delete(0, "end")
        for name in function_names:
            menu.add_command(label=name, command=lambda value=name: self.selected_function.set(value))

    def extract_functions_and_imports(self, filepath):
        """
        Extract function definitions from the uploaded code file.
        """
        return ce.extract_functions_and_imports(filepath)

    def submit(self):
        """
        Perform the embedding process and display final code output.
        """
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

        # Simulate progress for user feedback
        self.progress.start(10)

        status = ce.embed_code(embed_code_filename=self.embed_code_path, src_code_filename=self.original_code_path,
                               loc_to_inject=loc_to_inject, func_name=func_name, wrap=wrap, new_name=new_name)

        self.progress.stop()

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
