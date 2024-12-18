import re
import json
import operator

string_functions = ['concat', 'concatenate']

# Safe dictionary for evaluation
safe_dict = {
    'sum': sum,
    'max': max,
    'min': min,
    'concat': lambda *args: ''.join(map(str, args)),
    'concatenate': lambda *args: ''.join(map(str, args)),
    'operator': operator
}


def extract_elements(formula):
    """
    Extracts elements from a formula, including functions, variables, constants, and operators.

    :param formula: The formula to extract elements from.
    :type formula: str
    :return: A list of tuples, where each tuple contains the type of the element ('function', 'variable', 'quoted_constant', 'constant', 'operator') and the corresponding element.
    :rtype: List[Tuple[str, str]]
    :param formula:
    :type formula:
    :return:
    :rtype:
    """
    # Regular expressions to match functions, variables, constants, and operators
    function_pattern = r'\b(?:SUM|CONCATENATE|MAX|MIN)\b'
    variable_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*'
    quoted_constant_pattern = r"'[^']*'"
    constant_pattern = r'\b\d+(\.\d+)?\b'
    operator_pattern = r'[+\-*\/]'

    # Combine the patterns into a single pattern
    combined_pattern = re.compile(f'({function_pattern})|({variable_pattern})|({quoted_constant_pattern})|({constant_pattern})|({operator_pattern})')

    # Find all matches
    matches = combined_pattern.finditer(formula)

    # Capture elements in sequence
    elements = []
    for match in matches:
        if match.group(1):
            elements.append(('function', match.group(1)))
        elif match.group(2):
            elements.append(('variable', match.group(2)))
        elif match.group(3):
            elements.append(('quoted_constant', match.group(3).replace("'", '"')))
        elif match.group(4):
            elements.append(('constant', match.group(4)))
        elif match.group(6):
            elements.append(('operator', match.group(6)))

    return elements


def evaluate_subformula(subformula, json_data):
    """
    Evaluate a subformula using the provided JSON data.

    :param subformula: The subformula to evaluate.
    :type subformula: str

    :param json_data: The JSON data to use for evaluation.
    :type json_data: dict

    :return: The result of the evaluation.
    :rtype: any
    :param subformula:
    :type subformula:
    :param json_data:
    :type json_data:
    :return:
    :rtype:
    """
    elements = extract_elements(subformula)
    eval_parts = []
    is_string_function = False
    for elem_type, elem_value in elements:
        if elem_type == 'function':
            eval_parts.append(elem_value.lower() + '(')
            is_string_function = elem_value.lower() in string_functions
        elif elem_type == 'variable':
            value = get_value_from_json(json_data, elem_value)
            if is_string_function:
                value = '"' + str(value) + '"'
            eval_parts.append(str(value))
        elif elem_type == 'quoted_constant':
            value = elem_value
            eval_parts.append(value)
        elif elem_type == 'constant':
            value = elem_value
            if is_string_function:
                value = '"' + value + '"'
            eval_parts.append(value)
        elif elem_type == 'operator':
            eval_parts.append(elem_value)

    eval_formula = ''.join(eval_parts) + ')'
    return eval(eval_formula, {"__builtins__": None}, safe_dict)


def evaluate_formula(formula, json_data):
    """
    Evaluate a given formula using the provided JSON data.

    :param formula: The formula to evaluate.
    :type formula: str
    :param json_data: The JSON data to use for evaluation.
    :type json_data: dict
    :return: The result of the evaluation.
    :rtype: any
    """
    # Extract and evaluate subformulas
    elements = extract_elements(formula)
    eval_formula = ''
    should_evaluate = False
    last_function_index = 0
    for elem_type, elem_value in elements:
        if elem_type == 'function':
            func_start = formula.find(elem_value, last_function_index)
            func_end = formula.find(')', func_start) + 1
            last_function_index = func_end
            subformula = formula[func_start:func_end]
            result = evaluate_subformula(subformula, json_data)
            eval_formula += str(result)
        # elif elem_type == 'variable':
        #    value = get_value_from_json(json_data, elem_value)
        #    eval_formula += str(value)
        elif elem_type == 'quoted_constant':
            eval_formula += elem_value
        elif elem_type == 'constant':
            eval_formula += elem_value
        elif elem_type == 'operator':
            should_evaluate = True
            eval_formula += elem_value

    if should_evaluate:
        result = eval(eval_formula, {"__builtins__": None}, safe_dict)

    return result


def get_value_from_json(data, path):
    """
    Extract value from JSON data based on the provided path.

    :param data: JSON data.
    :type data: dict
    :param path: JSON path for element to get value from.
    :type path: str
    :return: Value from the JSON element found under specified path.
    :rtype: dict, str, list
    """
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, list):
            result = list()
            for val in value:
                result.append(get_value_from_json(val, key))
            value = result
        else:
            if key in value:
                value = value[key]
            else:
                raise KeyError(f"Key '{key}' not found in JSON data")
    return value


# Example JSON data
json_data = {
    "input": {
        "no": "123",
        "description": "Test Description",
        "lines": [{
            "amount": 100,
            "taxAmount": 10
        }, {
            "amount": 90,
            "taxAmount": 9
        }]
    }
}

if __name__ == "__main__":
    # Example usage with your formulas
    formulas = [
        "SUM(input.lines.amount)-SUM(input.lines.taxAmount)/SUM(input.lines.amount)",
        "SUM(input.lines.amount)",
        "CONCATENATE(input.no, ' ', input.description)",
        "MAX(input.lines.amount)",
        "MIN(input.lines.amount)",
        "MAX(input.lines.taxAmount)+SUM(input.lines.amount)",
        "MAX(input.lines.taxAmount)+MAX(input.lines.amount)"
    ]

    for formula in formulas:
        result = evaluate_formula(formula, json_data)
        print(f"Formula: {formula}")
        print(f"Result: {result}")
        print()
