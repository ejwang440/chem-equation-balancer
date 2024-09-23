from flask import Flask, request
import chem
app = Flask(__name__)


UPPER = 1
LOWER = 2
NUMBER = 3


# The HTML used to display our home page! Pay special attention to the "name"
# fields for our input forms -- that's how a function can look up data.
HEADER = "<h1 style='text-align:center;background-color: yellow;font-family:impact, sans serif;'> Chemical Equation Balancer </h1>  <style>li { margin-left: -25px; }</style>"
FORM = '''
<form action="/input" method="post" style="text-align:center">
 <input
   id="reactants"
   name="reactants"
   placeholder="Enter the left side of the equation here (Ex: H2 + O2)"
   style="height: 50px; width: 500px; background-color: pink"


 >
 &rarr;
 <input
   id="products"
   placeholder="Enter the right side of the equation here (Ex: H2O)"
   name="products"
   style="height: 50px; width: 500px; background-color: pink"
 >
 <br>
 <br>


 <input
   style = "height: 50px; text-align:center;background-color:yellow"
   type="submit"
   value="Balance"
 >


</form>
<hr>
'''


history = []


def page(msg):
    result = HEADER + FORM + "<ul>"
    msgs = history
    if msg and msg not in history:
        msgs += [msg]

    # TODO: Add the elements in `msgs` to the HTML list by
    # looping over the list, and adding the items to <li></li>
    # tags.

    result += "</ul>"
    if msg or history:
        result += "<br><br>"
    for i in msgs:
        result += "<li>" + i + "</li>"

    # TODO: Update our history. If page() was given a new message,
    # and that message is not already in history, then add it.
    if msg not in history:
        history.append(msg)

    return result


def error(msg, r, p):
    reactsd = display_side(r)
    prodsd = display_side(p)
    return page(
        f"<b>{reactsd} &rarr; {prodsd}</b> " + msg
    )


def letter_type(x):
    if len(x) == 0:
        return None
    else:
        x = x[0]
    if x.isupper():
        return UPPER
    elif x.islower():
        return LOWER
    elif x.isnumeric():
        return NUMBER


def split(element):
    element = list(element)
    if not element:
        return []
    partial = element.pop(0)
    prev_type = letter_type(partial)
    result = []
    while element or partial:
        next_type = letter_type(element)
        if not next_type or next_type == UPPER or\
           (prev_type != NUMBER and next_type == NUMBER):
            result.append(partial)
            partial = ""
        if element:
            partial += element.pop(0)
        prev_type = next_type
    return result


# Given a compound, return the appropriate HTML to display that compound.
# To display subscripts in HTML, put the number in between <sub> </sub>,
# so H2O would look like H<sub>2</sub>O


def display(str_cmpd):
    for i in str_cmpd:
        if i.isdigit():
            str_cmpd = str_cmpd.replace(i, f"<sub>{i}</sub>")
    return str_cmpd


# print(display("H20O"))


def display_side(side, sol=None):
    side = side.replace(" ", "").split("+")
    for i in range(len(side)):
        side[i] = display(side[i])
        if sol and sol[i] != 1:
            side[i] = str(sol[i]) + side[i]
    return " + ".join(side)


# Take in a "list element" and convert it into a list of
# tuples that our chemical equation code can work with
# Ex: ['H', '2'] --> [('H', 2)]
# Ex: ['C', 'O', '2'] --> [('C', 1), ('O', 2)]


def parse(element):
    tup_list = []
    for i in range(len(element)):
        if element[i].isdigit():
            continue
        elif element[i].isalpha() and i == len(element)-1:
            tup_element = (element[i], 1)
            tup_list.append(tup_element)
        elif element[i].isalpha() and element[i+1].isdigit():
            tup_element = (element[i], int(element[i+1]))
            tup_list.append(tup_element)
        else:
            tup_element = (element[i], 1)
            tup_list.append(tup_element)
    return tup_list


print(parse(['C', 'O', '2']))


# Given the chemical equation written in one of the inputs on the
# homepage, convert it into a list of tuple (you probably want to
# use the parse you wrote here!)
# Ex: 'H2 + O2' --> [[('H', 2)], [('O', 2)]]
# Ex: 'H2O' --> [[('H', 2), ('O', 1)]]


def parse_side(side):
    split_side = side.split(" + ")
    side_list = []
    for i in range(len(split_side)):
        testprint = parse(split_side[i])
        print(testprint)
        side_list.append(parse(split_side[i]))
    return side_list


print(parse_side('H2 + O2'))


# In the balance function, fill in the two variables at the very beginning of the function.
# To access form data, you'll want to use the request.form variable, and the "name" field of the form element.
# So, to get the data in the reactants field, you would write request.form['reactants'].


@app.route("/input", methods=['POST'])
def balance():
    reactant_form_data = request.form['reactants']  # Fill this in!
    product_form_data = request.form['products']  # Fill this in!
    reacts = parse_side(reactant_form_data)
    prods = parse_side(product_form_data)
    atoms1 = chem.find_atoms(reacts)
    atoms2 = chem.find_atoms(prods)
    if not atoms1 or set(atoms1) != set(atoms2):
        return error(
            "is not a valid chemical equation.",
            reactant_form_data,
            product_form_data
        )

    sol = chem.solve(chem.construct_matrix(atoms1, reacts, prods))
    if not sol or float('inf') in sol or float('nan') in sol:
        return error(
            "does not have a valid solution.",
            reactant_form_data,
            product_form_data
        )

    sol = [int(x) for x in sol]
    reactsd = display_side(reactant_form_data, sol)
    prodsd = display_side(product_form_data, sol[len(reacts):])
    return page(f"The balanced equation is <b>{reactsd} &rarr; {prodsd}</b>.")


@app.route("/")
def homepage():
    return page("")


app.run(host='0.0.0.0', port=81, debug=True)
