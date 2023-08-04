How it works:
point script on a python file and see information of their imports in terminal:

    python3 pyimports /path/to/file/to_analyze.py

That can achieve the following effect:
![Screenshot](Screenshot.png)

I wanted get all import dependencies for a bunch of python files and to my surprize I found no
simple tool in Python that could it, pydeps is too hefty and complx and more importantly doesn't output in terminal
This tool shows the dependency trees of a python source and tells which imports are modules, members, etc or if they are not found.
