from NodeData import *
from test import *
def main():
    filepath="nodes/Node01.txt"

    nodo=NodeData()
    nodo.parse_file(filepath)
    nodo.tostring()

if __name__ == "__main__":
    main()