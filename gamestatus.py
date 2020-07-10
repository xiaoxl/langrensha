# -*-coding: utf-8 -*-
# %%
import json
import random
import math


DEBUGMODE = True


class GameTime:
    def __init__(self):
        self.night = 1
        self.day = 0
        self.current = 'Night'

    def next(self):
        if self.night > self.day:
            self.day = self.day + 1
            self.current = 'Day'
        else:
            self.night = self.night + 1
            self.current = 'Night'

    def dumps(self):
        return self.current + ' ' + str(max(self.night, self.day))

    def loads(self, text):
        textlist = text.split(' ')
        self.current = textlist[0]
        num = int(textlist[1])
        if self.current == 'Night':
            self.night = num
            self.day = num - 1
        elif self.current == 'Day':
            self.night = num
            self.day = num
        else:
            pass


class LogMessage:
    def __init__(self, sender=list(), receiver=list(), info=dict(),
                 auth=None, logable=True):
        self.sender = sender
        self.receiver = receiver
        self.info = info
        self.auth = auth
        self.logable = logable

    def todict(self):
        return {'sender': self.sender,
                'receiver': self.receiver,
                'info': self.info,
                'auth': self.auth,
                'logable': self.logable}


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
        nlist = [i.playernum for i in self.statusindex()['alive']]
        if 'baichi' in self.statusindex().keys():
            nlist.extend([i.playernum for i in self.statusindex()['baichi']])
        return nlist

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
        self.printname = ''

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
        self.printname = '女巫'

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
        self.printname = '预言家'


class Roles_Lieren(Roles):
    def __init__(self):
        super().__init__('lieren', 'shen', -10)
        self.printname = '猎人'

    def passive(self):
        print('haha')


class Roles_Baichi(Roles):
    def __init__(self):
        super().__init__('baichi', 'shen', -10)
        self.printname = '白痴'

    def passive(self):
        print('haha')


class Roles_Lang(Roles):
    def __init__(self):
        super().__init__('lang', 'lang', 20)
        self.printname = '狼'

    def night(self):
        print('haha')


class Roles_Shouwei(Roles):
    def __init__(self):
        super().__init__('shouwei', 'shen', 10)
        self.printname = '守卫'


class Roles_Heilangwang(Roles):
    def __init__(self):
        super().__init__('heilangwang', 'lang', -10)
        self.printname = '黑狼王'

    def passive(self):
        print('hoho')


class Roles_Bailangwang(Roles):
    def __init__(self):
        super().__init__('bailangwang', 'lang', -20)
        self.printname = '白狼王'

    def day(self):
        print('xxxx')


class Roles_Cunmin(Roles):
    def __init__(self):
        super().__init__('cunmin', 'min', 0)
        self.printname = '村民'


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

    def LNC_generate(self, numofplayers):
        rlist = list()
        if numofplayers <= 1:
            rlist = self.LC_generate(numofplayers)
        else:
            numofcunmin = numofplayers - 2
            rlist = ['cunmin' for j in range(numofcunmin)]
            rlist.extend(['lang', 'nvwu'])
        return rlist

    def get(self, numberofplayers, mode='default'):
        '''
        mode = a list of names
        '''
        if mode == 'MODE_YNLB':
            rlist = self.MODE_YNLB
        elif mode == 'MODE_YNL9':
            rlist = self.MODE_YNL9
        elif mode == 'MODE_TESTLN':
            rlist = self.LNC_generate(numberofplayers)
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
        self.round = GameTime()

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
        self.round.loads(info['round'])

    def dumps(self):
        info = {'gamestatus': self.AllUsers.dumps(),
                'captain': self.captain,
                'round': self.round.dumps()}
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
        self._debugmode = DEBUGMODE

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

    def start(self):
        self.end()

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

    def getlog(self, outputtype='str', clear=True):
        output = list()
        if outputtype == 'str':
            for item in self._log:
                output.append(LogMessage(info=self.render(item.info),
                                         auth=item.auth, logable=item.logable))
        if clear is True:
            self._log = list()
        return output

    def generatelog(self, info, auth=None, logable=True):
        if self._debugmode is True:
            print(self.render(info))
        self._log.append(LogMessage(sender=[0], receiver=[0], info=info,
                                    auth=auth, logable=logable))

    def render(self, textinfo=list(), outputtype='str'):
        text = ''
        if outputtype == 'str':
            for item in textinfo:
                if isinstance(item, str):
                    text = text + item
                elif isinstance(item, list):
                    text = text + ', '.join([str(j) for j in item])
                elif isinstance(item, dict):
                    # pool = {'A': [], 1: []}
                    for j in item.keys():
                        text = text + str(j) + ': ' + ', '.join([str(c) for c in item[j]]) + '\n'
                else:
                    text = text + str(item)
        return text


class EventLang(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'lang'
        self._info = info
        self._cahce = info
        self._alllang = gamestatus.factionindex(count=False)['lang'][:]
        self._relatedusers = [i for i in self._alllang if gamestatus.pick(i).status == 'alive']
        self._alllangalive = self._relatedusers[:]
        self._targets = gamestatus.getalive()[:]

    def start(self):
        self.generatelog(info=['狼人请刀人。目标范围: ',
                               self._targets],
                         auth=self._relatedusers[:],
                         logable=False)

    def end(self):
        self.status = 'End'
        if set(self._pool.keys()) - set('A') != set():
            self.countvote(captain=False, tiebreak='random')
            self.generatelog(info=['狼人已刀人: ',
                                   self.result[0]],
                             auth=self._alllang[:])
            self._info[self._gamestatus.round.dumps()].update({'langdao': self.result[0]})


class EventPool(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'toupiao'
        self._info = info
        self._cahce = info
        self._relatedusers = gamestatus.getalive()[:]
        self._targets = gamestatus.getalive()[:]

    def start(self):
        self.generatelog(info=['现在开始投票。活人: ',
                               self._relatedusers[:]],
                         auth=[-1], logable=False)

    def end(self):
        self.status = 'End'
        self.countvote(captain=True, tiebreak='pk')
        if len(self.result) == 1:
            self.generatelog(info=['投票结束。被放逐的玩家是: ',
                                   self.result,
                                   '\n票型: \n',
                                   self._pool],
                             auth=[-1], logable=True)
            self._gamestatus.pick(self.result[0]).setstatus('banished')
            self._info = None
        elif len(self.result) > 1:
            self.generatelog(info=['投票结束。平票。上pk台的玩家是: ',
                                   self.result,
                                   '\n票型: \n',
                                   self._pool],
                             auth=[-1], logable=True)
            self._info[self._gamestatus.round.dumps()].update({'pk': self.result})


class EventPoolPk(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'pktoupiao'
        self._info = info
        self._cahce = info
        self._targets = info[self._gamestatus.round.dumps()]['pk']
        self._relatedusers = list(set(gamestatus.getalive())-set(self._targets))
        if self._relatedusers == list():
            self._pool = dict()
            self.end()

    def start(self):
        self.generatelog(info=['pk投票。pk的玩家是: ',
                               self._targets,
                               '\n可以投票的玩家有: ',
                               self._relatedusers], auth=[-1], logable=True)

    def end(self):
        self.status = 'End'
        self.countvote(captain=True, tiebreak='pk')
        if len(self.result) == 1:
            self.generatelog(info=['投票结束。被放逐的玩家是: ',
                                   self.result,
                                   '\n票型: ',
                                   self._pool], auth=[-1], logable=True)
            self._gamestatus.pick(self.result[0]).setstatus('banished')
            self._info[self._gamestatus.round.dumps()].update({'work': self.result[0]})
        elif len(self.result) > 1:
            self.generatelog(info=['继续平票。无人被流放。'], auth=[-1], logable=True)
            self._info[self._gamestatus.round.dumps()].update({'fail': None})


class EventNvwu(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'nvwu'
        self._info = info
        self._cahce = info
        self._relatedusers = [gamestatus.gameindex(basedon='role')['nvwu'][0]['playernum']]
        self._nvwunum = self._relatedusers[0]
        self._targets = gamestatus.getalive()[:]
        self._nvwujineng = self._gamestatus.pick(self._nvwunum).roleClass.info.copy()

    def start(self):
        info = self._info[self._gamestatus.round.dumps()]
        if self._gamestatus.pick(self._nvwunum).roleClass.info == {'jie': 0, 'du': 0}:
            self.generatelog(info=['女巫无技能'], auth=self._relatedusers[:], logable=False)
            self.end()
        else:
            self.generatelog(info=['女巫操作: '],
                             auth=self._relatedusers[:], logable=False)
            if self._nvwujineng['jie'] == 1:
                if 'langdao' in info.keys():
                    self.generatelog(info=['狼刀: ',
                                           info['langdao'],
                                           '。如果想救人请输入-1'],
                                     auth=self._relatedusers[:],
                                     logable=False)
                else:
                    self.generatelog(info=['狼空刀。'],
                                     auth=self._relatedusers[:],
                                     logable=False)
            if self._nvwujineng['du'] == 1:
                self.generatelog(info=['你有一瓶毒药。活人: ',
                                       self._gamestatus.getalive(),
                                       '。如果想毒人请直接输入玩家号码。'],
                                 auth=self._relatedusers[:],
                                 logable=False)

    def update(self, message):
        '''
        message = {sender, receiver, target, texttype, auth}
        '''
        sender = message.sender
        if sender in self._relatedusers:
            self._relatedusers.remove(sender)
            target = message.target
            if target == -1 and self._nvwujineng['jie'] == 1:
                # save
                try2save = self._gamestatus.pick(self._nvwunum).roleClass.applyjie()
                if try2save == 'succeed':
                    self.generatelog(info=['女巫出手救人。'],
                                     auth=[self._nvwunum],
                                     logable=True)
                    self._info[self._gamestatus.round.dumps()].update({'nvwujiu': None})
            elif target in self._targets and self._nvwujineng['du'] == 1:
                # du
                try2poison = self._gamestatus.pick(self._nvwunum).roleClass.applydu()
                if try2poison == 'succeed':
                    self.generatelog(info=['女巫出手毒人: ',
                                           target],
                                     auth=[self._nvwunum],
                                     logable=True)
                    self._info[self._gamestatus.round.dumps()].update({'nvwudu': target})
            else:
                # nothing
                self.generatelog(info=['女巫什么都没做'], auth=[self._nvwunum], logable=True)
        if len(self._relatedusers) == 0:
            self.end()

    def end(self):
        self.status = 'End'


class EventNightends(Event):
    def initialize(self, gamestatus, info):
        super().initialize(gamestatus)
        self.name = 'nightends'
        self._info = info[self._gamestatus.round.dumps()]
        self._cache = info
        # self.end()

    def end(self):
        self.status = 'End'
        dead = list()
        if 'langdao' in self._info.keys():
            if 'nvwujiu' not in self._info.keys():
                dead.append(self._info['langdao'])
        if 'nvwudu' in self._info.keys():
            if self._info['nvwudu'] not in dead:
                dead.append(self._info['nvwudu'])
        if len(dead) == 0:
            self.generatelog(info=['昨晚是平安夜。'],
                             auth=[-1], logable=True)
        else:
            self.generatelog(info=['昨晚死了', len(dead), '个人: ', dead],
                             auth=[-1], logable=True)
        for p in dead:
            self._gamestatus.pick(p).setstatus('dead')
        self._gamestatus.round.next()
        self._cache.update({self._gamestatus.round.dumps(): dict()})


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
                  'lang': EventLang,
                  'nightends': EventNightends}

    def __init__(self):
        self._status = 'Not Running'
        self.log = list()
        self.cevent = None
        self.gamestatus = GameStatus()
        self.cache = {self.gamestatus.round.dumps(): dict()}

    def initialize(self, users=list(), mode='default',
                   beginningevents=list(), settings={'changenum': False}):
        self.gamestatus = GameStatus(users=users, mode=mode)
        self.gamestatus.initialize(changenum=settings['changenum'])
        self.events = beginningevents
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
        # if len(self.cache) > 0:
        #     if 'pk' in self.cache[self.gamestatus.round.dumps()].keys():
        #         self.insertevent('poolpk')
        #     # if the game doesn't end, start the next event.
        if self.events == list():
            self.events.append('pool')
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
            self.log.extend(self.cevent.getlog(clear=True))
            if self.cevent.status == 'End':
                self.endevent()

    def update(self, message):
        # update only if the game is on.
        if self._status == 'Running':
            self.cevent.update(message)
            if self.cevent.status == 'End':
                self.endevent()

    def endevent(self):
        # first log all results and modify the status.
        self.log.extend(self.cevent.getlog())
        if self.checkendcondition()['end']:
            self.end()
        else:
            self.nextevent()

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

    def end(self):
        self._status = 'Not Running'
        print('the end!')

    def loguserview(self, cuser=0):
        clog = list()
        for item in self.log:
            if cuser == 0 or cuser in item.auth or -1 in item.auth:
                clog.append(item.info)
        return clog

    def printlog(self, alllog=True):
        for item in self.log:
            if alllog is True or item.logable is True:
                print(item.todict())

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



# %%
f = flowchart()
f.initialize(users=['1', '2', '3', '4', '5', '6', '7', '8', '9'], mode='MODE_TESTLN', beginningevents=['lang', 'nvwu', 'nightends', 'lang', 'nvwu', 'nightends', 'lang', 'nvwu', 'nightends', 'lang', 'nvwu', 'nightends'])

f.gamestatus.gameindex()

#%%
f.gamestatus.captain = 4

# %%
f.console(1,2)

# %%
f.console(2,3)

# %%
f.console(3,3)

# %%
f.console(4,2)
# %%
f.console(5,-1)
# %%
f.console(6,3)
# %%
f.console(7,1)
# %%
f.console(8,-1)
# %%
f.console(9,-1)

# %%
# f.gamestatus.factionindex()

# %%
# print(f.cevent.name)
# f.cevent._pool

# %%
f.console(6, 2)