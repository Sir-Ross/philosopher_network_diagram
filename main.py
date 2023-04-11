#https://networkx.org/documentation/stable/reference/readwrite/adjlist.html
#https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html#

import networkx as nx

f = open('adjacency_list.txt', 'rb')
graph = nx.read_adjlist(f, delimiter='|')
print(graph)
f.close()

nx.draw(graph, pos=nx.spring_layout(graph))