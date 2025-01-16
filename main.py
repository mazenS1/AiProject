def row_column_constraints(grid, n):
    for i in range(n):
        for j in range(n):
            for k in range(j+1, n):
                if grid[i][j] == grid[i][k] and j != k:
                    return False
            for k in range(i+1, n):
                if grid[i][j] == grid[k][j] and i != k:
                    return False
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
        return cells[0] / cells[1] == target
    else:
        return False
# Example usage
print(group_constraints([3, 7], '+', 10))  # True
print(group_constraints([8, 3], '-', 5))   # True
print(group_constraints([3, 4, 5], '*', 12))  # False
print(group_constraints([3, 4], '*', 12))  # True
print(group_constraints([8, 4], '/', 2))   # True
print(group_constraints([3, 6, 7], '+', 10))  # False
print(group_constraints([8], '-', 5))      # False
print(group_constraints([8],  8))  # True

# Example array to test the function
example_grid = [
    [1, 2, 3, 4],
    [2, 3, 4, 1],
    [3, 4, 1, 2],
    [4, 1, 2, 3]
]
example_grid_false = [
    [1, 2, 3, 4],
    [2, 3, 4, 1],
    [3, 4, 1, 2],
    [1, 2, 3, 4]
]






