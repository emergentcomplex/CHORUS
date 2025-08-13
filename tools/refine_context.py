import sys
import ast
import tokenize
import io

class DocstringRemover(ast.NodeTransformer):
    """
    A node transformer that removes docstrings from functions, classes, and modules.
    """
    def _remove_docstring(self, node):
        if not (node.body and isinstance(node.body, ast.Expr)):
            return
        first_stmt = node.body
        # In Python 3.8+, docstrings are ast.Constant nodes
        if isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
            node.body = node.body[1:]

    def visit_FunctionDef(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

    def visit_Module(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

def remove_comments_and_docstrings(source: str) -> str:
    """
    Removes all comments and docstrings from a Python source string.
    Uses `tokenize` for comments and `ast` for docstrings for robustness.
    """
    try:
        # First, remove comments using tokenize, which is safer than regex.
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        untokenized_source = tokenize.untokenize(
            (token for token in tokens if token.type != tokenize.COMMENT)
        )
    except (tokenize.TokenError, IndentationError):
        # If tokenizing fails, fall back to the original source for AST parsing.
        untokenized_source = source

    try:
        # Then, remove docstrings using AST, which is safer than regex.
        tree = ast.parse(untokenized_source)
        transformer = DocstringRemover()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)
    except (SyntaxError, ValueError):
        # If parsing fails at any stage, return the source after comment removal.
        # This is a safe fallback.
        return untokenized_source

def collapse_blank_lines(source: str) -> str:
    """
    Collapses multiple consecutive blank lines into a single blank line.
    """
    lines = source.splitlines()
    result_lines = []
    last_line_was_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and last_line_was_blank:
            continue
        result_lines.append(line)
        last_line_was_blank = is_blank
    return '\n'.join(result_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 refine_context.py <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv
    source_code = ''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Only apply Python-specific refinement to .py files
        if file_path.endswith('.py'):
            refined_code = remove_comments_and_docstrings(source_code)
        else:
            refined_code = source_code

        # Collapse blank lines for all file types
        final_code = collapse_blank_lines(refined_code)
        print(final_code)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        # Failsafe: if any error occurs during processing,
        # print the original content to avoid data loss in the context file.
        if source_code:
            print(source_code)
        sys.exit(0) # Exit with 0 to not break the bash pipe

if __name__ == "__main__":
    main()