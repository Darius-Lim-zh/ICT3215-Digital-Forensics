# To Use
Install the dependencies:
```commandline
pip install -r requirements.txt
```
### Running
navigate to page
```commandline
python ObfusQrypt.py
```

# Additional
Install Pyinstaller if you want to compile it into an `exe`:
```commandline
pip install pyinstaller
```

To Build the app into an `exe`, use the following command:
```commandline
pyinstaller --onefile --paths=venv/Lib/site-packages --hidden-import customtkinter --hidden-import qiskit --collect-all customtkinter --collect-all qiskit --add-data "assets/ObfusQrypt
.ico:assets" --add-data "venv/Lib/site-packages/qiskit_aer/VERSION.txt:qiskit_aer" --noconsole --icon=assets/ObfusQrypt.ico ObfusQrypt.py
```

The executable is in the `dist` folder
