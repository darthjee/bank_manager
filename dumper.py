#!/usr/bin/env python
import settings
import os
import sys
import re
from sre_constants import CATEGORY_LINEBREAK

dataset = settings.DATABASES['bank']
dataset['OUTPUT'] = 'dump.sql'

class Command():
    @classmethod
    def cmd_load(cla):
        '''Carrega um arquivo sql no banco de dados'''
        str = "mysql -u %(USER)s -p%(PASSWORD)s %(NAME)s < %(OUTPUT)s" % dataset
        os.system(str)
    @classmethod
    def cmd_dump(cla):
        '''faz um dump de um banco sql em um arquivo''' 
        str = "mysqldump -u %(USER)s -p%(PASSWORD)s %(NAME)s > %(OUTPUT)s" % dataset
        os.system(str)
    @classmethod
    def cmd_help(cla):
        '''Exibe esta ajuda'''
        cmds = [cmd for cmd in dir(Command) if re.match("^cmd_",cmd)]
        print "modo de uso:\ndumper.py command output\n"
        for cmd in cmds:
            print "  %-4s : %s\n" % (re.sub("^cmd_", "",cmd),getattr(cla,cmd).__doc__) 
    @classmethod
    def call(cla, met='help'):
        try:
            method = getattr(cla, 'cmd_%s' % met)
        except:
            method = getattr(cla, 'cmd_help')
        method()

def main(argv):
    if (len(argv)>0):
        cmd = argv[0]
    else:
        cmd = 'help'
    Command.call(cmd)

    
if __name__ == "__main__":
    main(sys.argv[1:])
