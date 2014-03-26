""" GDB Python customization auto-loader for js shell """

import os.path
sys.path[0:0] = [os.path.join('/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/js/src', 'gdb')]

import mozilla.autoload
mozilla.autoload.register(gdb.current_objfile())
