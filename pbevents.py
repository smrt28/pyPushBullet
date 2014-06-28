from pbkey import KEY
from pushbullet import PushBullet

MODEL= 'chaotic'
HIST_FILE='/home/smrt/.pb_history'


class PBEventHandler:
    def __init__(self):
        self.KEY = KEY
        self.HIST_FILE = HIST_FILE
        self.pb = PushBullet(KEY)
        self.maxmod = float(0)
        self.iden = None
        
        self._sync_maxmod()
        self._sync_maxmod(self._get_modified())

        devices = self.pb.getDevices()

        for device in devices:
            if device['active']:
                print 'DEVICE: ' + str(device)

        for device in devices:
            if device.get('model', None) == MODEL:
                self.iden = device['iden']
                break


    def _get_modified(self):
        return self.pb.getPushHistory(self.maxmod)


    def _sync_maxmod(self, pushes = []):
        for push in pushes:
            if float(push['modified']) > self.maxmod:
                self.maxmod = float(push['modified'])

        n = float(self.maxmod)
        try:
            fn = float(open(self.HIST_FILE).read()) + 0.01
        except:
            fn = 0
        fn = max(float(n), float(fn))
        open(self.HIST_FILE, "w").write(str(fn))
        self.maxmod = float(fn)
        

    def _event(self, data, callback):
        if data['type'] == 'tickle' and data['subtype'] == 'push':
            pushes = self.pb.getPushHistory(self.maxmod)
            for push in pushes:
                if push['modified'] > self.maxmod:
                    self.maxmod = push['modified']
                self._sync_maxmod()

                if self.iden != None and\
                        push.get('target_device_iden', "") != self.iden: continue
                try:
                    callback(push)
                except:
                    pass


    def run(self, callback):
        def __event(data):
            print "event: " + str(data)
            self._event(data, callback)

        self.pb.realtime(__event)



def event(data):
    print "EVENT: " + str(data)

#pb = PushBullet(KEY)
#pb.createDevice("smrt28")

pb = PBEventHandler()
pb.run(event)


