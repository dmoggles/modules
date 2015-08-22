'''
Created on Aug 22, 2015

@author: Dmitry
'''
import os
import csv

class AfflictionPriority():
    '''
    classdocs
    '''
    folder_name='affliction_priorities'
    file_name='%s_%s.csv'
    
    def __init__(self, skill, character, realm):
        '''
        Constructor
        '''
        self.skill=skill
        self.character=character
        self.realm=realm
        self.priority_list=[]
        self.affliction_dictionary={}
        
        priority_path=os.path.join(os.path.expanduser('~'), 'muddata', self.character, AfflictionPriority.folder_name)
        if not os.path.exists(priority_path):
            os.makedirs(priority_path,)
        
        
    def load_priorities(self, name):
        priority_path = os.path.join(os.path.expanduser('~'), 'muddata', self.character, AfflictionPriority.folder_name,
                            AfflictionPriority.file_name%(self.skill,name))
        if not os.path.exists(priority_path):
            self.realm.cwrite('<white*:red>Priority file %s does not exist'%name)
            return
        self.priority_list=[]
        self.affliction_dictionary={}
        with open(priority_path) as csvfile:
            reader=csv.DictReader(csvfile)
            for row in reader:
                aff=row['affliction']
                priority=float(row['priority'])
                t=(aff,priority)
                self.priority_list.append(t)
                self.affliction_dictionary[aff]=t
        
        self.priority_list=sorted(self.priority_list, key=lambda t:t[1])
                
        
        
if __name__=='__main__':
    afp=AfflictionPriority('testskill','testchar',None)