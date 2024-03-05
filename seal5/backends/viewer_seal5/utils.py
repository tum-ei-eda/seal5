# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Utility stuff for M2-ISA-R viewer"""

from typing import TYPE_CHECKING
from anytree import Node

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import ttk


class TreeGenContext:
    def __init__(self, parent=None) -> None:
        if parent:
            self.nodes = [parent]
        else:
            self.nodes = [Node("Tree")]
        self.parent_stack = [0]
        # self.layer = 0

    @property
    def parent(self):
        return self.nodes[self.parent_stack[-1]]

    @property
    def tree(self):
        return self.nodes[0]

    def push(self, node):
        # self.layer += 1
        self.parent_stack.append(len(self.nodes))
        self.nodes.append(node)

    def pop(self):
        # self.layer -= 1
        return self.parent_stack.pop()

    def insert(self, text, values=None):
        self.push(self.insert2(text, values=values))

    def insert2(self, text, values=None):
        raise NotImplementedError


class TkTreeGenContext(TreeGenContext):
    def __init__(self, tree: "ttk.Treeview", parent=None) -> None:
        super().__init__(parent=parent)
        self.tree = tree

    def insert2(self, text, values=None):
        return self.tree.insert(self.parent, tk.END, text=text, values=values)


class TextTreeGenContext(TreeGenContext):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

    def insert2(self, text, values=None):
        if isinstance(values, (list, set, tuple)):
            if len(values) == 1:
                values = values[0]
        return Node(text, parent=self.parent, value=values)
