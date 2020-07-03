
def maxoflist(alist):
    m = max(alist)
    return [i for i, j in enumerate(alist) if j == m]


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


#%%
class Event:
    '''
    all playernums are real playernums, not list index in python. 
    All numbers are in relatedusers, targets, and info
    '''
    def __init__(self, relatedusers, targets=list(), info=None):
        self._relatedusers = relatedusers[:]
        self._pool = {'A': list()}
        self._targets = targets[:]
        self.status = 'Active'
        self._info = info
        self.result = ['A']
        self._log = list()

    def start(self):
        pass

    def update(self, message):
        sender = message.sender
        if sender in self._relatedusers:
            self._relatedusers.remove(sender)
            self.type = message.texttype
            if message.target in self._targets:
                if message.target in self._pool.keys():
                    self._pool[message.target].append(message.sender)
                else:
                    self._pool.update({message.target: [message.sender]})
            else:
                self._pool['A'].append(message.sender)
        if len(self._relatedusers) == 0:
            self.end()

    def end(self):
        self.status = 'End'
        pool = [len(p) for p in list(self._pool.values())]
        max = maxoflist(pool)
        self.result = list()
        for index in max:
            self.result.append(list(self._pool.keys())[index])
        if 'A' in self.result:
            self.result.remove('A')

    def getpool(self):
        return self._pool

    def getlog(self):
        return self._log


class EventNight(Event):
    def __init__(self, info):
        super().__init__()


class EventPool(Event):
    def end(self):
        super().end()
        self._log.append(LogMessage([0], [0],
                                    info={'Pool': self._pool,
                                          'result': self.result},
                                    auth=[-1]))


class EventPoolRandom(Event):
    def end(self):
        super().end()
        if len(self.result) > 0:
            self.result = random.choices(self.result)
        self._log.append(LogMessage(self._relatedusers, [0],
                                    info={'Pool': self._pool,
                                          'result': self.result},
                                    auth=[-1]))


class EventNvwu(Event):
    '''
    _info = {'nvwu': user, 'daokou': playernum}
    '''
    # def __init__(self, relatedusers, external, targets=list(), texttype='default'):
    #     super().__init__(relatedusers=relatedusers, external=external,
    #                      targets=targets, texttype=texttype)

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
    def end(self):
        super().end()
        userindex = self._info['userindex']
        roleindex = self._info['roleindex']
        users = self._info['users']
        ynum = roleindex['yuyanjia'][0].playernum
        if len(self.result) > 0:
            self._log.append(LogMessage(sender=[ynum], receiver=[0],
                                        info={'type': 'yuyanjiayanren',
                                              'target': self.result[0],
                                              'result': userindex[users.pick(self.result[0])]},
                                        auth=[ynum]))




# new = EventPool(relatedusers=[1, 2, 3], targets=[1, 2])


class Langrensha:
    def __init__(self):
        self.log = list()
        self.events = [Event]
        self.cevent = None

    def startevent(self, event=None, relatedusers=list(), targets=list(), info=None):
        if event is None:
            event = self.events[0]
        self.cevent = event(relatedusers=relatedusers, targets=targets, info=info)
        self.cevent.start()

    def update(self, message):
        self.cevent.update(message)
        if self.cevent.status == 'End':
            self.endevent()

    def endevent(self):
        self.log.extend(self.cevent.getlog())
        print(self.cevent.getpool())

    def loguserview(self, cuser=0):
        clog = list()
        for item in self.log:
            if cuser == 0 or cuser in item.auth or -1 in item.auth:
                clog.append(item.info)
        return clog

    def printlog(self):
        for item in self.log:
            print(item)
            print('\n')


#%%
users = Users(['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8', 'i9', '10', '11', '12'])

newgame = GameStatus(users=users, mode='MODE_YNLB')
newgame.initialize()
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

#%%
with open('data.txt', 'w') as outfile:
    json.dump(newgame.gameindex(), outfile)


# %%
with open('data.txt', 'r') as readfile:
    dd = json.load(readfile)