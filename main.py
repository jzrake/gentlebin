import ast
from pycparser import c_generator
from pycparser.c_ast import *


def to_c_bin_op(node):
    if isinstance(node, ast.Add):
        return "+"
    if isinstance(node, ast.Sub):
        return "-"
    if isinstance(node, ast.Mult):
        return "*"
    if isinstance(node, ast.Div):
        return "/"
    raise ValueError(f"unsupported binary operation: {node}")


def to_c_identifier_type(t):
    if isinstance(t, ast.Constant) and t.value is None or t is None:
        return IdentifierType(names=["void"])
    if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Tuple):
        return IdentifierType(names=["TUPLE"])
    if isinstance(t, ast.Subscript) and t.value.id == "view":
        return PtrDecl(
            quals=None,
            type=TypeDecl(
                declname=None,
                quals=None,
                align=None,
                type=to_c_identifier_type(t.slice),
            ),
        )
    if isinstance(t, ast.Name):
        match t.id:
            case "int":
                return IdentifierType(names=["int"])
            case "float":
                return IdentifierType(names=["double"])
    raise ValueError(f"unsupported type annotation: {t}")


def to_c_node(node, known_type=None):
    if node is None:
        return None
    if isinstance(node, ast.Assign):
        raise ValueError("all assignments must be type-annotated")
    if isinstance(node, ast.Return):
        return Return(expr=to_c_node(node.value, known_type=known_type))
    if isinstance(node, ast.Constant):
        return Constant(type=None, value=str(node.value))
    if isinstance(node, ast.Name):
        return ID(node.id)
    if isinstance(node, ast.BinOp):
        return BinaryOp(
            to_c_bin_op(node.op),
            to_c_node(node.left),
            to_c_node(node.right),
        )
    if isinstance(node, ast.Subscript):
        return ArrayRef(
            name=to_c_node(node.value),
            subscript=to_c_node(node.slice),
        )
    if isinstance(node, ast.Call):
        return FuncCall(
            name=ID(name=node.func.id),
            args=ExprList(exprs=map(to_c_node, node.args)),
        )
    if isinstance(node, ast.IfExp):
        return TernaryOp(
            to_c_node(node.test),
            to_c_node(node.body),
            to_c_node(node.orelse),
        )
    if isinstance(node, ast.Tuple):
        if known_type is None:
            raise ValueError("converting a tuple requires known type")
        return CompoundLiteral(
            type=known_type,
            init=InitList(exprs=map(to_c_node, node.elts)),
        )
    if isinstance(node, ast.AugAssign):
        return Assignment(
            op=to_c_bin_op(node.op) + "=",
            lvalue=to_c_node(node.target),
            rvalue=to_c_node(node.value),
        )
    if isinstance(node, ast.AnnAssign):
        return Decl(
            name=node.target.id,
            quals=None,
            align=None,
            storage=None,
            funcspec=None,
            type=TypeDecl(
                declname=node.target.id,
                quals=None,
                align=None,
                type=to_c_identifier_type(node.annotation),
            ),
            init=to_c_node(
                node.value,
                known_type=to_c_identifier_type(node.annotation),
            ),
            bitsize=None,
        )
    if isinstance(node, ast.FunctionDef):
        return FuncDef(
            decl=Decl(
                name=node.name,
                quals=None,
                storage=None,
                funcspec=None,
                type=FuncDecl(
                    args=ParamList(
                        [
                            Decl(
                                name=arg.arg,
                                quals=None,
                                align=None,
                                storage=None,
                                funcspec=None,
                                type=TypeDecl(
                                    declname=arg.arg,
                                    quals=None,
                                    align=None,
                                    type=to_c_identifier_type(arg.annotation),
                                ),
                                init=None,
                                bitsize=None,
                            )
                            for arg in node.args.args
                        ]
                    ),
                    type=TypeDecl(
                        declname=node.name,
                        quals=None,
                        type=to_c_identifier_type(node.returns),
                        align=None,
                    ),
                ),
                init=None,
                bitsize=None,
                align=None,
            ),
            param_decls=None,
            body=Compound(
                block_items=(
                    (
                        to_c_node(n, known_type=to_c_identifier_type(node.returns))
                        for n in node.body
                    )
                )
            ),
        )
    raise ValueError(f"unsupported construct: {node}")


def emit_c_ast(filename):
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

    generator = c_generator.CGenerator()
    for c_node in emit_c_ast(filename):
        print(generator.visit(to_c_node(c_node)))
