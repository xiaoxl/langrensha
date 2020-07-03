import json
import random
import math


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


class User:
    def __init__(self, username, playernum=0):
        self.name = username
        self.role = 'unknown'
        self.playernum = playernum
        self.status = 'alive'

    def setrole(self, role):
        self.role = role

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


#%%
class Users:
    def __init__(self, listofusernames):
        self.users = list()
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

    def copy(self):
        newusers = Users(self.nameindex().values())
        return newusers

    def print(self, basedon='playernum'):
        rlist = dict()
        if basedon == 'name':
            ulist = self.nameindex()
            for k in sorted(ulist.keys()):
                rlist.update({k: {'playernum': ulist[k].playernum, 'role': ulist[k].role, 'status': ulist[k].status}})
        elif basedon == 'role':
            ulist = self.roleindex()
            for k in sorted(ulist.keys()):
                templist = [{'playernum': t.playernum, 'name': t.name, 'status': t.status} for t in ulist[k]]
                rlist.update({k: templist})
        else:
            ulist = self.numindex()
            for k in sorted(ulist.keys()):
                rlist.update({k: {'name': ulist[k].name, 'role': ulist[k].role, 'status': ulist[k].status}})
        return rlist

    def pick(self, playernum):
        return self.numindex(playernum)


#%%
class Roles:
    def __init__(self, name, faction, timing):
        self.name = name
        self.faction = faction
        self.timing = timing
        self.assigneduser = None

    def night(self, **kwargs):
        pass

    def passive(self, **kwargs):
        pass

    def day(self, **kwargs):
        pass


class Roles_Nvwu(Roles):
    def __init__(self, user):
        super().__init__('nvwu', 'shen', 30)
        self.assigneduser = user
        # self.assigneduser.setrole('nvwu')
        self.jie = 1
        self.du = 1

    # def night(self, *args):
    #     if args is 'yongjie':
    #         self.jie = 0
    #     if args is 'yongdu':
    #         self.du = 0
    #     return {'jie': self.jie, 'du': self.du}


class Roles_Yuyanjia(Roles):
    def __init__(self, user):
        super().__init__('yuyanjia', 'shen', 40)
        self.assigneduser = user
        # self.assigneduser.setrole('yuyanjia')
    # def night(self):
    #     print('haha')


class Roles_Lieren(Roles):
    def __init__(self, user):
        super().__init__('lieren', 'shen', -10)
        self.assigneduser = user
        # self.assigneduser.setrole('lieren')

    def passive(self):
        print('haha')


class Roles_Baichi(Roles):
    def __init__(self, user):
        super().__init__('baichi', 'shen', -10)
        self.assigneduser = user
        # self.assigneduser.setrole('baichi')

    def passive(self):
        print('haha')


class Roles_Lang(Roles):
    def __init__(self, user):
        super().__init__('lang', 'lang', 20)
        self.assigneduser = user
        # self.assigneduser.setrole('lang')

    def night(self):
        print('haha')


class Roles_Cunmin(Roles):
    def __init__(self, user):
        super().__init__('cunmin', 'min', 0)
        self.assigneduser = user
        # self.assigneduser.setrole('cunmin')


class Modes:
    MODE_YNL9 = [Roles_Yuyanjia, Roles_Nvwu, Roles_Lieren,
                 Roles_Cunmin, Roles_Cunmin, Roles_Cunmin,
                 Roles_Lang, Roles_Lang, Roles_Lang]

    MODE_YNLB = [Roles_Yuyanjia, Roles_Nvwu, Roles_Lieren, Roles_Baichi,
                 Roles_Cunmin, Roles_Cunmin, Roles_Cunmin, Roles_Cunmin,
                 Roles_Lang, Roles_Lang, Roles_Lang, Roles_Lang]

    MODE_DICT = {'yuyanjia': Roles_Yuyanjia,
                 'nvwu': Roles_Nvwu,
                 'lieren': Roles_Lieren,
                 'baichi': Roles_Baichi,
                 'cunmin': Roles_Cunmin,
                 'lang': Roles_Lieren}

    # MODE_DEFAULT = MODE_YNL9

    def LC_generate(self, numofplayers):
        numoflang = math.floor(numofplayers/2)
        numofcunmin = numofplayers - numoflang
        rlist = [Roles_Lang for i in range(numoflang)]
        rlist.extend([Roles_Cunmin for j in range(numofcunmin)])
        return rlist

    def get(self, numberofplayers, mode='Default'):
        if mode == 'MODE_YNLB':
            rlist = self.MODE_YNLB
        elif mode == 'MODE_YNL9':
            rlist = self.MODE_YNL9
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
        self.Mode = Modes().get(self.NumberOfPlayers, mode=mode)
        self.Roles = list()

    def initialize(self, changenum=False):
        self.changeroles()
        if changenum is True:
            self.changenums()

    def changeroles(self):
        self.Roles = list()
        self.RoleIndex = dict()
        self.UserIndex = dict()
        tempuser = list(range(1, self.NumberOfPlayers+1))
        random.shuffle(tempuser)
        for i in range(self.NumberOfPlayers):
            self.Roles.append(self.Mode[i](self.AllUsers.pick(tempuser[i])))
            self.Roles[-1].assigneduser.setrole(self.Roles[-1].name)

    def changenums(self):
        self.AllUsers.renum()

    def gameindex(self, basedon='playernum'):
        return self.AllUsers.print(basedon=basedon)

    def recoverfrom(self, gindex):
        '''
        gindex has to be the exact format as in gameindex()
        '''
        pnums = [item['playernum'] for item in gindex]
        unames = [item['username'] for item in gindex]
        roles = [item['role'] for item in gindex]
        ustatus = [item['playernum'] for item in gindex]
        self.AllUsers = Users(unames)
        for index, player in enumerate(self.AllUsers):
            player.setnumber(pnums[index])
            player.setstatus(ustatus[index])
        





#%%
users = Users(['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8', 'i9', '10', '11', '12'])


u=['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8', 'i9', '10', '11', '12']
newgame = GameStatus(users=u, mode='MODE_YNLB')
newgame.initialize(changenum=False)
newgame.gameindex(basedon='role')

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

#%%
with open('data.txt', 'w') as outfile:
    json.dump(newgame.gameindex(), outfile)


# %%
with open('data.txt', 'r') as readfile:
    dd = json.load(readfile)