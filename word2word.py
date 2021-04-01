from rich import print
from anytree import Node, RenderTree, Resolver, resolver

import enchant
import timeit

# constants
ALPHABET = [chr(letter).lower() for letter in range(97, 123)]
r = Resolver("name")


# function
# this w/change_char uses a lambda function to generate the word
# is slightly but consistently slower
def generate_permutations_lambda(
        word, char_pos=0, chars=ALPHABET,
        dictionary=enchant.Dict("en_US")):

    generator = change_char(char_pos)
    yield from [
        generator(word, char) for char in chars
        if dictionary.check(generator(word, char).lower())
        and word.lower() != generator(word, char).lower()]

    if char_pos + 1 < len(word):
        yield from (generate_permutations_lambda(word, char_pos+1))


def change_char(pos):
    return lambda word, letter: f"{word[:pos]}{letter}{word[int(pos+1):]}"


def generate_permutations_manual(
        word, pos=0, chars=ALPHABET,
        dictionary=enchant.Dict("en_US"), exclude=[]):
    yield from ([f"{word[:pos]}{char}{word[int(pos+1):]}" for char in chars
                if (dictionary.check(
                    f"{word[:pos]}{char}{word[int(pos+1):]}".lower())
                    and f"{word[:pos]}{char}{word[int(pos+1):]}".lower() != word.lower()
                    and not f"{word[:pos]}{char}{word[int(pos+1):]}".lower() in exclude)])

    if pos + 1 < len(word):
        yield from (generate_permutations_manual(word, pos+1, exclude=exclude))


def build_tree(word: str, target: str):
    # vars
    root = Node(word)
    base = root
    base_list = list(build_branch(parent=base))

    iterations = 0
    while not contains_child(root, target):
        if not base_list:
            for new_base in base.parent.children:
                base_list.extend(list(build_branch(parent=new_base)))
            iterations += 1
        else:
            base = base_list.pop()
            build_branch(parent=base)
            # print(f"New base {base} from {base_list}")

        if iterations >= 2:
            break

    print(r.glob(root, "*/hank"))
    to_output_file(str(RenderTree(root)))


def to_output_file(text: str, name="output"):
    with open(f"{name}.txt", "w") as w:
        w.write(text)


def build_branch(parent):
    new_words = list(generate_permutations_manual(
        parent.name,
        exclude=[parent.name] + [child.name for child in parent.children] + get_parents(parent)))
    for new_word in new_words:
        if not contains_child(parent, new_word):
            yield Node(new_word, parent=parent)
        else:
            print("Y")


def contains_child(tree, child_name: str):
    try:
        r.glob(tree, child_name)
    except resolver.ChildResolverError:
        return False
    except Exception:
        return False
    return True


def get_parents(node):
    parent_names = []
    branch = node
    try:
        while True:
            parent_names.append(branch.parent.name)
            branch = branch.parent
    except AttributeError:
        pass
    return parent_names


if __name__ == "__main__":
    build_tree("tank", "ship")
