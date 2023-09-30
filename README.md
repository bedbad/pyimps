Give a python source to the script and get detailed imports tree in terminal immideately:
'''
python3 pyimports.py /opt/homebrew/lib/python3.11/site-packages/numpy/__init__.py
sys<====built-in
warnings<====/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11/warnings.py
_globals
        ↑____CopyMode
        ↑____NoValue
exceptions
          ↑___ModuleDeprecationWarning
          ↑___TooHardError
          ↑___ComplexWarning
          ↑___VisibleDeprecationWarning
          ↑___AxisError
version
       ↑___git_revision
       ↑_____version__
'''
Each dependency colored differently depending on whether it exists, is a package and is a final transitive dependency(leaf)

I wanted get all import dependencies for a bunch of python files and to my surprize I found no
simple tool in Python that could it, pydeps is too hefty and more importantly is not a shell utility.

Pyimports shows the dependency trees of a python source and tells which imports are modules, members, etc or if they are not found.
