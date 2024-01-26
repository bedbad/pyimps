import sys
from pathlib import Path
import os
import argparse

import ast
import json

import requests

from collections import deque

import importlib.util
import inspect

import pkgutil

from typing import TypeVar, Generic, List, Type, Dict

class bcs:
    TEAL = '\033[96m'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

T = TypeVar('T')
class Node(Generic[T]):
    def __init__(self, value_type : Type[T], parent=None):
        self.parent = parent
        self.children = set()
        self.value = value_type()
    def add_child(self, child)->None:
        child.set_parent = self
        self.children.add(child)
    def add_child_x(self, child)->bool:
        if child not in self.children:
            self.add_child(child)
            return True
        return False
    def add_children(self, children : list)->None:
        for child in children:
            self.add_child(child)
    def remove_child(self, child)->bool:
        if child in self.children:
            child.set_parent(None)
            self.children.remove(child)
            return True
        return False
    def set_parent(self, parent):
        self.parent = parent
    def sever(self):
        self.set_parent(None)
    def set_value(self, value):
        self.value = value
    def outstr(self, indent = 0):
        outstr = ''
        if indent:
            outstr += '\n' +(' '*indent) + '↑___'
        elif not self.parent:
            outstr += '*'
        outstr += str(self.value)
        for child in self.children:
            outstr += child.outstr(indent+len(str(self.value)))
        return outstr
    def print(self):
        print(self.outstr())

    def get_root(self):
        back = self
        while back.parent is not None:
            back = back.parent
        return back
        
    def get_leafs(self):
        stack = [self]
        leafs = list()
        while stack:
            node = stack.pop()
            if node.children:
                stack.extend(node.children)
            else:
                leafs.append(node)
        return leafs
    
    def get_flat(self):
        stack = [self]
        flat = list()
        while stack:
            node = stack.pop()
            if node.children:
                stack.extend(node.children)
            flat.append(node)
        return flat

    
def node_pathname(node: Node)->str:
    outstr = str(node.value)
    back = node.parent
    while back:
        outstr = str(back.value) + '.' + outstr
        back = back.parent
    return outstr

def modtree_render(root: Node[str], final:dict, indent=0)->None:
    outstr = ''
    if indent:
        outstr += '\n' +(' '*indent) + '↑___'
    name = node_pathname(root)
    color = bcs.ENDC
    if(final[name] == 'root'):
        outstr += bcs.YELLOW + str(root.value) + bcs.ENDC + '<====' + str(sys.modules[name].__spec__.origin)
    elif(final[name] == 'submodule'):
        outstr += bcs.GREEN + str(root.value) + bcs.ENDC + '<====' + str(sys.modules[name].__spec__.origin) 
    elif(final[name] == 'irregular_module'):
        outstr += bcs.PINK + str(root.value) + bcs.ENDC #
    elif(final[name] == 'deleted_module'):
        outstr += bcs.PINK + str(root.value) + '(deleted)' + bcs.ENDC #
    elif(final[name] == 'ALL'):
        realname = name[:-2]
        if(hasattr(sys.modules[realname], '__all__')):
            outstr +=   '('+bcs.GRAY+','.join([str(item) for item in sys.modules[realname].__all__]) +bcs.ENDC+')' #
        else:
            mod  = sys.modules[realname]
            members = inspect.getmembers(mod, lambda m: inspect.isclass(m) or inspect.isfunction(m) or inspect.ismodule(m))
            path= mod.__file__
            outstr +=   '('+bcs.GRAY+','.join([str(member[0]) for member in members]) +bcs.ENDC+')' #
    elif final[name]=='class':
        outstr += bcs.BLUE + str(root.value) +bcs.ENDC
    elif final[name]=='variable':
        outstr += bcs.GRAY + str(root.value) +bcs.ENDC
    elif final[name]=='function':
        outstr += bcs.TEAL + str(root.value) +bcs.ENDC
    elif final[name]=='absent':
        outstr += bcs.RED + str(root.value) +bcs.ENDC 
    for child in root.children:
        outstr += modtree_render(child, final, indent+len(str(root.value)))
    return outstr
 
#transform a proper tree in a dict form into a tree form
def dict2trees(dic : dict, back : Node[T] = None) -> List[Node[T]]:
    rootvals = dic.keys()
    reses = list()
    for rootval in rootvals:
        res = Node[T](str, parent = None)
        res.set_value(rootval)
        if back is not None:
            res.set_parent(back)
        res.add_children(dict2trees(dic[rootval], res))
        reses.append(res)
    return reses

def path2package_name(path)->str:
        start_dir = Path(path).parent
        while start_dir.joinpath('__init__.py').exists():
            start_dir = start_dir.parent
        relpath = Path(path).parent.relative_to(start_dir)
        pacname = '.'.join(relpath.parts)
        return pacname

def get_import_trees(path):
    if Path(path).name == '__init__.py':
        return get_imports(path, pacname=path2package_name(path))
    else:
        return get_imports(path, pacname = None)

def name2chain(name, separator = '.')->(Dict, Dict):
    chain = dict()
    rez = chain
    namelist = name.split(separator)
    for i in range(0, len(namelist) - 1):
        chain[namelist[i]] = dict()
        chain = chain[namelist[i]]
    chain[namelist[-1]] = dict()
    return rez

def merge_tdics(map1 : dict, map2 : dict)->dict:
    xset = set.intersection(set(map1.keys()), set(map2.keys()))
    dset1 = set(map1.keys()) -  set(map2.keys())
    dset2 = set(map2.keys()) - set(map1.keys())
    rez = dict()
    for k in dset1:
        rez[k] = map1[k]
    for k in dset2:
        rez[k] = map2[k]
    for k in xset:
        rez[k] = merge_tdics(map1[k], map2[k])
    return rez


def get_imports(path, pacname = None):
    imports = dict()
    if pacname is not None:
        imports[pacname] = dict()
    with open(path) as fh:
        root = ast.parse(fh.read(), path)
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                temp = dict()
                for n in node.names:
                    temp = merge_tdics(temp,name2chain(n.name))
                imports = merge_tdics(imports, temp)
            elif isinstance(node, ast.ImportFrom):
                if node.module is None or node.level == 1:
                    #relative imports from . ..
                    if node.level > 1:
                        #We don't support relative imports of higher levels
                        raise Exception("relative import from parent folder or higher is ugly")
                    assert pacname is not None
                    temp = dict()
                    if node.module is not None:
                        temp = dict()
                        for n in node.names:
                            temp = merge_tdics(temp,name2chain(n.name))
                        chain = dict()
                        rez = chain
                        namelist = node.module.split('.')
                        for i in range(0, len(namelist)-1):
                            chain[namelist[i]] = dict()
                            chain = chain[namelist[i]]
                        chain[namelist[-1]] = temp
                        imports[pacname] = merge_tdics(imports[pacname],rez)
                    else:
                        temp = dict()
                        for n in node.names:
                            temp = merge_tdics(temp,name2chain(n.name))
                        imports[pacname] = merge_tdics(imports[pacname],temp)
                else:
                    temp = dict()
                    for n in node.names:
                        temp = merge_tdics(temp,name2chain(n.name))
                    chain = dict()
                    rez = chain
                    namelist = node.module.split('.')
                    for i in range(0, len(namelist)-1):
                        chain[namelist[i]] = dict()
                        chain = chain[namelist[i]]
                    chain[namelist[-1]] = temp
                    imports = merge_tdics(imports,rez)
            else:
                continue
    return imports

def traverse(tr : dict)->deque:
    stack = list(tr.items())
    res = deque()
    while stack:
        e =  stack.pop()
        print(e)
        res.append(e[0])
        if e[1]:
            stack.extend(list(e[1].items()))
    return res

def traverse(root : Node)->deque:
    stack = [root]
    res = deque()
    while stack:
        e = stack.pop()
        res.append(e)
        stack.extend(e.children)
    return res
        
def tr2importtr(tree : Node)->None:
    final = dict()
    # l = tree.get_flat()
    #print(l)
    deq = traverse(tree)
    while deq:
        n = deq.popleft()
        module_name = node_pathname(n)
        try:
            if n.parent is not None:
                parname = node_pathname(n.parent)
                importlib.import_module(parname)
                if parname in sys.modules:
                    parmod = sys.modules[parname]
                    member_modules = dict(inspect.getmembers(parmod, inspect.ismodule))
                    member_classes = dict(inspect.getmembers(parmod, inspect.isclass))
                    member_functions = dict(inspect.getmembers(parmod, inspect.isfunction))
                    if n.value in member_modules.keys():
                        mod = member_modules[n.value]
                        if mod.__spec__ is not None:
                            importlib.import_module(mod.__name__, parmod)
                            final[node_pathname(n)] = 'submodule'
                        else:
                            final[node_pathname(n)] = 'irregular_module'
                    elif n.value in member_classes.keys():
                        final[node_pathname(n)] = 'class'
                    elif n.value in member_functions.keys():
                        final[node_pathname(n)] = 'function'
                    elif n.value in dir(parmod):
                        final[node_pathname(n)] = 'variable'
                    else:
                        if module_name.endswith('.*'):
                            final[node_pathname(n)] = 'ALL'
                        else:
                            importlib.import_module(module_name)
                            final[node_pathname(n)] = 'deleted_module'
            else:
                importlib.import_module(module_name)
                final[module_name] = 'root'
        except Exception as e:
                    print(e)
                    print('sys path:', sys.path)
                    final[module_name] = 'absent'
                    # print("module error "+str(e))
    return (tree, final)


def exec_search(modsstr : str):
    api_url = "https://pypi.org/search/"
    page_size = 2
    sort_by = "name"
    date_format = "%d-%-m-%Y"
    link_defualt_format = "https://pypi.org/project/{package.name}"

    s = requests.Session()
    for page in range(3):
        params = {"q": modsstr, "page": page}
        r = s.get(api_url, params=params)
        print(r.text)

    return r.text


def main():
    parser = argparse.ArgumentParser(description = 'Pyimports shows dependency tree of python source files and modules')
    parser.add_argument('-s', '--search', required=False, help='search for specified module on registry', action='store_true', default=False)
    parser.add_argument('py_src', type=str, help = 'python source file to analyze')
    args = parser.parse_args()
    if args.search:
        exec_search(args.py_src.split('.')[0])
    if args.py_src.endswith('.py'):
        src = args.py_src
    else:
        #we got a module
        try:
            mod2inspect = importlib.import_module(args.py_src)
            src = mod2inspect.__file__
            print('Module path: ' + src) 
        except Exception as e:
            print(args.py_src + ' is not found in importable modules')
            print(e)
            sys.exit(1)
        
            
    imports = get_import_trees(src)
    trees = dict2trees(imports)
    for tree in trees:
        tree, final = tr2importtr(tree)
 
        print(modtree_render(tree, final))


if __name__ == '__main__':
   main()
