import unittest
from churn.churn import ChurnDriver
'''
!!!! NOTE !!!!
This requires mercurial to be installed and you need to edit these paths for your
environment
'''
repoloc = '../m-c'
repocmd = 'hg log --stat -l 10'

class TestChurnDriver(unittest.TestCase):
    def test_churndriver(self):
        chd = ChurnDriver(repo_location=repoloc, repo_command=repocmd, repo_type='hg')
        ch = chd.run()

        print "DOM directory Churn value: %d" % ch.get_churn('dom')
        # I can't express the actual value because if I update my tree, the test will fail as the
        # churn number will be different, but dom contains so many other directories
        # it would be really wierd to be 0.
        self.assertTrue(ch.get_churn('dom') > 0)
