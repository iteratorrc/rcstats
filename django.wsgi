import os
import sys

path = '/home/asymptote/Desktop/RCRacePerformance'
if path not in sys.path:
   sys.path.append(path)
path = '/home/asymptote/Desktop'
if path not in sys.path:
   sys.path.append(path)


os.environ['DJANGO_SETTINGS_MODULE'] = 'RCRacePerformance.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
