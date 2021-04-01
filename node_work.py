from anytree import Node, RenderTree, Resolver

top = Node("top", parent=None)
sub0 = Node("sub0", parent=top)
sub0sub0 = Node("sub0sub0", parent=sub0)
sub0sub1 = Node("sub0sub1", parent=sub0)
sub1 = Node("sub1", parent=top)

r = Resolver("name")

print(r.glob(top, "*/sub0sub0"))
