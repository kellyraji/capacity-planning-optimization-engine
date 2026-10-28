from pathlib import Path
import sys
print('Python:', sys.version)
print('Executable:', sys.executable)
for mod in ['duckdb','pyarrow','pandas','numpy','pulp']:
    try:
        m=__import__(mod)
        print(f'{mod}:', getattr(m,'__version__','installed'))
    except Exception as e:
        print(f'{mod}: MISSING ({e})')
root=Path(__file__).resolve().parents[1]
print('Project root:', root)
print('Disk space is not checked by this script; verify free disk before downloading the pod archive.')
