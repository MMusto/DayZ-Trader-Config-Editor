from cx_Freeze import setup, Executable

base = None    

executables = [Executable("trader_editor.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Smurf Team Six's Trader Editor",
    options = options,
    version = "1.0",
    description = 'Create and maintain realiable trader data with ease.',
    executables = executables
)