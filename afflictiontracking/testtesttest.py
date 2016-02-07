'''
Created on Nov 12, 2015

@author: Dmitry
'''
def get_data():
    
    nodes=[]
    while True:
        inp=raw_input()
        if inp=='':
            break
        t=tuple(inp.split(','))
        nodes.append(t)
        
    graph={}
    for n in nodes:
        if n[0]=='':
            continue
        if len(n)==3:
            graph[n[0]]=(n[1] if not n[1] == '' else None,n[2] if not n[2] == '' else None)
            if not n[1] == '':
                graph[n[1]]=(None,None)
            if not n[2] == '':
                graph[n[2]]=(None,None)
        if len(n)==2:
            if n[1]=='':
                graph[n[0]]=(None,n[2] if not n[2] == '' else None)
                graph[n[2]]=(None,None)
            else:
                graph[n[0]]=(n[1] if not n[1] == '' else None,None)
                graph[n[1]]=(None,None) 
                
    return graph

def bfs(graph, start):
    q = [(start, [start])]
    while q:
        node, visited_path = q.pop(0)
        for n in graph[node]:
            if n == None:
                continue
            if graph[n][0]==None and graph[n][1]==None:
                return len(visited_path)+1
            else:
                q.append((n, visited_path+[n]))
        
if __name__=='__main__':
    tuples=get_data()
    print(bfs(tuples, tuples.keys()[0]))
    