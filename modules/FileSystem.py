#!/usr/bin/env python3

# FileSystem.py - A file system implemented as a tree of nodes.
# Examples:
#       FileTree()                                                   -> A new empty file system.
#       FileTreeNode('file1', '/path/to/file1')                      -> Create a new file node.
#       FileTree().add_node(FileTreeNode('file2', '/path/to/file2')) -> Add a file to the tree.
#       FileTree().traverse()                                        -> Iterate over all nodes in the tree. 

class FileTreeNode:
    """
    A tree node representing a file.
    """
    def __init__(self, name: str, path: str, parent=None):
        """
        Initialize a new FileTreeNode instance.

        Args:
            name (str): The name of the file.
            path (str): The path to the file.
            parent (FileTreeNode, optional): The parent node. Defaults to None.
        """
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []

    def add_child(self, child: 'FileTreeNode'):
        """
        Add a child node to this node.

        Args:
            child (FileTreeNode): The child node to be added.

        Returns:
            FileTreeNode: The newly added child node.
        """
        self.children.append(child)

    def __repr__(self):
        """
        Return a string representation of this object.

        Returns:
            str: A string representing this FileTreeNode instance.
        """
        return f"FileTreeNode('{self.name}', '{self.path}')"

    def __str__(self):
        """
        Return a string representation of this object.

        Returns:
            str: A string representing this FileTreeNode instance.
        """
        return f"{self.path}"


class FileTree:
    """
    A file tree data structure, represented as a hierarchical tree.
    """

    def __init__(self):
        """
        Initialize a new FileTree instance.
        """
        self.root = None

    def add_node(self, node: 'FileTreeNode'):
        """
        Add a node to the tree.

        Args:
            node (FileTreeNode): The node to be added.

        Returns:
            FileTreeNode: The newly added node.
        """
        if not self.root:
            self.root = node
        else:
            current = self.root
            while True:
                try:
                    if child := current.add_child(node):
                        return child
                    if current == node.parent:
                        break
                    current = current.parent
                except Exception as e:
                    print(e)
                    break

    def traverse(self) -> iter:
        """
        Traverse the tree, yielding each node in order.

        Yields:
            FileTreeNode: Each node in the file tree.
        """
        def recursive_traversal(node: 'FileTreeNode') -> iter:
            yield node
            for child in node.children:
                yield from recursive_traversal(child)

        yield from recursive_traversal(self.root)


def create_file_tree(directory_object, file_tree):
    """
    Create a FileTree instance by traversing the given directory object \
    and adding all files and directories to the tree.

    Args:
        directory_object: The directory object to traverse.
        file_tree: The FileTree instance to populate.

    Returns:
        FileTree: The populated FileTree instance.
    """
    for directory in directory_object.directories:
        dir_node = FileTreeNode(os.path.basename(directory), directory)
        file_tree.add_node(dir_node)
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_name, ext = os.path.splitext(file)
                if not ext: # ignore directories with no extension (like .git)
                    continue
                file_node = FileTreeNode(os.path.basename(root) + '/' + file_name, 
                                        os.path.join(root, file), parent=dir_node)
                try:
                    dir_node.add_child(file_node)
                except Exception as e:
                    print(e)
                    pass
    return file_tree