from tabulate import tabulate

_verbose = False  # internal flag
_tables = False

def setup(verbose, tables):
    global _verbose, _tables
    _verbose = verbose
    _tables = tables

def vprint(*messages):
    if _verbose:
        print(*messages)

def tprint(*tables):
    if _tables:
        print(tabulate(*tables,
                       headers='keys',
                       tablefmt='mixed_grid',
                       maxcolwidths=24))