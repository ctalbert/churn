from churn.churnhash import ChurnHash
import unittest

directory_structure1 = [
    {'name': 'a/b/c/d/l4a.cpp', 'value': 2},
    {'name': 'a/b/c/d/l4b.js', 'value': 2},
    {'name': 'a/b/c/l3a.c', 'value': 2},
    {'name': 'a/b/c/e/l4c.c', 'value': 2},
    {'name': 'a/b/f/l3a.c', 'value': 5},
    {'name': 'a/g/l2a.c', 'value': 2}]
''' Directory Structure 1 - note that this also tests that l3a.c (same file name
    in different directories is properly counted as two separate files)
a(15)
    b(13)
        c(8)
            d(4)
                l4a.cpp (2)
                l4b.js (2)
            e(2)
                l4c.c (2)
            l3a.c (2)
        f(5)
            l3a.c(5)
    g (2)
        l2.c (2)
'''

directory_structure2_multiple_files = [
    {'name': 'a/b/c/d/l4a.cpp', 'value': 2},
    {'name': 'a/b/c/d/l4b.js', 'value': 2},
    {'name': 'a/b/c/l3a.c', 'value': 2},
    {'name': 'a/b/c/e/l4c.c', 'value': 2},
    {'name': 'a/b/c/d/l4a.cpp', 'value': 2},
    {'name': 'a/b/c/l3a.c', 'value': 2}]
''' Directory structure 2 is the same structure as directory_structure1 except 
this time we test having multiple files mentioned which should give us additive
scores, i.e.:
a(12)
    b(12)
        c(12)
            d(6)
                l4a.cpp (4)
                l4b.js (2)
            e(2)
                l4c.c (2)
            l3a.c (4)
'''

class TestDirectoryStructure1Parsing(unittest.TestCase):
    def setUp(self):
        self.churnhash = ChurnHash()
        for i in directory_structure1:
            self.churnhash.add_file_path(i['name'], i['value'])

    def test_churn_values(self):
        self.assertEqual(self.churnhash.get_churn('a/b/c/d'), 4)
        self.assertEqual(self.churnhash.get_churn('a/b/c/e'), 2)
        self.assertEqual(self.churnhash.get_churn('a/b/c'), 8)
        self.assertEqual(self.churnhash.get_churn('a/b/f'), 5)
        self.assertEqual(self.churnhash.get_churn('a/b'), 13)
        self.assertEqual(self.churnhash.get_churn('a/g'), 2)
        self.assertEqual(self.churnhash.get_churn('a'), 15)

class TestDirectoryStructure2MultiFile(unittest.TestCase):
    def setUp(self):
        self.churnhash = ChurnHash()
        for i in directory_structure2_multiple_files:
            self.churnhash.add_file_path(i['name'], i['value'])

    def test_churn_values_multi_file(self):
        self.assertEqual(self.churnhash.get_churn('a'), 12)
        self.assertEqual(self.churnhash.get_churn('a/b'), 12)
        self.assertEqual(self.churnhash.get_churn('a/b/c'), 12)
        self.assertEqual(self.churnhash.get_churn('a/b/c/d'), 6)
        self.assertEqual(self.churnhash.get_churn('a/b/c/e'), 2)


if __name__ == '__main__':
    unittest.main()
