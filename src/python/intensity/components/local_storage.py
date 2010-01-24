
#=============================================================================
# Copyright (C) 2008 Alon Zakai ('Kripken') kripkensteiner@gmail.com
#
# This file is part of the Intensity Engine project,
#    http://www.intensityengine.com
#
# The Intensity Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3.
#
# The Intensity Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with the Intensity Engine.  If not, see
#     http://www.gnu.org/licenses/
#     http://www.gnu.org/licenses/agpl-3.0.html
#=============================================================================


import os
import sqlite3

from intensity.base import *
from intensity.logging import *
from intensity.signals import signal_component


db_file = os.path.join( get_home_subdir(), 'local_storage_' + ('client' if Global.CLIENT else 'server') + '.db' )
need_table = not os.path.exists(db_file)

conn = sqlite3.connect(db_file)

if need_table:
    print 'LocalStorage: Creating database'
    conn.execute('''create table data (key text primary key, value text)''')

def receive(sender, **kwargs):
    component_id = kwargs['component_id']
    data = kwargs['data']

    try:
        if component_id == 'LocalStorage':
            parts = data.split('|')
            command = parts[0]
            if command == 'read':
                print "READ:" + parts[1]
                try:
                    ret = conn.execute('''select value from data where key = ?''', (parts[1],)).fetchone()[0]
                    print ":::::", ret
                    return str(ret)
                except Exception, e:
                    print "Ah well:", str(e)
                    return ''
            elif command == 'write':
                print "WRITE:" + parts[1] + ',' + parts[2]
                if conn.execute('''select * from data where key = ?''', (parts[1],)).fetchone() is None:
                    print "Insert"
                    conn.execute('''insert into data values (?, ?)''', (parts[1], parts[2]))
                else:
                    print "Update"
                    conn.execute('''update data set value = ? where key = ?''' , (parts[2], parts[1]))
                conn.commit()
                print "Reread:", conn.execute('''select value from data where key = ?''', (parts[1],)).fetchone()
    except Exception, e:
        log(logging.ERROR, "Error in LocalStorage component: " + str(e))

    return ''

signal_component.connect(receive, weak=False)

