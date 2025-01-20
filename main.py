from collections import deque

def row_column_constraints(grid, n):
    for i in range(n):
        row_set = set()
        col_set = set()
        for j in range(n):
            if grid[i][j] in row_set:
                return False
            row_set.add(grid[i][j])

            if grid[j][i] in col_set:
                return False
            col_set.add(grid[j][i])
    return True


def group_constraints(cells,operation,target):
    if len(cells) == 1:
        return cells[0] == target

    if operation == '+':
        return sum(cells) == target
    elif operation == '-':
        return abs(cells[0] - cells[1]) == target
    elif operation == '*':
        product = 1
        for cell in cells:
            product *= cell
        return product == target
    elif operation == '/':
        return cells[1] / cells[0] == target
    else:
        return False

        
def is_consistent(value, variable, assignment, groups, operator, target):
    # First check if any group constraints are violated
    for group_vars, group_op, group_target in groups:
        # Check if our variables are part of this group
        if all(var in group_vars for var in variable):
            # Get all values we know
            values = {}
            for var in group_vars:
                if var in variable and var == variable[-1]:
                    values[var] = value
                elif var in assignment:
                    values[var] = assignment[var]
            
            # If we have enough values to check a constraint
            if len(values) == len(group_vars):
                # Sort values by position in group_vars to maintain order
                ordered_values = [values[var] for var in group_vars]
                
                if group_op == '+':
                    result = sum(ordered_values)
                    if result != group_target:
                        return False
                elif group_op == '*':
                    result = 1
                    for v in ordered_values:
                        result *= v
                    if result != group_target:
                        return False
                elif group_op == '-':
                    if len(ordered_values) == 2:
                        if abs(ordered_values[1] - ordered_values[0]) != group_target:
                            return False
                elif group_op == '/':
                    if len(ordered_values) == 2:
                        if ordered_values[1] == 0:
                            return False
                        if ordered_values[0] / ordered_values[1] != group_target:
                            return False

    # Check row/column constraints (no duplicate values)
    for var in variable:
        if var in assignment and assignment[var] == value:
            return False
            
    return True

def get_arcs(grid, group, n):
    arcs = []
    for i in range(n):
        for j in range(n):
            for k in range(j+1, n):
                arcs.append((f'grid_{i}_{j}', f'grid_{i}_{k}'))
                arcs.append((f'grid_{j}_{i}', f'grid_{k}_{i}'))
    for group in group:
        cells, operation, target = group
        for i in range(len(cells)):
            for j in range(i + 1, len(cells)):
                arcs.append((cells[i], cells[j]))

    return arcs


def setup_puzzle(N, groups):
    csp = {
        'variables': [(i, j) for i in range(N) for j in range(N)],
        'domains': {(i, j): list(range(1, N+1)) for i in range(N) for j in range(N)},
        'assignment': {},
        'constraints': [],
        'neighbors': {(i, j): set() for i in range(N) for j in range(N)},
        'groups': groups
    }
    
    print("Setting up constraints...")
    # Add row and column constraints
    for i in range(N):
        for j in range(N):
            # Add row constraints
            for k in range(N):
                if j != k:
                    csp['constraints'].append(((i, j), (i, k)))
                    csp['neighbors'][(i, j)].add((i, k))
            # Add column constraints
            for k in range(N):
                if i != k:
                    csp['constraints'].append(((i, j), (k, j)))
                    csp['neighbors'][(i, j)].add((k, j))
    
    print(f"Added {len(csp['constraints'])} row/column constraints")
    
    # Add group constraints
    group_constraints = 0
    for group_vars, op, target in groups:
        print(f"Adding constraints for group: {group_vars} {op} = {target}")
        for v1 in group_vars:
            for v2 in group_vars:
                if v1 != v2:
                    csp['constraints'].append((v1, v2))
                    csp['neighbors'][v1].add(v2)
                    group_constraints += 1
    
    print(f"Added {group_constraints} group constraints")
    print(f"Total constraints: {len(csp['constraints'])}")
    return csp

def ac3(csp):
    queue = deque(csp['constraints'])
    print(f"Initial queue size: {len(queue)}")
    steps = 0
    while queue:
        steps += 1
        if steps % 100 == 0:
            print(f"Step {steps}, Queue size: {len(queue)}")
            print(f"Current domains: {csp['domains']}")
        
        (xi, xj) = queue.popleft()
        if revise(csp, xi, xj):
            if len(csp['domains'][xi]) == 0:
                print(f"Domain of {xi} became empty!")
                return False
            for xk in csp['neighbors'][xi]:
                if xk != xj:
                    queue.append((xk, xi))
    print(f"AC3 finished after {steps} steps")
    return True

def revise(csp, xi, xj):
    revised = False
    # Find which groups these variables belong to together
    shared_groups = []
    for group_vars, op, target in csp['groups']:
        if xi in group_vars and xj in group_vars:
            shared_groups.append((group_vars, op, target))
    
    # If they're not in any groups together and not in same row/col, they don't constrain each other
    if not shared_groups and (xi[0] != xj[0] and xi[1] != xj[1]):
        return False
    
    # Try each value in xi's domain
    for x in list(csp['domains'][xi]):
        # Check if there's any value in xj's domain that allows this value of x
        consistent = False
        for y in csp['domains'][xj]:
            # Skip if it's the same value and they're in same row/col
            if x == y and (xi[0] == xj[0] or xi[1] == xj[1]):
                continue
                
            # Create a temporary assignment
            temp_assignment = csp['assignment'].copy()
            temp_assignment[xj] = y
            
            # For each group they share, check if the constraint can be satisfied
            constraint_satisfied = True
            for group_vars, op, target in shared_groups:
                # Get all known values for this group
                values = {}
                for var in group_vars:
                    if var == xi:
                        values[var] = x
                    elif var in temp_assignment:
                        values[var] = temp_assignment[var]
                
                # If we have all values for this group, check if constraint is satisfied
                if len(values) == len(group_vars):
                    ordered_values = [values[var] for var in group_vars]
                    if op == '+':
                        if sum(ordered_values) != target:
                            constraint_satisfied = False
                            break
                    elif op == '*':
                        product = 1
                        for v in ordered_values:
                            product *= v
                        if product != target:
                            constraint_satisfied = False
                            break
                    elif op == '-':
                        if abs(ordered_values[1] - ordered_values[0]) != target:
                            constraint_satisfied = False
                            break
                    elif op == '/':
                        if ordered_values[1] == 0 or ordered_values[0] / ordered_values[1] != target:
                            constraint_satisfied = False
                            break
            
            if constraint_satisfied:
                consistent = True
                break
                
        if not consistent:
            print(f"Removing {x} from domain of {xi} due to constraint with {xj}")
            if shared_groups:
                print(f"  Due to groups: {shared_groups}")
            else:
                print(f"  Due to row/column constraint")
            csp['domains'][xi].remove(x)
            revised = True
            
    return revised



N= 4
groups=[
    ([(0, 0), (0, 1), (1, 0)],'*', 24),
    ([(0, 2), (0, 3)],'/',2),
    ([(1, 1), (1, 2)],'-',3),
    ([(1,3), (2,3)],'-',1),
    ([(2,0), (2,1)],'+',5),
    ([(2,2), (3,2), (3,3)],'+',6),
    ([(3,0), (3,1)],'-',3)
]

csp = setup_puzzle(N, groups)
if ac3(csp):
    print("Solution found")
else:
    print("No solution found.")
