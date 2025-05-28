from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': ['tkinter', 'pathlib', 're', 'threading', 'os'],
    'excludes': []
}

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('prefix_checker.py', base=base, target_name='PDF_Analyzer.exe')
]

setup(
    name='PDF File Analyzer',
    version='1.0',
    description='Analyzes PDF files for required prefixes and naming conventions',
    options={'build_exe': build_options},
    executables=executables
)