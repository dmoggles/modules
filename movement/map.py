'''
Created on Nov 9, 2015

@author: Dmitry
'''
from __future__ import generators
import requests
import xml.etree.ElementTree as ET


class priorityDictionary(dict):
    def __init__(self):
        '''Initialize priorityDictionary by creating binary heap
of pairs (value,key).  Note that changing or removing a dict entry will
not remove the old pair from the heap until it is found by smallest() or
until the heap is rebuilt.'''
        self.__heap = []
        dict.__init__(self)

    def smallest(self):
        '''Find smallest item after removing deleted items from heap.'''
        if len(self) == 0:
            raise IndexError, "smallest of empty priorityDictionary"
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2*insertionPoint+1
                if smallChild+1 < len(heap) and \
                        heap[smallChild] > heap[smallChild+1]:
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild
        return heap[0][1]
    
    def __iter__(self):
        '''Create destructive sorted iterator of priorityDictionary.'''
        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]
        return iterfn()
    
    def __setitem__(self,key,val):
        '''Change value stored in dictionary and add corresponding
pair to heap.  Rebuilds the heap if the number of deleted items grows
too large, to avoid memory leakage.'''
        dict.__setitem__(self,key,val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v,k) for k,v in self.iteritems()]
            self.__heap.sort()  # builtin sort likely faster than O(n) heapify
        else:
            newPair = (val,key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and \
                    newPair < heap[(insertionPoint-1)//2]:
                heap[insertionPoint] = heap[(insertionPoint-1)//2]
                insertionPoint = (insertionPoint-1)//2
            heap[insertionPoint] = newPair
    
    def setdefault(self,key,val):
        '''Reimplement setdefault to call our customized __setitem__.'''
        if key not in self:
            self[key] = val
        return self[key]

def Dijkstra(G,start,end=None):
    """
    Find shortest paths from the start vertex to all
    vertices nearer than or equal to the end.

    The input graph G is assumed to have the following
    representation: A vertex can be any object that can
    be used as an index into a dictionary.  G is a
    dictionary, indexed by vertices.  For any vertex v,
    G[v] is itself a dictionary, indexed by the neighbors
    of v.  For any edge v->w, G[v][w] is the length of
    the edge.  This is related to the representation in
    <http://www.python.org/doc/essays/graphs.html>
    where Guido van Rossum suggests representing graphs
    as dictionaries mapping vertices to lists of neighbors,
    however dictionaries of edges have many advantages
    over lists: they can store extra information (here,
    the lengths), they support fast existence tests,
    and they allow easy modification of the graph by edge
    insertion and removal.  Such modifications are not
    needed here but are important in other graph algorithms.
    Since dictionaries obey iterator protocol, a graph
    represented as described here could be handed without
    modification to an algorithm using Guido's representation.

    Of course, G and G[v] need not be Python dict objects;
    they can be any other object that obeys dict protocol,
    for instance a wrapper in which vertices are URLs
    and a call to G[v] loads the web page and finds its links.
    
    The output is a pair (D,P) where D[v] is the distance
    from start to v and P[v] is the predecessor of v along
    the shortest path from s to v.
    
    Dijkstra's algorithm is only guaranteed to work correctly
    when all edge lengths are positive. This code does not
    verify this property for all edges (only the edges seen
     before the end vertex is reached), but will correctly
    compute shortest paths even for some graphs with negative
    edges, and will raise an exception if it discovers that
    a negative edge has caused it to make a mistake.
    """

    D = {}    # dictionary of final distances
    P = {}    # dictionary of predecessors
    Q = priorityDictionary()   # est.dist. of non-final vert.
    Q[start] = 0
    
    for v in Q:
        D[v] = Q[v]
        if v == end: break
        
        for w in G[v].exits:
            vwLength = D[v] + 1
            if w in D:
                if vwLength < D[w]:
                    raise ValueError, \
  "Dijkstra: found better path to already-final vertex"
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v
    
    return (D,P)

def shortestPath(G,start,end):
    """
    Find a single shortest path from the given start vertex
    to the given end vertex.
    The input has the same conventions as Dijkstra().
    The output is a list of the vertices in order along
    the shortest path.
    """

    D,P = Dijkstra(G,start,end)
    Path = []
    while 1:
        Path.append(end)
        if end == start: break
        end = P[end]
    Path.reverse()
    return Path

def exits_to_dict(exit_list):
    exits= {}
    for e in exit_list:
        exits[int(e.attrib['target'])]=e.attrib['direction']
    return exits

class Room:
    def __init__(self, vnum, name, area, exits):
        self.vnum=vnum
        self.name = name
        self.area = area
        self.exits = exits
        

class MapFromXml:
    def __init__(self, url='http://www.imperian.com/maps/map.xml'):
        self.room_dict={}
        self.areas={}
        r=requests.get(url)
        if r.ok:
            root=ET.fromstring(r.text)
            for area in root.findall('areas/area'):
                self.areas[int(area.attrib['id'])]=area.attrib['name']
            for room in root.findall('rooms/room'):
                room_obj = Room(int(room.attrib['id']), room.attrib['title'],int(room.attrib['area']), exits_to_dict(room.findall('exit')))
                self.room_dict[room_obj.vnum]=room_obj
            for room in self.room_dict:
                for e in self.room_dict[room].exits.keys():
                    if e not in self.room_dict:
                        del self.room_dict[room].exits[e]
                    
    
    def __getitem__(self, item):
        return self.room_dict[item]
    
    def find_by_name(self, name):
        return [r for r in self.room_dict.values() if name in r.name]
    
    
    def area_tree(self, start, blacklist):
        '''
        @param start: Room number of starting room
         
        '''
        if not start in self.room_dict:
            return []
        area_id = self.room_dict[start].area
        visited, stack = [], [start]
        while stack:
            vertex = stack.pop()
            if int(vertex) not in blacklist:
                if vertex not in visited and self.room_dict[vertex].area == area_id:
                    visited.append(vertex)
                    stack.extend(set(self.room_dict[vertex].exits.keys()) - set(visited))
        return visited
    


    

    def shortest_path(self, start, goal):
        return shortestPath(self.room_dict, start, goal)
    
    
    
    def traverse(self, start, blacklist=[]):
        p = self.area_tree(start, blacklist)
        full_p=[]
        for  i in xrange(len(p)):
            full_p.append(p[i])
            if i == len(p)-1:
                continue
            if not p[i+1] in self.room_dict[p[i]].exits:
                backtrack = self.shortest_path(p[i], p[i+1])
                full_p.extend(backtrack[1:-1])
        full_p.extend(self.shortest_path(full_p[-1],full_p[0])[1:])
        return full_p
            

    
if __name__=="__main__":
    m=MapFromXml()
    m.visit_area(7815)