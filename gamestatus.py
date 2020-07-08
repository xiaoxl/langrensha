# %%
import json
import random
import math


# def maxoflist(alist):
#     m = max(alist)
#     return [i for i, j in enumerate(alist) if j == m]


class LogMessage:
    def __init__(self, sender=list(), receiver=list(), info=dict(), auth=None):
        self.sender = sender
        self.receiver = receiver
        self.info = info
        self.auth = auth

    def todict(self):
        return {'sender': self.sender,
                'receiver': self.receiver,
                'info': self.info,
                'auth': self.auth}


# %%
class LRSMessage:
    '''
    target, sender, receiver are all playernums. 0 means system.
    The target can represent some other meaning like nvwu.
    '''
    def __init__(self, sender=0, receiver=0,
                 target=0, texttype='default', auth=None, info=dict()):
        self.sender = sender
        self.receiver = receiver
        self.target = target
        self.texttype = texttype
        self.auth = auth
        self.info = info

    def todict(self):
        return {'sender': self.sender,
                'receiver': self.receiver,
                'target': self.target,
                'texttype': self.texttype,
                'auth': self.auth,
                'info': self.info}


# %%
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


# %%
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

    def factionindex(self, count=True, alive=True):
        fdict = dict()
        for player in self.users:
            fname = player.roleClass.faction
            if fname not in fdict.keys():
                fdict.update({fname: list()})
            if alive is True:
                if player.status == 'alive':
                    fdict[fname].append(player.playernum)
            else:
                fdict[fname].append(player.playernum)
        if count is False:
            result = fdict
        else:
            result = dict()
            for item in fdict.keys():
                result.update({item: len(fdict[item])})
        return result

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

    def getalive(self):
        return [i.playernum for i in self.statusindex()['alive']]

    def dumps(self):
        return [item.dumps() for item in self.users]

    def loads(self, data):
        self.num = len(data)
        self.users = list()
        for index in range(self.num):
            temp = User(' ')
            temp.loads(data[index])
            self.users.append(temp)


# %%
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


class Roles_Shouwei(Roles):
    def __init__(self):
        super().__init__('shouwei', 'shen', 10)


class Roles_Heilangwang(Roles):
    def __init__(self):
        super().__init__('heilangwang', 'lang', -10)

    def passive(self):
        print('hoho')


class Roles_Bailangwang(Roles):
    def __init__(self):
        super().__init__('bailangwang', 'lang', -20)

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
                 'shouwei': Roles_Shouwei,
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

    def nightflow(self, listofroles):
        rdict = {self.MODE_DICT[item]().timing: self.MODE_DICT[item]().name for item in listofroles if self.MODE_DICT[item]().timing > 0}
        return [rdict[i] for i in sorted(rdict.keys())]


# %%
class GameStatus:
    def __init__(self, users=None, mode='Default'):
        if isinstance(users, Users):
            self.NumberOfPlayers = users.num
            self.AllUsers = users.copy()
        elif isinstance(users, list):
            self.NumberOfPlayers = len(users)
            self.AllUsers = Users(users)
        else:
            self.NumberOfPlayers = 0
            self.AllUsers = Users()
        self.Mode = sorted(Modes().get(self.NumberOfPlayers, mode=mode))
        self.captain = 0
        self.round = 1

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

    def setcaptain(self, playernum):
        self.captain = playernum

    def loads(self, info):
        '''
        info = {dumps}
        '''
        gamestatus = info['gamestatus']
        self.NumberOfPlayers = len(gamestatus)
        self.Mode = sorted([item['role'] for item in gamestatus])
        self.AllUsers.loads(gamestatus)
        self.captain = info['captain']
        self.round = info['round']

    def dumps(self):
        info = {'gamestatus': self.AllUsers.dumps(),
                'captain': self.captain,
                'round': self.round}
        return info

    def pick(self, i):
        return self.AllUsers.pick(i)

    def getalive(self):
        return self.AllUsers.getalive()

    def factionindex(self, count=True):
        return self.AllUsers.factionindex(count)

    def dump(self, filename='default.sav'):
        with open(filename, 'w') as outfile:
            json.dump(self.dumps(), outfile)

    def load(self, filename='default.sav'):
        with open(filename, 'r') as readfile:
            self.loads(json.load(readfile))


# %%
class Event:
    '''
    All playernums are real playernums, not list index in python.
    All numbers are in relatedusers, targets, and info
    info = {..., round=current round and timing}
    all logs are written in children classes

    binded with gamestatus
    '''
    def __init__(self):
        self.status = 'Active'
        self._pool = {'A': list()}
        self.result = ['A']
        self._info = dict()
        self._log = list()
        self._gamestatus = None

    def initialize(self, gamestatus=None, info=None):
        self.name = 'basic'
        self._gamestatus = gamestatus
        self._relatedusers = list()
        self._targets = list()
        self._info = info
        # relatedusers and targets are initialized in childeren classes

    def blindrun(self):
        # if all relatedusers are dead, do something
        pass

    def update(self, message):
        '''
        message = {sender, receiver, target, texttype, auth}
        '''
        sender = message.sender
        if sender in self._relatedusers:
            self._relatedusers.remove(sender)
            self.vote(message.sender, message.target)
        if len(self._relatedusers) == 0:
            self.end()

    def vote(self, sender, target):
        if target in self._targets:
            if target in self._pool.keys():
                self._pool[target].append(sender)
            else:
                self._pool.update({target: [sender]})
        else:
            self._pool['A'].append(sender)

    def countvote(self, captain=True, tiebreak='pk'):
        pool = {item: 0 for item in self._gamestatus.getalive()}
        for i in self._pool.keys():
            if i != 'A':
                pool[i] = len(self._pool[i])
                if captain is True:
                    if self._gamestatus.captain in self._pool[i]:
                        pool.update({i: pool[i]+0.5})
        maxvalue = max(pool.values())
        result = [i for i in pool.keys() if pool[i] == maxvalue]
        if tiebreak == 'random':
            if len(result) > 1:
                result = random.choices(result)
        self.result = result
        return result

    def end(self):
        self.status = 'End'
        self.countvote(captain=True, tiebreak='pk')

    def getpool(self):
        return self._pool

    def getlog(self):
        return self._log


class EventLang(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'lang'
        self._info = info
        alllang = gamestatus.factionindex(count=False)['lang'][:]
        self._relatedusers = [i for i in alllang if gamestatus.pick(i).status == 'alive']
        self._targets = gamestatus.getalive()[:]

    def start(self):
        print(self.name)
        print('alive: ')
        print(self._targets)
        print('\n')

    def end(self):
        self.status = 'End'
        if set(self._pool.keys()) - set('A') != set():
            self.countvote(captain=False, tiebreak='random')
            self._log.append(LogMessage([0], [0],
                                        info={'Pool': self._pool,
                                              'result': self.result},
                                        auth=[-1]))
            self._gamestatus.pick(self.result[0]).setstatus('murdered')
            self._info.append({'type': 'langdao', 'target': self.result[0],
                               'round': self._gamestatus.round})


class EventPool(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'toupiao'
        self._info = info
        self._relatedusers = gamestatus.getalive()[:]
        self._targets = gamestatus.getalive()[:]

    def start(self):
        print(self.name)
        print('alive: ')
        print(self._relatedusers)
        print('\n')

    def end(self):
        self.status = 'End'
        self.countvote(captain=True, tiebreak='pk')
        self._log.append(LogMessage([0], [0],
                                    info={'Pool': self._pool,
                                          'result': self.result},
                                    auth=[-1]))
        if len(self.result) == 1:
            self._gamestatus.pick(self.result[0]).setstatus('banished')
            self._info = None
        elif len(self.result) > 1:
            self._info.append({'type': 'pk', 'info': self.result})


class EventPoolPk(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'pktoupiao'
        self._info = info
        self._targets = info[-1]['info'][:]
        self._relatedusers = list(set(gamestatus.getalive())-set(self._targets))
        if self._relatedusers == list():
            self._pool = dict()
            self.end()

    def start(self):
        print(self.name)
        print('pk: ')
        print(self._targets)
        print('dd')
        print(self._relatedusers)
        print('\n')

    def end(self):
        self.status = 'End'
        self.countvote(captain=True, tiebreak='pk')
        self._log.append(LogMessage([0], [0],
                                    info={'Pool': self._pool,
                                          'result': self.result},
                                    auth=[-1]))
        if len(self.result) == 1:
            self._gamestatus.pick(self.result[0]).setstatus('banished')
            self._info.append({'type': 'pkgood', 'info': self.result[0]})
        elif len(self.result) > 1:
            self._info.append({'type': 'pkfail', 'info': None})


class EventNvwu(Event):
    '''
    _info = {'nvwu': user, 'daokou': playernum}
    '''
    def start(self):
        if 'nvwu' in self._info.keys():
            self._info['nvwu'].notifymessage(self._info['daokou'],
                                             texttype='nvwuyandaokou')

    def end(self):
        super().end()
        if len(self.result) > 0:
            self.result = random.choices(self.result)


class EventYuyanjia(Event):
    '''
    _info = {'yuyanjia': user, 'users': users}
    '''
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'yuyanjiayanren'
        self._info = None
        self._relatedusers = [gamestatus.gameindex(basedon='role')['yuyanjia'][0]['playernum']]
        self._targets = gamestatus.getalive()[:]

    def start(self):
        print('alive yanren')
        print(self._gamestatus.getalive())

    def end(self):
        super().end()
        # userindex = self._info['userindex']
        # roleindex = self._info['roleindex']
        # users = self._info['users']
        ynum = self._gamestatus.gameindex(basedon='role')['yuyanjia'][0]['playernum']
        if len(self.result) > 0:
            result = self._gamestatus.pick(self.result[0]).role
            msg = LogMessage(sender=[ynum], receiver=[0],
                             info={'type': 'yuyanjiayanren',
                                   'target': self.result[0],
                                   'result': result}, auth=[ynum])
            self._log.append(msg)
            print(str(self.result[0])+': '+result)


# %%
class flowchart:

    EVENT_DICT = {'default': Event,
                  'yuyanjia': EventYuyanjia,
                  'nvwu': EventNvwu,
                  'pool': EventPool,
                  'poolpk': EventPoolPk,
                  'lang': EventLang}

    def __init__(self):
        self._status = 'Not Running'
        self.log = list()
        self.cevent = None
        self.cache = list()
        self.gamestatus = GameStatus()

    def initialize(self, users=list(), mode='default',
                   beginningevents=list(), settings={'changenum': False}):
        self.gamestatus = GameStatus(users=users, mode=mode)
        self.gamestatus.initialize(changenum=settings['changenum'])
        self.events = beginningevents[:]
        # self.currentstatus = self.gamestatus.gameindex()
        self._status = 'Running'
        self.nextevent()

    def insertevent(self, eventname, place=0):
        if place == -1:
            self.events.append(eventname)
        else:
            self.events.insert(place, eventname)

    def nextevent(self):
        # flowchart is controlled here
        self.startevent(self.events.pop(0))

    def startevent(self, eventname, info=None):
        '''
        info = {previous result}
        '''
        # start a new event
        if info is None:
            info = self.cache
        if eventname in self.EVENT_DICT.keys():
            self.cevent = self.EVENT_DICT[eventname]()
            self.cevent.initialize(gamestatus=self.gamestatus, info=info)
            self.cevent.start()

    def update(self, message):
        # update only if the game is on.
        if self._status == 'Running':
            if message.texttype == 'cmd-endgame':
                self.end()
            else:
                # when get a new message, call the update function from event
                self.cevent.update(message)
                # if the event ends by the update, it will call event.end()
                # automatically, and make event.status = 'End'.
                if self.cevent.status == 'End':
                    self.endevent()
                # if the event ends, call the endevent function in the flowchart.
        else:
            if message.texttype == 'cmd-newgame':
                # in this case message.info contains:
                # info = {[usernames], mode, [beginningevents], 'setings'={}}
                self._status = 'Running'
                self.initialize(users=message.info['usernames'],
                                mode=message.info['mode'],
                                beginningevents=message.info['beginningevents'],
                                settings=message.info['settings'])
                self.nextevent()

    def endevent(self):
        # first log all results and modify the status.
        self.log.extend(self.cevent.getlog())
        print(self.cevent.getpool())
        self.modifygamestatus()
        # check whether the game ends.
        if self.checkendcondition()['end']:
            self.end()
        else:
            if len(self.cache) > 0:
                if 'pk' == self.cache[-1]['type']:
                    self.insertevent('poolpk')
            # if the game doesn't end, start the next event.
            if self.events == list():
                self.events.append('pool')
            self.startevent(self.events.pop(0))

    def checkendcondition(self):
        faction = self.gamestatus.factionindex()
        if 0 in faction.values():
            if faction['lang'] == 0:
                result = {'end': True, 'winner': 'haoren'}
            else:
                result = {'end': True, 'winner': 'lang'}
            print(result)
        else:
            result = {'end': False, 'winner': None}
        return result

    def modifygamestatus(self):
        pass

    def end(self):
        self._status = 'Not Running'
        print('the end!')

    def loguserview(self, cuser=0):
        clog = list()
        for item in self.log:
            if cuser == 0 or cuser in item.auth or -1 in item.auth:
                clog.append(item.info)
        return clog

    def printlog(self):
        for item in self.log:
            print(item.todict())
            print('\n')

    def console(self, sender, target):
        self.update(LRSMessage(sender=sender, receiver=0,
                               target=target, auth=[sender]))

# %%
# if __name__ == '__main__':
u = ['a1', 'b2', 'c3', 'd4']
# newgame = GameStatus(users=u, mode='MODE_YNLB')
# newgame.initialize(changenum=True)
# newgame.gameindex()

# %%
# newgame.dump()
# %%
# new = GameStatus()
# new.load()

# %%
# users = Users(['a1', 'b2', 'c3', 'd4', 'e5', 'f6',
#                'g7', 'h8', 'i9', '10', '11', '12'])

# newgame = GameStatus(users=users, mode='MODE_YNLB')
# newgame.initialize()
# newgame.gameindex()

CMDNEWGAME = LRSMessage(sender=0, receiver=0, target=0, texttype='cmd-newgame',
                        info={'usernames': u,
                              'mode': 'MODE_YNLB',
                              'beginningevents': ['pool', 'pool', 'pool'],
                              'settings': {'changenum': False}})

CMDENDGAME = LRSMessage(sender=0, receiver=0, target=0,
                        texttype='cmd-endgame', info=dict())

# %%
f = flowchart()
f.initialize(users=['1', '2', '3', '4', '5', '6', '7', '8', '9'], mode='MODE_YNL9', beginningevents=['lang'])

#%%
f.gamestatus.captain = 4

f.console(1,0)
f.console(2,0)
f.console(3,0)
f.console(4,4)
f.console(5,0)
f.console(6,6)
f.console(7,0)
f.console(8,0)
f.console(9,0)
# %%
f.gamestatus.gameindex()

# %%
f.gamestatus.factionindex()

# %%
f.console(2,3)