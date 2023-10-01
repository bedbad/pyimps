import sys
from pathlib import Path
import argparse

import ast
import json

from collections import deque

import importlib.util
import inspect

from typing import TypeVar, Generic, List, Type, Dict

class bcs:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
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
        outstr += bcs.WARNING + str(root.value) + bcs.ENDC + '<====' + str(sys.modules[name].__spec__.origin)
    elif(final[name] == 'submodule'):
        outstr += bcs.GREEN + str(root.value) + bcs.ENDC + '<====' + str(sys.modules[name].__spec__.origin) 
    elif final[name]=='member':
        outstr += bcs.BLUE + str(root.value) +bcs.ENDC
    elif final[name]=='absent':
        outstr += bcs.FAIL + str(root.value) +bcs.ENDC 
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

def get_import_trees(path):
    if Path(path).name == '__init__.py':
        pacname = Path(path).parent.name
        return get_imports(path, pacname = pacname)
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
                    temp = temp | name2chain(n.name)
                imports = imports | temp
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
                            temp = temp | name2chain(n.name)
                        chain = dict()
                        rez = chain
                        namelist = node.module.split('.')
                        for i in range(0, len(namelist)-1):
                            chain[namelist[i]] = dict()
                            chain = chain[namelist[i]]
                        chain[namelist[-1]] = temp
                        imports[pacname] = imports[pacname] | rez
                    else:
                        temp = dict()
                        for n in node.names:
                            temp = temp | name2chain(n.name)
                        imports[pacname] = imports[pacname] | temp
                else:
                    temp = dict()
                    for n in node.names:
                        temp = temp | name2chain(n.name)
                    chain = dict()
                    namelist = node.module.split('.')
                    for i in range(0, len(namelist)):
                        chain[namelist[i]] = dict()
                        chain = chain[namelist[i]]
                    chain[namelist[-1]] = temp
                    imports = imports | chain
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
                    members = dict(inspect.getmembers(parmod, inspect.ismodule))
                    if n.value in members.keys():
                        final[node_pathname(n)] = 'submodule'
                    elif hasattr(parmod, '__all__') and n.value in parmod.__all__:
                        final[node_pathname(n)] = 'member'
                    else:
                        final[node_pathname(n)] = 'absent'
            else:
                importlib.import_module(module_name)
                final[module_name] = 'root'
        except Exception as e:
                    print(e)
                    print('sys path:', sys.path)
                    final[module_name] = 'absent'
                    # print("module error "+str(e))
    return (tree, final)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Pyimports shows dependency tree of python source files and modules')
    parser.add_argument('py_src', type=str, help = 'python source file to analyze')
    args = parser.parse_args()
    if args.py_src.endswith('.py'):
        src = args.py_src
    else:
        #we got a module
        try:
            mod2inspect = importlib.import_module(args.py_src)
            src = mod2inspect.__file__
            print('Full path: ' + src) 
        except Exception as e:
            print(args.py_src + ' is not found in importable modules')
            print(e)
            sys.exit(1)
        
            
    imports = get_import_trees(src)
    trees = dict2trees(imports)
    for tree in trees:
        tree, final = tr2importtr(tree)
 
        print(modtree_render(tree, final))
    # final = dict()
    # # l = tree.get_flat()
    # #print(l)
    # deq = traverse(tree)
    # while deq:
    #     n = deq.popleft()
    #     module_name = node_pathname(n)
    #     try:
    #         if n.parent is not None:
    #             importlib.import_module(node_pathname(n))
    #             parname = node_pathname(n.parent)
    #             if parname in sys.modules:
    #                 parmod = sys.modules[parname]
    #                 members = dict(inspect.getmembers(parmod, inspect.ismodule))
    #                 if n.value in members.keys():
    #                     final[node_pathname(n)] = 'submodule'
    #                 elif n.value in parmod.__all__:
    #                     final[node_pathname(n)] = 'member'
    #         else:
    #             importlib.import_module(module_name)
    #             final[module_name] = 'root'
    #     except Exception as e:
    #                 final[module_name] = 'absent'
    #                 # print("module error "+str(e))
