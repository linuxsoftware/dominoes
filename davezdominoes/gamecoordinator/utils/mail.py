#---------------------------------------------------------------------------
# Mailer functions
#---------------------------------------------------------------------------
import sys
from ...commoncode.proc import daemonSpawn

def launchPostMail(settings):
    here    = settings['here']
    cfgfile = settings['__file__']
    daemonSpawn("dominoes_post_mail", "data/mail", "--config", cfgfile,
                cwd=here, log="post_mail.log", delayStart=1.25)

def getPostMailLauncher(settings):
    return lambda: launchPostMail(settings)

