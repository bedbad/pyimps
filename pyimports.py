import sys
import ast
import json

from collections import deque

import importlib.util
import inspect

from typing import TypeVar, Generic, List, Type

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

def tree_outstr(root: Node[str], final:dict, indent=0)->None:
    outstr = ''
    if indent:
        outstr += '\n' +(' '*indent) + '↑___'
    name = node_pathname(root)
    color = bcs.ENDC
    if final[name] == 'member':
        color = bcs.BLUE
    elif final[name] == 'submodule':
        color = bcs.GREEN
    elif final[name] == 'root':
        color = bcs.UNDERLINE
    if(name in sys.modules):
        outstr += color + str(root.value) + ' from ' + str(sys.modules[name].__spec__.origin) + bcs.ENDC
    elif final[name]=='member':
        outstr += color + str(root.value) +bcs.ENDC +'\n'
    else:
        pass
    for child in root.children:
        outstr += tree_outstr(child, final, indent+len(str(root.value)))
    return outstr
 

def dict2trees(dic : dict, back : Node[T] = None) -> List[Node[T]]:
    rootvals = dic.keys()
    reses = list()
    for rootval in rootvals:
        res = Node[T](str, parent = None)
        res.set_value(rootval)
        if back is not None:
            res.set_parent(back)
        if dic[rootval]:
            res.add_children(dict2trees(dic[rootval], res))
        reses.append(res)
    return reses
        

def get_imports(path):
    imports = dict()
    with open(path) as fh:
        root = ast.parse(fh.read(), path)
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                temp = imports
                for n in node.names:
                    namelist = n.name.split('.')
                    if len(namelist) > 1:
                        for st in namelist:
                            temp[st] = dict()
                            temp = temp[st]
                    else:
                        temp[n.name] = dict()
            elif isinstance(node, ast.ImportFrom):
                temp = imports
                namelist = node.module.split('.')
                for n in namelist:
                    temp[n] = dict()
                    temp = temp[n]
                for n in node.names:
                    temp[n.name] = dict()
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
        

if __name__ == '__main__':
    imports = get_imports(sys.argv[1])

    trees = dict2trees(imports)

    # for tree in trees:
    #     tree.print()
    

    for tree in trees:
        final = dict()
        l = tree.get_flat()
        #print(l)
        for n in l:
            module_name = node_pathname(n)
            if n.parent is not None:
                parname = node_pathname(n.parent)
                if sys.modules[parname]:
                    parmod = sys.modules[parname]
                    members = dict(inspect.getmembers(parmod, inspect.ismodule))
                    if n.value in members.keys():
                        final[node_pathname(n)] = 'submodule'
                        importlib.import_module(node_pathname(n))
                    elif n.value in parmod.__all__:
                        final[node_pathname(n)] = 'member'
            else:
                try:
                    importlib.import_module(module_name)
                    final[module_name] = 'root'
                except Exception as e:
                    print("module error "+str(e))
        print(tree_outstr(tree, final))
            # if(final[module_name] is not None):
            #     if final[module_name] == 'root':
            #         print("*"+module_name)
            #     elif final[module_name] == 'member':
            #         print("+"+module_name)
            #     elif final[module_name] == 'submodule':
            #         print("--"+module_name)
