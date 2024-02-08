# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Classes to recursively import files of a CoreDSL model."""

import logging
import pathlib

from .parser_gen import CoreDSL2Listener, CoreDSL2Parser, CoreDSL2Visitor
from .utils import make_parser


class Importer(CoreDSL2Listener):
	"""ANTLR listener based importer. Bad on performance, as it traverses
	the entire parse tree when it only has to look for import statements.
	"""

	def __init__(self, search_path) -> None:
		super().__init__()
		self.imported = set()
		self.new_children = []
		self.new_defs = []
		self.got_new = True
		self.search_path = search_path

	def enterImport_file(self, ctx: CoreDSL2Parser.Import_fileContext):
		"""The actual import functionality. Extracts the filename to import,
		constructs a new parser and parses the next file.
		"""

		filename = ctx.RULE_STRING().getText().replace('"', '')
		if filename not in self.imported:
			print(f"importing file {filename}")
			self.got_new = True
			self.imported.add(filename)

			parser = make_parser(self.search_path/filename)

			tree = parser.description_content()

			self.new_children.extend(tree.children)
			self.new_defs.extend(tree.definitions)
		pass

def recursive_import(tree, search_path):
	"""Helper method to recursively process all import statements of a given
	parse tree. The search path should be set to the directory of the root document.
	"""

	path_extender = ImportPathExtender(search_path)
	path_extender.visit(tree)

	importer = VisitImporter(search_path)

	while importer.got_new:
		importer.new_imports.clear()
		importer.new_defs.clear()
		importer.new_children.clear()
		importer.got_new = False

		importer.visit(tree)

		tree.imports = importer.new_imports + tree.imports
		tree.definitions = importer.new_defs + tree.definitions
		tree.children = importer.new_children + [x for x in tree.children if not isinstance(x, CoreDSL2Parser.Import_fileContext)]


class VisitImporter(CoreDSL2Visitor):
	"""Importer class based on an ANTLR Visitor. Only traverses the model tree
	to the import statements and stops traversion after that.
	"""

	def __init__(self, search_path) -> None:
		super().__init__()
		self.imported = set()
		self.new_children = []
		self.new_imports = []
		self.new_defs = []
		self.got_new = True
		self.search_path = search_path
		self.logger = logging.getLogger("visit_importer")

	def visitDescription_content(self, ctx: CoreDSL2Parser.Description_contentContext):
		for i in ctx.imports:
			self.visit(i)

	def visitImport_file(self, ctx: CoreDSL2Parser.Import_fileContext):
		"""The actual import functionality. Extracts the filename to import,
		constructs a new parser and parses the next file.
		"""

		import_name = ctx.uri.text.replace('"', '')
		filename = str(pathlib.Path(import_name).resolve())

		# only import each file once
		if filename not in self.imported:
			self.logger.info("importing file %s", filename)

			# keep track that we imported something
			self.got_new = True
			self.imported.add(filename)

			# extract file path and search path
			file_path = pathlib.Path(filename)
			file_dir = file_path.parent

			parser = make_parser(file_path)

			# run ImportPathExtender on the new tree
			tree = parser.description_content()
			path_extender = ImportPathExtender(file_dir)
			path_extender.visit(tree)

			# keep track of the new children
			self.new_children.extend(tree.children)
			self.new_imports.extend(tree.imports)
			self.new_defs.extend(tree.definitions)


class ImportPathExtender(CoreDSL2Visitor):
	"""ANTLR visitor to resolve relative import paths. Replaces all import URIs
	with their equivalent absolute path, relative to search_path.
	"""

	def __init__(self, search_path: pathlib.Path) -> None:
		super().__init__()
		self.search_path = search_path

	def visitDescription_content(self, ctx: CoreDSL2Parser.Description_contentContext):
		for i in ctx.imports:
			self.visit(i)

	def visitImport_file(self, ctx: CoreDSL2Parser.Import_fileContext):
		filename = self.search_path / ctx.uri.text.replace('"', '')
		ctx.uri.text = str(filename)
