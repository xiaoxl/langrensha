import json
import random


#%%
def maxoflist(alist):
    m = max(alist)
    return [i for i, j in enumerate(alist) if j == m]


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
    '''
    playernum is the most important identifier.
    '''
    def __init__(self, username, playernum=0):
        self.name = username
        self.role = 'unknown'
        self.playernum = playernum

    def setrole(self, role):
        self.role = role

    def setnumber(self, num):
        self.playernum = num

    def sendmessage(self, target, texttype='default', auth=None):
        return LRSMessage(sender=self.playernum, receiver=0,
                          target=target, texttype=texttype, auth=auth)

    def notifymessage(self, target, texttype='default', auth=None):
        return LRSMessage(sender=0, receiver=self.playernum,
                          target=target, texttype=texttype, auth=auth)


class Event:
    def __init__(self, relatedusers, targets=list(), info=None):
        self.__relatedusers = relatedusers[:]
        self.__pool = {'A': list()}
        self.__targets = targets
        self.status = 'Active'
        self.__info = info
        self.result = ['A']
        self.__log = list()

    def start(self):
        pass

    def update(self, message):
        sender = message.sender
        if sender in self.__relatedusers:
            self.__relatedusers.remove(sender)
            self.type = message.texttype
            if message.target in self.__targets:
                if message.target in self.__pool.keys():
                    self.__pool[message.target].append(message.sender)
                else:
                    self.__pool.update({message.target: [message.sender]})
            else:
                self.__pool['A'].append(message.sender)
        if len(self.__relatedusers) == 0:
            self.end()

    def end(self):
        self.status = 'End'
        pool = [len(p) for p in list(self.__pool.values())]
        max = maxoflist(pool)
        self.result = list()
        for index in max:
            self.result.append(list(self.__pool.keys())[index])
        if 'A' in self.result:
            self.result.remove('A')

    def getpool(self):
        return self.__pool

    def getlog(self):
        return self.__log


class EventEvenRandom(Event):
    def __init__(self, relatedusers, targets=list(), texttype='default'):
        super().__init__(relatedusers, targets, texttype)

    def end(self):
        super().end()
        if len(self.result) > 0:
            self.result = random.choices(self.result)


class EventNvwu(Event):
    '''
    __info = {'nvwu': user, 'daokou': playernum}
    '''
    # def __init__(self, relatedusers, external, targets=list(), texttype='default'):
    #     super().__init__(relatedusers=relatedusers, external=external,
    #                      targets=targets, texttype=texttype)

    def start(self):
        if 'nvwu' in self.__info.keys():
            self.__info['nvwu'].notifymessage(self.__info['daokou'],
                                              texttype='nvwuyandaokou')          

    def end(self):
        super().end()
        if len(self.result) > 0:
            self.result = random.choices(self.result)


class EventYuyanjia(Event):
    '''
    __info = {'yuyanjia': user}
    '''
    def end(self):
        super().end()
        if len(self.result) > 0:
            print(users[self.result[0]].role)
            

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

    # def night(self):
    #     print('haha')


class Roles_Lieren(Roles):
    def __init__(self, user):
        super().__init__('lieren', 'shen', -10)
        self.assigneduser = user

    def passive(self):
        print('haha')


class Roles_Baichi(Roles):
    def __init__(self, user):
        super().__init__('baichi', 'shen', -10)
        self.assigneduser = user

    def passive(self):
        print('haha')


class Roles_Lang(Roles):
    def __init__(self, user):
        super().__init__('lang', 'lang', 20)
        self.assigneduser = user

    def night(self):
        print('haha')


class Roles_Cunmin(Roles):
    def __init__(self, user):
        super().__init__('cunmin', 'min', 0)
        self.assigneduser = user


class Modes:
    MODE_YNL9 = [Roles_Yuyanjia, Roles_Nvwu, Roles_Lieren, 
                 Roles_Cunmin, Roles_Cunmin, Roles_Cunmin, 
                 Roles_Lang, Roles_Lang, Roles_Lang]

    MODE_YNLB = [Roles_Yuyanjia, Roles_Nvwu, Roles_Lieren, Roles_Baichi,
                 Roles_Cunmin, Roles_Cunmin, Roles_Cunmin, Roles_Cunmin,
                 Roles_Lang, Roles_Lang, Roles_Lang, Roles_Lang]

    Mode_Default = MODE_YNL9


#%%
class GameStatus:
    def __init__(self, user=list(), modes=Modes.Mode_Default):
        self.Modes = modes
        self.NUMBEROFPLAYERS = len(user)
        self.allusers = user
        self.roles = list()
        self.log = list()
        self.events = [Event]
        tempuser = self.allusers[:]
        random.shuffle(tempuser)
        for i, p in enumerate(tempuser):
            self.roles.append(modes[i](p))
        self.roleindex = {}
        for i in self.roles:
            i.assigneduser.setrole(i.name)
            if i.name in self.roleindex.keys():
                temlist = self.roleindex[i.name]
                temlist.append(i.assigneduser)
                self.roleindex.update({i.name: temlist})
            else:
                self.roleindex.update({i.name: [i.assigneduser]})

    def changeroles(self):
        tempuser = self.allusers[:]
        random.shuffle(tempuser)
        for i, p in enumerate(tempuser):
            self.roles.append(self.Modes[i](p))

    def printroles(self):
        for r in list(self.roleindex.keys()):
            for u in self.roleindex[r]:
                print(r + ': ' + u.name)

    def printlog(self):
        for item in self.log:
            print(item)
            print('\n')


new = Event(relatedusers=[1, 2, 3], targets=[1, 2])

user1 = User(username='a1', playernum=1)
user2 = User(username='b2', playernum=2)
user3 = User(username='c3', playernum=3)
user4 = User(username='d4', playernum=4)
user5 = User(username='e5', playernum=5)
user6 = User(username='f6', playernum=6)
user7 = User(username='g7', playernum=7)
user8 = User(username='h8', playernum=8)
user9 = User(username='i9', playernum=9)

user8.role


#%%
users = [user1, user2, user3, user4, user5, user6, user7, user8, user9]

newgame = GameStatus(users)
newgame.printroles()

newgame.roles[0].night()
user8.role

newgame.printlog()
#%%
new.update(user1.sendmessage(1))
print(new.getpool())
#%%
new.update(user1.sendmessage(2))
print(new.getpool())
new.update(user2.sendmessage(1))
print(new.getpool())
new.update(user3.sendmessage(3))
print(new.getpool())
print(new.result)


#%%
# y = EventYuyanjia(relatedusers=[1], targets=[0,1,2,3,4,5,6,7,8])
for i in range(9):
    y = EventYuyanjia(relatedusers=[1], targets=[0,1,2,3,4,5,6,7,8]).update(user1.sendmessage(i))
newgame.printroles()

# %%
