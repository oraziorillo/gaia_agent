import ast
import operator
import math
from typing import Union
from langchain.tools import tool

class SafeMathEvaluator:
    """
    Safe mathematical expression evaluator that only allows basic math operations
    and mathematical functions while preventing code injection attacks.
    """
    
    # Supported operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }
    
    # Supported mathematical functions
    functions = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        # Math module functions
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'exp': math.exp,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': math.factorial,
        'degrees': math.degrees,
        'radians': math.radians,
    }
    
    # Mathematical constants
    constants = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
    }
    
    def evaluate(self, expression: str) -> Union[float, int]:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression as string
            
        Returns:
            Result of the mathematical calculation
            
        Raises:
            ValueError: If the expression contains unsafe operations
            SyntaxError: If the expression has invalid syntax
            ZeroDivisionError: If division by zero occurs
        """
        try:
            # Parse the expression into an AST
            node = ast.parse(expression, mode='eval')
            return self._eval_node(node.body)
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {str(e)}")
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):  # Numbers
            return node.value
        elif isinstance(node, ast.Constant):  # For older Python versions
            return node.n
        elif isinstance(node, ast.Name):  # Variables/constants
            if node.id in self.constants:
                return self.constants[node.id]
            else:
                raise ValueError(f"Undefined variable: {node.id}")
        elif isinstance(node, ast.BinOp):  # Binary operations
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
            
            # Special handling for division by zero
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Division by zero")
            
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):  # Unary operations
            operand = self._eval_node(node.operand)
            op = self.operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operation: {type(node.op).__name__}")
            return op(operand)
        elif isinstance(node, ast.Call):  # Function calls
            func_name = node.func.id
            if func_name not in self.functions:
                raise ValueError(f"Unsupported function: {func_name}")
            
            args = [self._eval_node(arg) for arg in node.args]
            func = self.functions[func_name]
            
            try:
                return func(*args)
            except Exception as e:
                raise ValueError(f"Error calling function {func_name}: {str(e)}")
        elif isinstance(node, ast.List):  # Lists (for functions like min, max, sum)
            return [self._eval_node(item) for item in node.elts]
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")

# Initialize the evaluator
math_evaluator = SafeMathEvaluator()

@tool
def evaluate_expression(expression: str) -> str:
    """
    Perform mathematical calculations safely. This tool can handle:
    - Basic arithmetic: +, -, *, /, %, //, **
    - Mathematical functions: sqrt, sin, cos, tan, log, exp, etc.
    - Constants: pi, e, tau, inf
    - Functions: abs, round, min, max, sum, factorial
    
    Examples:
    - "2 + 3 * 4" -> 14
    - "sqrt(16)" -> 4.0
    - "sin(pi/2)" -> 1.0
    - "log(e)" -> 1.0
    - "2**3" -> 8
    
    Args:
        expression: Mathematical expression as a string
        
    Returns:
        String representation of the calculation result
    """
    try:
        # Clean the input
        expression = expression.strip()
        
        if not expression:
            return "Error: Empty expression provided"
        
        # Evaluate the expression
        result = math_evaluator.evaluate(expression)
        
        # Format the result nicely
        if isinstance(result, float):
            # Round to reasonable precision and remove trailing zeros
            if result.is_integer():
                return str(int(result))
            else:
                return f"{result:.10g}"
        else:
            return str(result)
            
    except ZeroDivisionError:
        return "Error: Division by zero"
    except ValueError as e:
        return f"Error: {str(e)}"
    except SyntaxError:
        return "Error: Invalid mathematical expression syntax"
    except Exception as e:
        return f"Error: Unexpected error occurred - {str(e)}"