import json
import random
import math


#%%
class LRSMessage:
    '''
    target, sender, receiver are all playernums. 0 means system. The target can represent some other meaning like nvwu.
    '''
    def __init__(self, sender=0, receiver=0,
                 target=0, texttype='default', auth=None):
        self.sender = sender
        self.receiver = receiver
        self.target = target
        self.texttype = texttype
        self.auth = auth

    def todict(self):
        return {'sender': self.sender,
                'receiver': self.receiver,
                'target': self.target,
                'texttype': self.texttype,
                'auth': self.auth}


#%%
class User:
    def __init__(self, username, playernum=0):
        self.name = username
        self.playernum = playernum
        self.status = 'alive'
        self.role = 'unknown'
        self.roleClass = Modes.MODE_DICT[self.role]()

    def setrole(self, role):
        self.role = role
        self.roleClass = Modes.MODE_DICT[self.role]()

    def setnumber(self, num):
        self.playernum = num

    def setstatus(self, flag):
        self.status = flag

    def sendmessage(self, target, texttype='default', auth=None):
        if auth is None:
            auth = [self.playernum]
        return LRSMessage(sender=self.playernum, receiver=0,
                          target=target, texttype=texttype, auth=auth)

    def notifymessage(self, target, texttype='default', auth=None):
        if auth is None:
            auth = [self.playernum]
        return LRSMessage(sender=0, receiver=self.playernum,
                          target=target, texttype=texttype, auth=auth)

    def dumps(self):
        return {'name': self.name,
                'playernum': self.playernum,
                'status': self.status,
                'role': self.role,
                'roleinfo': self.roleClass.dumps()['info']}

    def loads(self, data):
        self.name = data['name']
        self.playernum = data['playernum']
        self.status = data['status']
        self.role = data['role']
        self.roleClass = Modes.MODE_DICT[self.role]()
        self.roleClass.loads({'name': data['role'], 'info': data['roleinfo']})


#%%
class Users:
    def __init__(self, listofusernames=None):
        self.users = list()
        if listofusernames is not None:
            for item in listofusernames:
                if isinstance(item, str):
                    self.users.append(User(username=item))
                if isinstance(item, User):
                    self.users.append(item)
            self.num = len(self.users)
            for item, cuser in enumerate(self.users):
                cuser.setnumber(item + 1)

    def nameindex(self, index=None):
        nameindex = {item.name: item for item in self.users}
        if index in nameindex.keys():
            nameindex = nameindex[index]
        return nameindex

    def numindex(self, index=None):
        numindex = {item.playernum: item for item in self.users}
        if index in numindex.keys():
            numindex = numindex[index]
        return numindex

    def roleindex(self, index=None):
        rlist = dict()
        for item in self.users:
            if item.role in rlist.keys():
                rlist[item.role].append(item)
            else:
                rlist.update({item.role: [item]})
        if index in rlist.keys():
            rlist = rlist[index]
        return rlist

    def statusindex(self, index=None):
        rlist = dict()
        for item in self.users:
            if item.status in rlist.keys():
                rlist[item.status].append(item)
            else:
                rlist.update({item.status: [item]})
        if index in rlist.keys():
            rlist = rlist[index]
        return rlist

    def renum(self):
        tempnum = list(range(1, self.num+1))
        random.shuffle(tempnum)
        for item, cuser in enumerate(self.users):
            cuser.setnumber(tempnum[item])

    def changeroles(self, listofrolenames):
        if len(listofrolenames) == self.num:
            for i in range(self.num):
                self.pick(i+1).setrole(listofrolenames[i])

    def copy(self):
        newusers = Users(self.nameindex().values())
        return newusers

    def print(self, basedon='playernum'):
        rlist = dict()
        if basedon == 'name':
            ulist = self.nameindex()
            for k in sorted(ulist.keys()):
                rlist.update({k: {'playernum': ulist[k].playernum,
                                  'role': ulist[k].role,
                                  'status': ulist[k].status}})
        elif basedon == 'role':
            ulist = self.roleindex()
            for k in sorted(ulist.keys()):
                templist = [{'playernum': t.playernum, 
                             'name': t.name, 
                             'status': t.status} for t in ulist[k]]
                rlist.update({k: templist})
        else:
            ulist = self.numindex()
            for k in sorted(ulist.keys()):
                rlist.update({k: {'name': ulist[k].name,
                                  'role': ulist[k].role,
                                  'status': ulist[k].status}})
        return rlist

    def pick(self, playernum):
        return self.numindex(playernum)

    def dumps(self):
        return [item.dumps() for item in self.users]

    def loads(self, data):
        self.num = len(data)
        self.users = list()
        for index in range(self.num):
            temp = User(' ')
            temp.loads(data[index])
            self.users.append(temp)


#%%
class Roles:
    def __init__(self, name, faction, timing):
        self.name = name
        self.faction = faction
        self.timing = timing
        self.info = dict()

    def night(self, **kwargs):
        pass

    def passive(self, **kwargs):
        pass

    def day(self, **kwargs):
        pass

    def dumps(self):
        return {'name': self.name,
                'info': self.info.copy()}

    def loads(self, data):
        temp = Modes.MODE_DICT[data['name']]()
        self.name = temp.name
        self.faction = temp.faction
        self.timing = temp.timing
        self.info = data['info']


class Roles_Unknown(Roles):
    def __init__(self):
        super().__init__('unknown', 'unknown', 0)


class Roles_Nvwu(Roles):
    def __init__(self):
        super().__init__('nvwu', 'shen', 30)
        self.info = {'jie': 1, 'du': 1}

    def applyjie(self):
        flag = 'fail'
        if self.info['jie'] == 1:
            self.info['jie'] = 0
            flag = 'succeed'
        return flag

    def applydu(self):
        flag = 'fail'
        if self.info['du'] == 1:
            self.info['du'] = 0
            flag = 'succeed'
        return flag


class Roles_Yuyanjia(Roles):
    def __init__(self):
        super().__init__('yuyanjia', 'shen', 40)


class Roles_Lieren(Roles):
    def __init__(self):
        super().__init__('lieren', 'shen', -10)

    def passive(self):
        print('haha')


class Roles_Baichi(Roles):
    def __init__(self):
        super().__init__('baichi', 'shen', -10)

    def passive(self):
        print('haha')


class Roles_Lang(Roles):
    def __init__(self):
        super().__init__('lang', 'lang', 20)

    def night(self):
        print('haha')


class Roles_Heilangwang(Roles):
    def __init__(self):
        super().__init__('heilangwang', 'lang', -10)

    def passive(self):
        print('hoho')


class Roles_Bailangwang(Roles):
    def __init__(self):
        super().__init__('bailangwang', 'lang', 100)
        
    def day(self):
        print('xxxx')


class Roles_Cunmin(Roles):
    def __init__(self):
        super().__init__('cunmin', 'min', 0)


class Modes:
    MODE_YNL9 = ['yuyanjia', 'nvwu', 'lieren',
                 'cunmin', 'cunmin', 'cunmin',
                 'lang', 'lang', 'lang']

    MODE_YNLB = ['yuyanjia', 'nvwu', 'lieren', 'baichi',
                 'cunmin', 'cunmin', 'cunmin', 'cunmin',
                 'lang', 'lang', 'lang', 'lang']

    MODE_DICT = {'yuyanjia': Roles_Yuyanjia,
                 'nvwu': Roles_Nvwu,
                 'lieren': Roles_Lieren,
                 'baichi': Roles_Baichi,
                 'cunmin': Roles_Cunmin,
                 'lang': Roles_Lang,
                 'heilangwang': Roles_Heilangwang,
                 'bailangwang': Roles_Bailangwang,
                 'unknown': Roles_Unknown}

    def LC_generate(self, numofplayers):
        numoflang = math.floor(numofplayers/2)
        numofcunmin = numofplayers - numoflang
        rlist = ['lang' for i in range(numoflang)]
        rlist.extend(['cunmin' for j in range(numofcunmin)])
        return rlist

    def get(self, numberofplayers, mode='default'):
        '''
        mode = a list of names
        '''
        if mode == 'MODE_YNLB':
            rlist = self.MODE_YNLB
        elif mode == 'MODE_YNL9':
            rlist = self.MODE_YNL9
        elif isinstance(mode, list):
            rlist = mode
        else:
            rlist = self.LC_generate(numberofplayers)
        if numberofplayers != len(rlist):
            rlist = self.LC_generate(numberofplayers)
        return rlist


class GameStatus:
    def __init__(self, users=None, mode='Default'):
        if isinstance(users, Users):
            self.NumberOfPlayers = users.num
            self.AllUsers = users.copy()
        if isinstance(users, list):
            self.NumberOfPlayers = len(users)
            self.AllUsers = Users(users)
        self.Mode = sorted(Modes().get(self.NumberOfPlayers, mode=mode))

    def initialize(self, changenum=False):
        self.changeroles()
        if changenum is True:
            self.changenums()

    def changeroles(self, shuffle=True):
        roles = self.Mode[:]
        if shuffle is True:
            random.shuffle(roles)
        self.AllUsers.changeroles(roles)

    def changenums(self):
        self.AllUsers.renum()

    def gameindex(self, basedon='playernum'):
        return self.AllUsers.print(basedon=basedon)

    def loads(self, info):
        '''
        info = {dumps}
        '''
        self.NumberOfPlayers = len(info)
        self.Mode = sorted([item['role'] for item in info])
        self.AllUsers.loads(info)

    def dumps(self):
        return self.AllUsers.dumps()

    def pick(self, i):
        return self.AllUsers.pick(i)


#%%
users = Users(['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8', 'i9', '10', '11', '12'])


u=['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8', 'i9', '10', '11', '12']
newgame = GameStatus(users=u, mode='MODE_YNLB')
newgame.initialize(changenum=True)
# newgame.
newgame.gameindex()

#%%

# #%%
# # newgame.roles[0].night()
# # user8.role
# for i in range(1, 10):
#     newgame.startevent(event=EventYuyanjia, relatedusers=[yuyanjianum],
#                        targets=[1, 2, 3, 4, 5, 6, 7, 8, 9],
#                        info={'userindex': newgame.UserIndex,
#                              'roleindex': newgame.RoleIndex,
#                              'users': newgame.AllUsers})
#     newgame.update(users.pick(yuyanjianum).sendmessage(i))

# #%%
# print(newgame.loguserview(cuser=yuyanjianum))
# newgame.printroles()

# #%%
# print(newgame.loguserview(cuser=nvwunum))
# newgame.printroles()
# # newgame.printlog()
# #%%

# newgame.startevent(event=EventPool, relatedusers=[1,2,3,4], targets=[1,2,3])
# newgame.update(users.pick(1).sendmessage(2))

# newgame.update(users.pick(2).sendmessage(1))

# newgame.update(users.pick(3).sendmessage(3))

# newgame.update(users.pick(4).sendmessage(2))


# newgame.loguserview(cuser=1)

# #%%
# with open('data.txt', 'w') as outfile:
#     json.dump(ul.dumps(), outfile)


# # %%
# with open('data.txt', 'r') as readfile:
#     dd = json.load(readfile)
# s = {'header': {'modes': [], 'NumberOfPlayers': 12}, 'status': dd}

# #%%
# newgame.recoverfrom(s)

# #%%
# mm = ['yuyanjia', 'nvwu', 'lang', 'lang', 'cunmin', 'cunmin']
# t = Modes().generate(mm)
# t[0]


# #%%
# users = Users(['a1', 'b2', 'c3', 'd4'])
# uu = users.dumps()
# users.pick(2).setrole('nvwu')
# users.load(uu)
# print(users.print())
