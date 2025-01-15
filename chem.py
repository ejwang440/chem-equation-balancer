
from fractions import Fraction
import numpy as np


def find_atoms(reactants):
    atoms = []
    for i in range(len(reactants)):
        for j in range(len(reactants[i])):
            if reactants[i][j] not in atoms:
                atoms.append(reactants[i][j][0])
    return atoms


def get_num_atoms_in_compound(atom, compound):
    for i in range(len(compound)):
        if compound[i][0] == atom:
            return compound[i][1]
    return 0


def get_atom_in_side(atom, side):
    result = []
    for i in side:
        result.append(get_num_atoms_in_compound(atom, i))
    return result


def get_coeffs(atoms, side):
    result = []
    for i in atoms:
        result.append(get_atom_in_side(i, side))
    return result


def negate_all_coefficients(coeffs):
    result = []
    for i in coeffs:
        list = []
        for j in i:
            if j != 0:
                list.append(-j)
            else:
                list.append(0)
        result.append(list)
    return result


def construct_matrix(atoms, reactants, products):
    reactant_coeffs = get_coeffs(atoms, reactants)
    product_coeffs = negate_all_coefficients(get_coeffs(atoms, products))

    coeffs = []
    for x in range(len(atoms)):
        coeffs.append(reactant_coeffs[x] + product_coeffs[x])

    # Add a dummy equation to complete the system of equations.
    coeffs.append([1] + [0]*(len(coeffs[0])-1))
    return coeffs



def solve(coeffs):
    A = np.array(coeffs)
    b = np.array([0]*(len(coeffs)-1) + [1])
    solution = np.linalg.solve(A, b)
    solution = [Fraction(x).limit_denominator() for x in solution]

    # Scale the solutions so the coefficients are all integers
    x = max([x.denominator for x in solution])
    solution = [s * x for s in solution]
    return solution


SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


def chemical(chem):
    z = ""
    for x in chem:
        y = x[0]
        if x[1] != 1:
            j = ""
            for c in str(x[1]):
                j += SUBSCRIPTS[int(c)]
            y += j
        z += y
    return z


def equation(reactants, products, sol=None):
    def strside(side, N=0):
        output = []
        for i, x in enumerate(side):
            term = chemical(x)
            if sol and int(sol[i + N]) > 1:
                term = str(int(sol[i + N])) + term
            output.append(term)
        return " + ".join(output)
    return strside(reactants) + " → " + strside(products, N=len(reactants))


def balance(reactants, products):
    solution = solve(construct_matrix(
        find_atoms(reactants), reactants, products))
    print("Unbalanced Equation:", equation(reactants, products))
    print("  Balanced Equation:", equation(reactants, products, solution))


# H₂ + O₂ → H₂O
reactants = [[("H", 2)], [("O", 2)]]
products = [[("H", 2), ("O", 1)]]
balance(reactants, products)
print()

# C₃H₈ + O₂ → CO₂ + H₂O
reactants = [[("C", 3), ("H", 8)], [("O", 2)]]
products = [[("C", 1), ("O", 2)], [("H", 2), ("O", 1)]]
balance(reactants, products)
