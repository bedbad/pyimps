import sys
import ast
import json

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

if __name__ == '__main__':
    imports = get_imports(sys.argv[1])
    print(json.dumps(imports, indent=4), '\n')
    
    
                
