import sys
import ast
import json

from collections import deque
import importlib.util
from typing import TypeVar, Generic, List, Type


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
        if child in self.children:
            self.add_child(child)
            return True
        return False
    def add_children(self, children : list)->None:
        for child in children:
            self.add_child(child)
    def remove_child(self, child)->bool:
        if child in self.children:
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
                        for n in namelist:
                            temp[n] = dict()
                            temp = temp[n]
                    else:
                        temp[n.name] = dict()
            elif isinstance(node, ast.ImportFrom):
                namelist = node.module.split('.')
                temp = imports
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
    #print(json.dumps(imports, indent=4), '\n')
    #for module in traverse(imports):
    #    print('Module {} is found:{}'.format(module, (importlib.util.find_spec(module) is not None)))
    trees = dict2trees(imports)
    for tree in trees:
        tree.print()

    print('--Flats---')
    for tree in trees:
        l = tree.get_flat()
        #print(l)
        for n in l:
            module_name = node_pathname(n)
            print(module_name)
            try:
                print("Module found:", importlib.util.find_spec(n.value, n.get_root()))
            except Exception as e:
                print("module not found error "+str(e))
                
    print("---Leafs---")
    for tree in trees:
        for leaf in tree.get_leafs():
            print("Leaf name: "+leaf.outstr())
            module_name = node_pathname(leaf)
            print(str(leaf.value), module_name)
        
