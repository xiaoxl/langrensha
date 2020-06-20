import json
import random

#%%
class Langrensha():
    MODE_YNLB = {'shen': {'yuyanjia': 1, 'nvwu': 1, 'lieren': 1, 'baichi': 1}, 'cunmin': {'putong': 4}, 'lang': {'putong': 4}, 'renshu': 12, 'name': 'YNLB'}

    Mode_Default = MODE_YNLB

    def __init__(self, name='', users=None, mode=Mode_Default):
        self.__GAMENAME = name
        # understand MODE
        self.__NUMOFPLAYER = mode['renshu']
        self.__MODE = mode
        if users is None:
            users = list(range(self.__NUMOFPLAYER))
        self.__USERS = users
        roles = []
        for i in mode['shen'].keys():
            for j in range(mode['shen'][i]):
                roles.append('shen_'+i)
        for i in mode['cunmin'].keys():
            for j in range(mode['cunmin'][i]):
                roles.append('cunmin_'+i)
        for i in mode['lang'].keys():
            for j in range(mode['lang'][i]):
                roles.append('lang_'+i)
        self.__ROLES = roles
        status = {}
        temp = list(range(self.__NUMOFPLAYER))
        random.shuffle(temp)
        for i in range(self.__NUMOFPLAYER):
            status.update({i: {
                'name': self.__USERS[i],
                'role': self.__ROLES[temp[i]],
                'faction': self.__ROLES[temp[i]][0],
                'status': 'alive'
            }})
        self.__STATUS = status
        self.__LOG = ['Game started. # of players: '+ str(self.__NUMOFPLAYER)+ '. Game mode: ' + mode['name'] + '.']

    def shuffleroles(self):
        temp = list(range(self.__NUMOFPLAYER))
        random.shuffle(temp)
        for i in range(self.__NUMOFPLAYER):
            self.__STATUS[i]['role'] = self.__ROLES[temp[i]]
            self.__STATUS[i]['faction'] = self.__ROLES[temp[i]][0]


    def getgamename(self):
        return self.__GAMENAME

    def getroles(self):
        return self.__STATUS

    def printlog(self):
        return '\n'.join(self.__LOG)

a = Langrensha(users=['aa', 'bb', 'cc', 'dd', 'ww', 'tt', 'ss', 'da', 'vv', 'xx', 'bbaa', 'cccc'])
s = a.getroles()

print(s)
print('-------------------\n')
a.shuffleroles()
# j = json.load(a.getroles())
s = a.getroles()

print(s)