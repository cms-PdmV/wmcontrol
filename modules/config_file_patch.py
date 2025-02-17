"""This module parses syntactically an auto-generated configuration file."""

import sys

if sys.version_info < (3, 9):
    raise RuntimeError("This module requires Python 3.9 or higher!")

import ast
from pathlib import Path


class SourceTypeFinder(ast.NodeVisitor):
    """Check for the `cms.Source` type in the configuration file."""

    def __init__(self):
        self.source_type = None

    def visit_Assign(self, node):
        """Check the type provided via `cms.Source`."""
        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                if target.value.id == "process" and target.attr == "source":
                    # Found the assignment: process.source
                    if (
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and node.value.func.value.id == "cms"
                        and node.value.func.attr == "Source"
                        and len(node.value.args) == 1
                    ):
                        source_type = node.value.args[0]
                        if isinstance(source_type, ast.Constant):
                            self.source_type = source_type.value


class ProcessSourceFilter(ast.NodeTransformer):
    """Check for file names under the `process.source` assignment and filter them."""

    def __init__(self, max_files):
        self.max_files = max_files
        self._found = False

    def visit_Assign(self, node):
        if self._found:
            return node

        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                if target.value.id == "process" and target.attr == "source":
                    # Found the assignment: process.source
                    if (
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and node.value.func.value.id == "cms"
                        and node.value.func.attr == "Source"
                    ):
                        # Filter file names
                        for kw in node.value.keywords:
                            if (
                                kw.arg == "fileNames"
                                and isinstance(kw.value, ast.Call)
                                and isinstance(kw.value.func, ast.Attribute)
                                and isinstance(kw.value.func.value, ast.Attribute)
                                and kw.value.func.value.value.id == "cms"
                                and kw.value.func.value.attr == "untracked"
                                and kw.value.func.attr == "vstring"
                            ):
                                for iar in kw.value.args:
                                    if isinstance(iar, ast.Tuple):
                                        iar.elts = iar.elts[: self.max_files]
                                        self._found = True
                                        return node
        return node


class ProcessMixInputFilter(ast.NodeTransformer):
    """Check for file names under the `process.mix.input` assignment and filter them."""

    def __init__(self, max_files):
        self.max_files = max_files
        self._found = False

    def visit_Assign(self, node):
        if self._found:
            return node

        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Attribute)
                and target.attr == "fileNames"
                and target.value.attr == "input"
            ):
                if (
                    isinstance(target.value.value, ast.Attribute)
                    and target.value.value.attr == "mix"
                ):
                    if (
                        isinstance(target.value.value.value, ast.Name)
                        and target.value.value.value.id == "process"
                    ):
                        # Found the assignment: process.mix.input.fileNames
                        if isinstance(node.value, ast.Call):
                            if (
                                isinstance(node.value.func, ast.Attribute)
                                and isinstance(node.value.func.value, ast.Attribute)
                                and isinstance(node.value.func.value.value, ast.Name)
                                and node.value.func.attr == "vstring"
                                and node.value.func.value.attr == "untracked"
                                and node.value.func.value.value.id == "cms"
                            ):
                                # Filter file names
                                for arg in node.value.args:
                                    if isinstance(arg, ast.List):
                                        arg.elts = arg.elts[: self.max_files]
                                        self._found = True
                                        return node
        return node


class ProcessMixDataInputFilter(ast.NodeTransformer):
    """Check for file names under the `process.mixData.input` assignment and filter them."""

    def __init__(self, max_files):
        self.max_files = max_files
        self._found = False

    def visit_Assign(self, node):
        if self._found:
            return node

        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Attribute)
                and target.attr == "fileNames"
                and target.value.attr == "input"
            ):
                if (
                    isinstance(target.value.value, ast.Attribute)
                    and target.value.value.attr == "mixData"
                ):
                    if (
                        isinstance(target.value.value.value, ast.Name)
                        and target.value.value.value.id == "process"
                    ):
                        # Found the assignment: process.mixData.input.fileNames
                        if isinstance(node.value, ast.Call):
                            if (
                                isinstance(node.value.func, ast.Attribute)
                                and isinstance(node.value.func.value, ast.Attribute)
                                and isinstance(node.value.func.value.value, ast.Name)
                                and node.value.func.attr == "vstring"
                                and node.value.func.value.attr == "untracked"
                                and node.value.func.value.value.id == "cms"
                            ):
                                # Filter file names
                                for arg in node.value.args:
                                    if isinstance(arg, ast.List):
                                        arg.elts = arg.elts[: self.max_files]
                                        self._found = True
                                        return node
        return node


class FilterFilesFromConfigFile:
    """Filter the list of source files from several attributes in the configuration file."""

    _keep_files_if_source = ["LHESource"]

    def __init__(self, max_files_to_keep=5):
        self._max_files_to_keep = max_files_to_keep

    def _raises_syntax_errors(self, tree):
        """Check if a source code tree would raise SyntaxError."""
        try:
            compile(tree, filename="<ast-check>", mode="exec")
            return False
        except SyntaxError:
            return True

    def _filter_files_from_configuration_file(self, source_code):
        """
        Filter a list of file names for an autogenerated cms-sw configuration file.

        Args:
            source_code (str): `cms-sw` configuration file source code.

        Returns:
            str | None: Modified source code.
        """
        source_tree = ast.parse(source_code)
        if self._raises_syntax_errors(source_tree):
            print("FilterFilesFromConfigFile: Configuration file has syntax errors...")
            return None

        # Check if files should be modified
        source_type_visitor = SourceTypeFinder()
        source_type_visitor.visit(source_tree)
        source_type = source_type_visitor.source_type
        if not source_type:
            print("FilterFilesFromConfigFile: Unable to find source type")
            return None

        if source_type in self._keep_files_if_source:
            print("FilterFilesFromConfigFile: Files must be kept for source type: ", source_type)
            return None

        # Filter the file names from the desired attributes:

        # process.source.fileNames
        process_source_visitor = ProcessSourceFilter(max_files=self._max_files_to_keep)
        process_source_filtered = process_source_visitor.visit(source_tree)
        if not process_source_visitor._found:
            print("FilterFilesFromConfigFile: Unable to filter files for `process.source.fileNames`, skipping...")

        # process.mix.input.fileNames
        process_mix_visitor = ProcessMixInputFilter(max_files=self._max_files_to_keep)
        process_mix_filtered = process_mix_visitor.visit(process_source_filtered)
        if not process_mix_visitor._found:
            print("FilterFilesFromConfigFile: Unable to filter files for `process.mix.input.fileName`, skipping...")

        process_mix_data_visitor = ProcessMixDataInputFilter(max_files=self._max_files_to_keep)
        process_mix_data_filtered = process_mix_data_visitor.visit(process_mix_filtered)
        if not process_mix_data_visitor._found:
            print("FilterFilesFromConfigFile: Unable to filter files for `process.mixData.input.fileName`, skipping...")

        # Check there's no SyntaxError
        result_tree = process_mix_data_filtered
        if self._raises_syntax_errors(result_tree):
            print("FilterFilesFromConfigFile: Modified configuration file has syntax errors...")
            return None
        
        return ast.unparse(result_tree)

    def _prepare_metadata_header(self, source_code):
        """
        Pick the first comments in a configuration file and append
        more metadata.

        Args:
            source_code (str): `cms-sw` configuration file source code.

        Returns:
            str: New metadata header.
        """
        header = []
        for line in source_code.splitlines(keepends=True):
            if line.startswith("#"):
                header.append(line)
            else:
                break

        # Ensure the header ends with a newline
        if header and not header[-1].endswith("\n"):
            header[-1] += "\n"

        header += [
            "#\n",
            "# This file has been preprocessed by wmcontrol to filter file names\n",
            "#\n"
        ]

        return "".join(header)

    def patch(self, cfg_path):
        """
        Patch a configuration file filtering its source files and save
        the result in a new source file.

        Args:
            cfg_path (str): `cms-sw` configuration file path.

        Returns:
            str | None: Patched configuration file path.
        """
        as_path = Path(cfg_path)
        with open(as_path, "r") as file:
            source_code = file.read()

        modified_source_code = self._filter_files_from_configuration_file(source_code=str(source_code))
        if not modified_source_code:
            return None

        # Parse the metadata
        headers = self._prepare_metadata_header(source_code=str(source_code))
        result = headers + modified_source_code
        if self._raises_syntax_errors(result):
            print("FilterFilesFromConfigFile: Modified configuration file with headers has syntax errors...")
            return None

        new_source_path = (
            as_path.with_name(as_path.stem + "-wmupload")
            .with_suffix(".py")
        )
        with open(new_source_path, "w") as file:
            file.write(result)

        return str(new_source_path.absolute())


# Quick example usage
if __name__ == "__main__":
    # Download BPH-GenericGSmearS-00010_1_cfg.py from:
    # https://cmsweb.cern.ch/couchdb/reqmgr_config_cache/8586532bbcd76d7ddac8b4ebdf4dddb5/configFile
    example_file = "BPH-GenericGSmearS-00010_1_cfg.py"
    patcher = FilterFilesFromConfigFile(max_files_to_keep=5)
    new_file = patcher.patch(example_file)
    print("Patched configuration file is available at: ", new_file)
