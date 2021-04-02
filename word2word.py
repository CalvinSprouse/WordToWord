from anytree import Node, RenderTree, PreOrderIter, search, AsciiStyle
from rich import print

import argparse
import enchant

# constants
ALPHABET = [chr(letter).lower() for letter in range(97, 123)]


# word generators
def generate_permutations_on_tree(
        word: str, tree: Node, pos=0, chars=ALPHABET, dictionary=enchant.Dict("en_US")):
    '''
    Given a word generates all possible single letter changes that are also words
    by simply iterating over the alphabet and recursing to the next char in the word
    '''
    # a lambda function so I dont have to write 1 million f""
    generator = change_char(pos)

    # generates all changes to the first character of the word
    '''
    faster but brain hurty
    word_list = ([generator(word, char) for char in chars
                  if dictionary.check(generator(word, char))
                  and generator(word, char) != word.lower()
                  and not search.find(
                    tree, lambda node: node.name == generator(word, char))])
    '''
    word_list = []
    for char in chars:
        new_word = generator(word, char)
        if dictionary.check(new_word) and new_word != word.lower() and not search.find(
                tree, lambda node: node.name == new_word):
            word_list.append(new_word)

    # calls the function with the next character of the word if applicable
    if pos + 1 < len(word):
        word_list.extend(generate_permutations_on_tree(
            word=word, tree=tree, pos=int(pos+1), chars=chars, dictionary=dictionary))
    return word_list


# lambda function used to change a single char of a word given a position
def change_char(pos: int):
    return lambda word, char: f"{word[:pos]}{char}{word[int(pos+1):]}".lower()


# special tree print
def render_tree(tree: Node):
    print(RenderTree(tree, style=AsciiStyle()))


# essentially render tree but to text file
def output_tree(tree: Node, name=""):
    with open(f"{name}.out", "w") as w:
        for pre, fill, node in RenderTree(tree, style=AsciiStyle()):
            w.write("%s%s\n" % (pre, node.name))


# ensures the word can actually be mapped
def is_legal_word(word: str):
    return word.isalpha()


# checks if two trees contain matching leaves? end pieces
def has_match(tree1: Node, tree2: Node):
    tree2_nodes = [node.name for node in PreOrderIter(tree2)]
    tree1_nodes = [node.name for node in PreOrderIter(tree1)]
    match = set(tree1_nodes).intersection(tree2_nodes)
    return bool(match), match


# returns a list of names from leaf to root (child to oldest)
def deconstruct_tree(tree: Node, names=[]):
    if not names:
        names.append(tree.name)
    parent = tree.parent
    if parent:
        return deconstruct_tree(parent, names=names + [parent.name])
    return names


# generate new branches from youngest members of a tree
def generate_branches(tree: Node):
    has_succeded = False
    for new_parent in [node for node in PreOrderIter(tree) if not node.children]:
        permutations = generate_permutations_on_tree(word=new_parent.name, tree=tree)
        if permutations:
            has_succeded = True
            [Node(child, parent=new_parent) for child in permutations]
    return has_succeded


# link two words via tree and return all matches
def generate_word_tree_to_target(start_tree: Node, finish_tree: Node):
    match = has_match(start_tree, finish_tree)
    while not match[0]:
        if not generate_branches(start_tree) or not generate_branches(finish_tree):
            match = has_match(start_tree, finish_tree)
            if not match:
                return False
            else:
                return match[1]
        match = has_match(start_tree, finish_tree)

    return match[1]


# find all connected branches and return a list of nodes? list of start to finishes?
def find_connections(start_tree: Node, finish_tree: Node, matches):
    output_tree(start_tree, "st")
    output_tree(finish_tree, "ft")
    series = []
    for match in matches:
        s_match = list(reversed(deconstruct_tree(search.find(
            start_tree, lambda node: node.name == match), [])))
        f_match = deconstruct_tree(search.find(
            finish_tree, lambda node: node.name == match), [])
        series.append(s_match[:-1] + f_match)
    return series


# connect two words by changing one letter at a time
def two_word_connection(start_word: str, finish_word: str):
    if len(start_word) == len(finish_word) and is_legal_word(
            start_word) and is_legal_word(finish_word):
        start_node = Node(start_word)
        finish_node = Node(finish_word)
        match = generate_word_tree_to_target(start_node, finish_node)
        if match:
            return find_connections(start_node, finish_node, match)
        return None


# returns the first shortest chain
def get_shortest(chain):
    return min(chain, key=len)


# converts a single chain of words into a tree, why not
def convert_to_tree(chain):
    root = Node(chain.pop(0))
    base = root
    for child in chain:
        base = Node(child, parent=base)
    return root


# chain multipe words together
def word_to_word(start_word: str, *other_words, duplicate=False):
    try:
        word_list = list(reversed([start_word] + list(other_words)))
        returned_solutions = []
        if not any([not is_legal_word(word) for word in word_list]):
            first_word = word_list.pop()
            solutions = []
            while len(word_list) > 0:
                second_word = word_list.pop()
                solutions.append(two_word_connection(first_word, second_word))
                first_word = second_word

            base_combo = solutions.pop(0)
            for word_combo in solutions:
                new_list = []
                for b_chain in base_combo:
                    for chain in word_combo:
                        new_list.append(b_chain[:-1] + chain)
                base_combo = new_list
            returned_solutions = base_combo

            # remove duplicates
            if not duplicate:
                returned_solutions = [combo for combo in returned_solutions if
                                      len(set(combo)) == len(combo)]
        return returned_solutions
    except Exception:
        return []


# for the output when finding all
def prettify_list(list):
    return_list = []
    for chain in list:
        return_list.append(" -> ".join(chain))
    return "\n".join(''.join(map(str, item)) for item in return_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the shortest way to get from one word to another one letter change at a time")
    parser.add_argument(
        "words", metavar="W", type=str, nargs="+", help="List of words to connect")
    parser.add_argument(
        "--all", dest="find_all", action="store_const", const=True, default=False)
    parser.add_argument(
        "--duplicates-allowed", dest="dup",
        action="store_const", const=True, default=False)

    args = vars(parser.parse_args())
    if args["find_all"]:
        print(prettify_list(word_to_word(
            args["words"][0], *args["words"][1:], duplicate=args["dup"])))
    else:
        print(prettify_list([get_shortest(word_to_word(
            args["words"][0], *args["words"][1:], duplicate=args["dup"]))]))
