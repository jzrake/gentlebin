import ast
from pycparser import c_generator
from pycparser.c_ast import *


class UnsupportedConstruct(Exception):
    pass


def to_c_identifier_type(t):
    match t:
        case None | ast.Constant(value=None):
            return IdentifierType(names=["void"])
        case ast.Subscript(slice=ast.Tuple()):
            # tuples are not actually supported yet in C code
            return IdentifierType(names=["TUPLE"])
        case ast.Subscript(slice=slice, value=ast.Name("Array")):
            return PtrDecl(
                quals=None,
                type=TypeDecl(
                    declname=None,
                    quals=None,
                    align=None,
                    type=to_c_identifier_type(t.slice),
                ),
            )
        case ast.Name(id="int"):
            return IdentifierType(names=["int"])
        case ast.Name(id="float"):
            return IdentifierType(names=["double"])
    raise ValueError(f"unsupported type annotation: {t}")


def to_c_range_args(node):
    """
    Return C AST nodes for start, stop, stride args of a range call
    """
    match node:
        case ast.Call(func=ast.Name(id="range"), args=[i1]):
            ast.Constant("0"), i1, ast.Constant("1")
        case ast.Call(func=ast.Name(id="range"), args=[i0, i1]):
            args = i0, i1, ast.Constant("1")
        case ast.Call(func=ast.Name(id="range"), args=[i0, i1, di]):
            args = i0, i1, di
        case _:
            raise UnsupportedConstruct(
                f"must be a valid range call at line {node.lineno} got {node}"
            )
    return map(to_c_node, args)


def to_c_bin_op(node):
    match node:
        case ast.Add():
            return "+"
        case ast.Sub():
            return "-"
        case ast.Mult():
            return "*"
        case ast.Div():
            return "/"
    raise ValueError(f"unsupported binary operation: {node} at line {node.lineno}")


def to_c_node(node, known_type=None, force_compound=False):
    """
    Convert a small subset of Python AST to C AST.
    """
    match node:
        case None:
            return None
        case [node]:
            return to_c_node(node)
        case [*body]:
            return Compound(block_items=map(to_c_node, node))
        case ast.Return(value=value):
            return Return(expr=to_c_node(value, known_type=known_type))
        case ast.Constant(value=value):
            return Constant(type=None, value=str(value))
        case ast.Name(id=id):
            return ID(id)
        case ast.Assign():
            raise ValueError("all assignments must be type-annotated")
        case ast.AnnAssign(target=ast.Name(id=id), value=value, annotation=annotation):
            return Decl(
                name=id,
                quals=None,
                align=None,
                storage=None,
                funcspec=None,
                type=TypeDecl(
                    declname=id,
                    quals=None,
                    align=None,
                    type=to_c_identifier_type(annotation),
                ),
                init=to_c_node(value, to_c_identifier_type(annotation)),
                bitsize=None,
            )
        case ast.AugAssign(op=op, target=target, value=value):
            return Assignment(
                op=to_c_bin_op(op) + "=",
                lvalue=to_c_node(target),
                rvalue=to_c_node(value),
            )
        case ast.BinOp(op=op, left=left, right=right):
            return BinaryOp(
                to_c_bin_op(op),
                to_c_node(left),
                to_c_node(right),
            )
        case ast.Subscript(value=value, slice=slice):
            return ArrayRef(
                name=to_c_node(value),
                subscript=to_c_node(slice),
            )
        case ast.Call(func=func, args=args):
            return FuncCall(
                name=ID(name=func.id),
                args=ExprList(exprs=map(to_c_node, args)),
            )
        case ast.IfExp(test=test, body=body, orelse=orelse):
            return TernaryOp(
                to_c_node(test),
                to_c_node(body),
                to_c_node(orelse),
            )
        case ast.If(test=test, body=body, orelse=orelse):
            return If(
                cond=to_c_node(test),
                iftrue=to_c_node(body),
                iffalse=to_c_node(orelse),
            )
        case ast.Tuple(elts=elts):
            return CompoundLiteral(
                type=known_type,
                init=InitList(exprs=map(to_c_node, elts)),
            )
        case ast.FunctionDef(name=name, args=args, body=body, returns=returns):
            return FuncDef(
                decl=Decl(
                    name=name,
                    quals=None,
                    storage=None,
                    funcspec=None,
                    type=FuncDecl(
                        args=ParamList(
                            (
                                Decl(
                                    name=n.arg,
                                    quals=None,
                                    align=None,
                                    storage=None,
                                    funcspec=None,
                                    type=TypeDecl(
                                        declname=n.arg,
                                        quals=None,
                                        align=None,
                                        type=to_c_identifier_type(n.annotation),
                                    ),
                                    init=None,
                                    bitsize=None,
                                )
                                for n in args.args
                            )
                        ),
                        type=TypeDecl(
                            declname=name,
                            quals=None,
                            type=to_c_identifier_type(returns),
                            align=None,
                        ),
                    ),
                    init=None,
                    bitsize=None,
                    align=None,
                ),
                param_decls=None,
                body=Compound(block_items=map(to_c_node, body)),
            )
        case ast.For(target=ast.Name(id=counter_id), iter=iter, body=body):
            i0, i1, di = to_c_range_args(iter)
            return For(
                init=DeclList(
                    decls=[
                        Decl(
                            name=counter_id,
                            quals=None,
                            align=None,
                            storage=None,
                            funcspec=None,
                            type=TypeDecl(
                                declname=counter_id,
                                quals=None,
                                align=None,
                                type=IdentifierType(names=["int"]),
                            ),
                            init=i0,
                            bitsize=None,
                        )
                    ]
                ),
                cond=BinaryOp(
                    op="<",
                    left=ID(name=counter_id),
                    right=i1,
                ),
                next=Assignment(
                    op="+=",
                    lvalue=ID(name=counter_id),
                    rvalue=di,
                ),
                stmt=to_c_node(body),
            )
    raise UnsupportedConstruct(f"unsupported construct: {node} at line {node.lineno}")


def emit_py_ast(filename):
    """
    Iterates over function definition nodes found in a python source file
    """
    with open(filename) as infile:
        node = ast.parse(infile.read())
        for n in node.body:
            if isinstance(n, ast.FunctionDef):
                yield n


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-c", "--check", action="store_true")
    args = parser.parse_args()
    filename = args.filename

    if args.check:
        from mypy import api

        res = api.run([filename])
        if res[2]:
            print(res[0])
            exit()

    try:
        generator = c_generator.CGenerator()
        res = str()
        for node in emit_py_ast(filename):
            res += generator.visit(to_c_node(node))
        # remove newlines; good styling if processed through clang-format
        print(res.replace("\n", str()))
        # output the result from the C generator (not well styled)
        # print(res)
    except UnsupportedConstruct as e:
        print(f"{e} of {filename}")
