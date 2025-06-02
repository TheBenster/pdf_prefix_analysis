import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading
 
class PDFAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF File Analyzer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
       
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
       
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
       
        # Title
        title_label = ttk.Label(main_frame, text="PDF File Analyzer",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
       
        # Folder selection area
        self.create_folder_selection_area(main_frame)
       
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
       
        # Browse button
        self.browse_btn = ttk.Button(button_frame, text="Browse Folder",
                                    command=self.browse_folder)
        self.browse_btn.pack(side=tk.LEFT, padx=(0, 10))
       
        # Analyze button
        self.analyze_btn = ttk.Button(button_frame, text="Analyze",
                                     command=self.start_analysis, state='disabled')
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
       
        # Clear button
        self.clear_btn = ttk.Button(button_frame, text="Clear Results",
                                   command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT)
       
        # Progress bar
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
       
        # Results area
        self.create_results_area(main_frame)
       
        # Selected folder label
        self.folder_label = ttk.Label(main_frame, text="No folder selected",
                                     foreground='gray')
        self.folder_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
       
        self.selected_folder = None
       
    def create_folder_selection_area(self, parent):
        # Folder selection frame
        self.folder_frame = tk.Frame(parent, bg='lightblue', relief='ridge',
                                    bd=2, height=80)
        self.folder_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E),
                              pady=(30, 10))
        self.folder_frame.grid_propagate(False)
       
        # Folder selection label
        folder_label = tk.Label(self.folder_frame,
                               text="Click 'Browse Folder' to select a folder for analysis",
                               bg='lightblue', font=('Arial', 11))
        folder_label.place(relx=0.5, rely=0.5, anchor='center')
       
    def create_results_area(self, parent):
        # Results frame with notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S),
                          pady=10)
       
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
       
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame,
                                                     wrap=tk.WORD, height=15)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Files Found tab
        self.files_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.files_frame, text="Files Found")
       
        self.files_text = scrolledtext.ScrolledText(self.files_frame,
                                                   wrap=tk.WORD, height=15)
        self.files_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Issues tab
        self.issues_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.issues_frame, text="Issues")
       
        self.issues_text = scrolledtext.ScrolledText(self.issues_frame,
                                                    wrap=tk.WORD, height=15)
        self.issues_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
    def browse_folder(self):
        """Open folder browser dialog"""
        folder_path = filedialog.askdirectory(title="Select folder to analyze")
        if folder_path:
            self.selected_folder = folder_path
            self.folder_label.config(text=f"Selected: {folder_path}")
            self.analyze_btn.config(state='normal')
            self.folder_frame.config(bg='lightgreen')
           
            # Update the label in the frame
            for widget in self.folder_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(text=f"Selected: {os.path.basename(folder_path)}",
                                 bg='lightgreen')
           
    def start_analysis(self):
        """Start analysis in a separate thread"""
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
           
        # Disable button and start progress
        self.analyze_btn.config(state='disabled')
        self.progress.start()
       
        # Run analysis in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
       
    def run_analysis(self):
        """Run the PDF analysis"""
        try:
            results = self.analyze_pdf_files(self.selected_folder)
            # Update GUI in main thread
            self.root.after(0, self.display_results, results)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.analysis_complete)
           
    def analysis_complete(self):
        """Called when analysis is complete"""
        self.progress.stop()
        self.analyze_btn.config(state='normal')
       
    def show_error(self, error_message):
        """Show error message"""
        messagebox.showerror("Analysis Error", f"An error occurred:\n{error_message}")
       
    def clear_results(self):
        """Clear all results"""
        self.summary_text.delete('1.0', tk.END)
        self.files_text.delete('1.0', tk.END)
        self.issues_text.delete('1.0', tk.END)
       
    def analyze_pdf_files(self, directory_path, recursive=True):
        """The original analysis function"""
        # imperative files/names
        id_prefixes = ['02_ID_', '02_IDs_', '02_ID1_', '02_ID2_']
        title_prefixes = ['04_TITLE_', '04_DEED_', '04_TITLE-']
        other_prefixes = ['01_ROE_']
        all_prefixes = other_prefixes + id_prefixes + title_prefixes
       
        # convert to Path object
        search_path = Path(directory_path)
       
        if not search_path.exists():
            raise Exception(f"Directory '{directory_path}' does not exist.")
       
        # find all PDF files
        if recursive:
            pdf_files = list(search_path.glob('**/*.pdf'))
        else:
            pdf_files = list(search_path.glob('*.pdf'))
       
        # initialize tracking
        results = {
            'files_by_prefix': {prefix: [] for prefix in all_prefixes},
            'folders_missing_prefixes': {},
            'files_without_tt': [],
            'folder_analysis': {},
            'total_files': len(pdf_files),
            'search_path': str(search_path.absolute())
        }
       
        # track what each folder has
        folder_prefixes = {}
       
        # analyze each PDF file title
        for pdf_file in pdf_files:
            filename = pdf_file.name
            folder_path = str(pdf_file.parent)
           
            # initialize folder tracking/ whereabouts
            if folder_path not in folder_prefixes:
                folder_prefixes[folder_path] = set()
           
            # check against each prefix using wildcard matching
            matched_prefix = None
            for prefix in all_prefixes:
                # create pattern: prefix + anything + .pdf
                pattern = f"{re.escape(prefix)}.*\\.pdf$"
                if re.match(pattern, filename, re.IGNORECASE):
                    results['files_by_prefix'][prefix].append(str(pdf_file))
                    folder_prefixes[folder_path].add(prefix)
                    matched_prefix = prefix
                    break
           
            # check ROE pattern for matched files
            if matched_prefix:
                # Check if TT-BC appears anywhere in the full file path
               
                if 'TT-BC' not in filename:
                    results['files_without_tt'].append({
                        'file': str(pdf_file),
                        'prefix': matched_prefix,
                        'issue': f'TT-BC not found anywhere in file name'
                    })
       
        # analyze folder completeness
        for folder, found_prefixes in folder_prefixes.items():
            missing = []
           
            # check for 01_ROE_
            if '01_ROE_' not in found_prefixes:
                # if missing, append to specific TT number folder
                missing.append('01_ROE_')
               
           
            # check for ID requirement (any of the ID variations, ID, IDs, ID1, ID2)
            has_id = any(id_prefix in found_prefixes for id_prefix in id_prefixes)
            if not has_id:
                missing.append('02_ID_ (or ID1_/ID2_/IDs_)')
           
            # check for TITLE/DEED requirement (any of the title variations)
            has_title = any(title_prefix in found_prefixes for title_prefix in title_prefixes)
            if not has_title:
                missing.append('04_TITLE_ or 04_DEED_')
           
            if missing:
                results['folders_missing_prefixes'][folder] = missing
       
        # check folders with PDFs but no matching prefixes
        all_pdf_folders = set()
        for pdf_file in pdf_files:
            all_pdf_folders.add(str(pdf_file.parent))
       
        folders_with_no_matches = all_pdf_folders - set(folder_prefixes.keys())
        for folder in folders_with_no_matches:
            results['folders_missing_prefixes'][folder] = ['01_ROE_', '02_ID_ (or ID1_/ID2_/IDs_)', '04_TITLE_ or 04_DEED_']
       
        return results
   
    def display_results(self, results):
        # display analysis results in the GUI
        self.clear_results()
       
        # display summary
        summary = self.generate_summary(results)
        self.summary_text.insert(tk.END, summary)
       
        # display issues
        issues_info = self.generate_issues_info(results)
        self.issues_text.insert(tk.END, issues_info)
 
        # display files found
        files_info = self.generate_files_info(results)
        self.files_text.insert(tk.END, files_info)
       
       
       
    def generate_summary(self, results):
        """Generate summary text"""
        summary = f"ANALYSIS SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        summary += f"Search Path: {results['search_path']}\n"
        summary += f"Total PDF files found: {results['total_files']}\n\n"
       
        # Count files by category
        id_prefixes = ['02_ID_', '02_IDs_', '02_ID1_', '02_ID2_']
        title_prefixes = ['04_TITLE_', '04_DEED_']
       
        roe_count = len(results['files_by_prefix']['01_ROE_'])
        id_count = sum(len(results['files_by_prefix'][prefix]) for prefix in id_prefixes)
        title_count = sum(len(results['files_by_prefix'][prefix]) for prefix in title_prefixes)
       
        summary += f"Files by Category:\n"
        summary += f"• 01_ROE_ files: {roe_count}\n"
        summary += f"• ID files (02_ID_/IDs_/ID1_/ID2_): {id_count}\n"
        summary += f"• TITLE/DEED files (04_TITLE_/04_DEED_): {title_count}\n"
        summary += f"• Total categorized files: {roe_count + id_count + title_count}\n\n"
       
        # Issues summary
        tt_issues = len(results['files_without_tt'])
        missing_folders = len(results['folders_missing_prefixes'])
       
        summary += f"Issues Found:\n"
        summary += f"• Files missing ROE prefix (TT-BCx) in path: {tt_issues}\n"
        summary += f"• Folders with missing files and/or naming convention errors: {missing_folders}\n\n"
       
        if tt_issues == 0 and missing_folders == 0:
            summary += "✅ All files and folders are compliant!\n"
        else:
            summary += "⚠️ Issues found - check the Issues tab for details.\n"
           
        return summary
       
    def generate_files_info(self, results):
        """generate files found information"""
        info = "files found by prefix\n"
        info += "=" * 50 + "\n\n"
       
        # imperative prefixes
        id_prefixes = ['02_ID_', '02_IDs_', '02_ID1_', '02_ID2_']
        title_prefixes = ['04_TITLE_', '04_DEED_', '04_TITLE-']
        other_prefixes = ['01_ROE_']
       
        # display ROE ct
        for prefix in other_prefixes:
            files = results['files_by_prefix'][prefix]
            count = len(files)
            info += f"{prefix} files: ({count} found)\n"
            if files:
                for file_path in sorted(files):
                    info += f"  • {file_path}\n"
            else:
                info += "  None found\n"
            info += "\n"
       
        # display ct of ID files
        info += "ID files (02_ID_/02_IDs_/02_ID1_/02_ID2_):\n"
        id_total = 0
        for prefix in id_prefixes:
            files = results['files_by_prefix'][prefix]
            count = len(files)
            id_total += count
            if files:
                info += f"  {prefix} files: ({count} found)\n"
                for file_path in sorted(files):
                    info += f"    • {file_path}\n"
       
        if id_total == 0:
            info += "  None found\n"
        else:
            info += f"  Total ID files: {id_total}\n"
        info += "\n"
       
        # display ct of property title's
        info += "TITLE/DEED files (04_TITLE_/04_DEED_):\n"
        title_total = 0
        for prefix in title_prefixes:
            files = results['files_by_prefix'][prefix]
            count = len(files)
            title_total += count
            if files:
                info += f"  {prefix} files: ({count} found)\n"
                for file_path in sorted(files):
                    info += f"    • {file_path}\n"
       
        if title_total == 0:
            info += "  None found\n"
        else:
            info += f"  Total TITLE/DEED files: {title_total}\n"
           
        return info
       
    def generate_issues_info(self, results):
        """Generate issues information"""
        issues = ""
       
        # TT-BC issues
        if results['files_without_tt']:
            issues += "FILES NOT FOLLOWING ROE PATTERN (TT-BCx)\n"
            issues += "=" * 50 + "\n"
            issues += "Expected: ROE Prefix should appear somewhere in the file path\n\n"
           
            for issue in results['files_without_tt']:
                issues += f"❌ {issue['file']}\n"
                issues += f"   Issue: {issue['issue']}\n\n"
           
            issues += f"⚠️ Total files with TT-BC issues: {len(results['files_without_tt'])}\n\n"
       
        # missing prefix issues
        if results['folders_missing_prefixes']:
            issues += "FOLDERS MISSING REQUIRED PREFIXES\n"
            issues += "=" * 50 + "\n"
           
            for folder, missing_prefixes in sorted(results['folders_missing_prefixes'].items()):
                folder_name = Path(folder).name if Path(folder).name else folder
                issues += f"📁 {folder}\n"
                issues += f"   Missing: {', '.join(missing_prefixes)}\n\n"
           
            issues += f"⚠️ Total incomplete folders: {len(results['folders_missing_prefixes'])}\n"
       
        if not results['files_without_tt'] and not results['folders_missing_prefixes']:
            issues = "✅ No issues found! All files and folders are compliant.\n"
           
        return issues
 
 
def main():
    # Create the main window
    root = tk.Tk()
    app = PDFAnalyzerGUI(root)
   
    # Start the GUI
    root.mainloop()
 
if __name__ == "__main__":
    main()