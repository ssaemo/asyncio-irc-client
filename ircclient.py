import asyncio

class IRCClient(asyncio.Protocol):
    def __init__(self, CHANNEL, NICK, PASS, cb_init, cb_proc, cb_close, loop):
        self.channel = CHANNEL
        self.nick = NICK
        self.password = PASS
        self.cb_init = cb_init
        self.cb_proc = cb_proc
        self.cb_close = cb_close
        self.loop = loop

    # callback
    def connection_made(self, transport):
        self.transport = transport
        
        msg_list = []
        if self.password and len(self.password) > 0:
            msg_list.append('PASS %s\r\n' % self.password)
        msg_list.append('NICK %s\r\n' % self.nick)
        msg_list.append('USER dummy 0 * :dummy\r\n')
        msg_list.append('JOIN %s\r\n' % self.channel)
        
        for msg in msg_list:
            print('*** [SENDED]', msg, end='')
            transport.write(msg.encode())
        
        if self.cb_init:
            self.cb_init()

    # callback
    def data_received(self, data):
        packet = data.decode().split(' ', 3) # split 3 times
        nick = (packet[0].split('!'))[0][1:]
        command = packet[1]
        
        if command != 'PRIVMSG':
            print(data.decode())
        else:
            chat = packet[3][1:].replace('\r\n', '')
            if self.cb_proc:
                self.cb_proc(nick, chat)

    # callback
    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()
        if self.cb_close:
            self.cb_close()

    # call by main()
    def send_chat(self, chat):
        msg = 'PRIVMSG %s :%s\r\n' % (self.channel, chat)
        print('*** [SENDED]', msg)
        self.transport.write(msg.encode())