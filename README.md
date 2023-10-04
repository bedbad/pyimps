Give a python source to the script and get detailed imports tree in terminal immideately:

A complicated project like torch will give somthing like this
```
python3 pyimports.py torch                                                       
```
![Screenshot](Screenshot.png)

Each dependency colored differently depending on whether it exists, depending on it's type

I wanted get all import dependencies for a bunch of python files and to my surprize I found no
simple tool in Python that could it, pydeps is too hefty and more importantly is not a shell utility.

Pyimports shows the dependency trees of a python source and tells which imports are modules, members, etc or if they are not found.
