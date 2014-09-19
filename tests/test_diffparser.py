from churn.diffparser import DiffParser
import os
import unittest

''' Diff pieces from hg log '''
onefilechange = """changeset:   204935:d1cfe5bf9a56
user:        B2G Bumper Bot <release+b2gbumper@mozilla.com>
date:        Thu Sep 11 12:05:46 2014 -0700
summary:     Bumping gaia.json for 2 gaia revision(s) a=gaia-bump

 b2g/config/gaia.json |  2 +-
 1 files changed, 1 insertions(+), 1 deletions(-)"""

multiplefilechange = """changeset:   204900:e2e2e6397253
user:        Thomas Zimmermann <tdz@users.sourceforge.net>
date:        Thu Sep 11 09:38:13 2014 +0200
summary:     Bug 1061489: Distribute Bluetooth HAL implementation among multiple files, r=
shuang

 dom/bluetooth/bluedroid/BluetoothA2dpHALInterface.cpp      |   184 +
 dom/bluetooth/bluedroid/BluetoothA2dpHALInterface.h        |    44 +
 dom/bluetooth/bluedroid/BluetoothAvrcpHALInterface.cpp     |   593 +++
 dom/bluetooth/bluedroid/BluetoothAvrcpHALInterface.h       |    84 +
 dom/bluetooth/bluedroid/BluetoothHALHelpers.cpp            |   298 +
 dom/bluetooth/bluedroid/BluetoothHALHelpers.h              |  1439 ++++++++
 dom/bluetooth/bluedroid/BluetoothHALInterface.cpp          |  3684 +--------------------
 dom/bluetooth/bluedroid/BluetoothHALInterface.h            |   214 -
 dom/bluetooth/bluedroid/BluetoothHandsfreeHALInterface.cpp |   616 +++
 dom/bluetooth/bluedroid/BluetoothHandsfreeHALInterface.h   |    95 +
 dom/bluetooth/bluedroid/BluetoothSocketHALInterface.cpp    |   480 ++
 dom/bluetooth/bluedroid/BluetoothSocketHALInterface.h      |    49 +
 dom/bluetooth/moz.build                                    |     5 +
 13 files changed, 3978 insertions(+), 3807 deletions(-)"""

multiplechangediff = """changeset:   204900:e2e2e6397253
user:        Thomas Zimmermann <tdz@users.sourceforge.net>
date:        Thu Sep 11 09:38:13 2014 +0200
summary:     Bug 1061489: Distribute Bluetooth HAL implementation among multiple files, r=
shuang

 dom/bluetooth/bluedroid/BluetoothA2dpHALInterface.cpp      |   184 +
 dom/bluetooth/bluedroid/BluetoothA2dpHALInterface.h        |    44 +
 dom/bluetooth/bluedroid/BluetoothAvrcpHALInterface.cpp     |   593 +++
 dom/bluetooth/bluedroid/BluetoothAvrcpHALInterface.h       |    84 +
 dom/bluetooth/bluedroid/BluetoothHALHelpers.cpp            |   298 +
 dom/bluetooth/bluedroid/BluetoothHALHelpers.h              |  1439 ++++++++
 dom/bluetooth/bluedroid/BluetoothHALInterface.cpp          |  3684 +--------------------
 dom/bluetooth/bluedroid/BluetoothHALInterface.h            |   214 -
 dom/bluetooth/bluedroid/BluetoothHandsfreeHALInterface.cpp |   616 +++
 dom/bluetooth/bluedroid/BluetoothHandsfreeHALInterface.h   |    95 +
 dom/bluetooth/bluedroid/BluetoothSocketHALInterface.cpp    |   480 ++
 dom/bluetooth/bluedroid/BluetoothSocketHALInterface.h      |    49 +
 dom/bluetooth/moz.build                                    |     5 +
 13 files changed, 3978 insertions(+), 3807 deletions(-)

changeset:   204899:8644a9c4b993
parent:      204848:35b605159edf
user:        Thomas Zimmermann <tdz@users.sourceforge.net>
date:        Thu Sep 11 09:38:10 2014 +0200
summary:     Bug 1061489: Move Bluedroid code out of BluetoothInterface.{cpp,h}, r=shuang

 dom/bluetooth/BluetoothInterface.cpp              |  109 ++++
 dom/bluetooth/BluetoothInterface.h                |  634 +++++++++++++++++++++++++
 dom/bluetooth/bluedroid/BluetoothHALInterface.cpp |  770 +++++++++++++++---------------
 dom/bluetooth/bluedroid/BluetoothHALInterface.h   |  324 +++++++++++++
 dom/bluetooth/bluedroid/BluetoothInterface.h      |  675 ---------------------------
 dom/bluetooth/moz.build                           |    3 +-
 6 files changed, 1448 insertions(+), 1067 deletions(-)
"""

class TestDiffParser(unittest.TestCase):
    def test_simple_diff(self):
        dp = DiffParser(os.getcwd())
        diffinfo = dp.parse(onefilechange.split('\n'))
        correct_info = {'diffs':['d1cfe5bf9a56'], 
                        'd1cfe5bf9a56': {'files': ['b2g/config/gaia.json']}}
        self.assert_diff_correct(diffinfo, correct_info)
        self.assertEqual(diffinfo['d1cfe5bf9a56']['b2g/config/gaia.json'], 2)
  
    def test_multifile_diff(self):
        dp = DiffParser(os.getcwd())
        diffinfo = dp.parse(multiplefilechange.split('\n'))
        correct_info = {'diffs': ['e2e2e6397253'],
                        'e2e2e6397253': {'files': [
                        'dom/bluetooth/bluedroid/BluetoothA2dpHALInterface.cpp',   
                        'dom/bluetooth/bluedroid/BluetoothA2dpHALInterface.h',
                        'dom/bluetooth/bluedroid/BluetoothAvrcpHALInterface.cpp',    
                        'dom/bluetooth/bluedroid/BluetoothAvrcpHALInterface.h',      
                        'dom/bluetooth/bluedroid/BluetoothHALHelpers.cpp',           
                        'dom/bluetooth/bluedroid/BluetoothHALHelpers.h',             
                        'dom/bluetooth/bluedroid/BluetoothHALInterface.cpp',         
                        'dom/bluetooth/bluedroid/BluetoothHALInterface.h',
                        'dom/bluetooth/bluedroid/BluetoothHandsfreeHALInterface.cpp',
                        'dom/bluetooth/bluedroid/BluetoothHandsfreeHALInterface.h',
                        'dom/bluetooth/bluedroid/BluetoothSocketHALInterface.cpp',
                        'dom/bluetooth/bluedroid/BluetoothSocketHALInterface.h']}}
        self.assert_diff_correct(diffinfo, correct_info)
        self.assertEqual(diffinfo['e2e2e6397253']['dom/bluetooth/bluedroid/BluetoothHALInterface.cpp'], 3684)

    def test_multichange_diff(self):
        dp = DiffParser(os.getcwd())
        diffinfo = dp.parse(multiplechangediff.split('\n'))
        self.assertEqual(diffinfo['e2e2e6397253']['dom/bluetooth/moz.build'], 5)
        self.assertEqual(diffinfo['8644a9c4b993']['dom/bluetooth/moz.build'], 3)

    def assert_diff_correct(self, diffinfo, correct_info):
           for d in correct_info['diffs']:
                self.assertTrue(d in diffinfo)
                for f in correct_info[d]['files']:
                    self.assertTrue(f in diffinfo[d].keys())
