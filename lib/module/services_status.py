import snmpy.module
import subprocess
import logging
import time

LOG = logging.getLogger()

class services_status(snmpy.module.ValueModule):
    def __init__(self, conf):
        LOG.debug("INIT")
	snmpy.module.ValueModule.__init__(self, conf)
	
	self.check_services()

    def update(self):
        pass

    @snmpy.task_func(snmpy.THREAD_TASK)
    def check_services(self):
	while True:
            for item in self:
                self[item] = subprocess.call(['service', item, 'status'])
            time.sleep(30)
