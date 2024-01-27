# Unconfuse your Py imports
Pyimps shows you fully, exactly and immediately what you're importing.

If any dependency may present an issue(reloaded module, frozen, or module defined in code from ModuleType() for example) or not found you would see it. Each dependency colored differently so that you see if importing another module or just class, function or const variable. This saves debugging errors or helps making them hermetic especially when bundling, freezing them into applications.

## Installation

```
pip install pyimps
```

## Usage
Use it on a) source.py file b) any module name (main.suba.subb) in sys.path and current path

A complex project like tensorflow will give something like this
```
pyimps tensorflow                                                  
```
![Screenshot](resources/Screenshot.png)



I wanted to check and control dependencies for large python codebase to bundled into an application and to my surprize I found no
simple tool in Python that could it, pydeps is too hefty and more importantly is not a shell utility and lacks some functionality.
