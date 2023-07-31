How it works:
point script on a python file and see information of their imports in terminal:

    python3 pyimports /path/to/file/to_analyze.py

That wil achieve the following effect:


Once upon a time I wanted get all import dependencies for a bunch of python files and to my surprize I found no
simple tool in Python that could it, pydeps is too hefty and complx and more importantly doesn't output in terminal
This tool shows the dependency trees of a python source and tells which imports are modules, members, etc or if they are not found.
The idea is you know better which minimal set of dependencies you need and fill in the gaps morequickly or get read of annoying dependencies that
contribute too little and loan too much technical dept. 
