import unittest
from churn.backend import SQLiteBackend
import base64

'''
NOTE: If you are testing this with a real database, be warned this test is destructive
The test also uses a bunch of theoretically private methods in backend to be nasty to the database
Also, if you don't set the below to "True" you won't re-create the database and therefore will hit a bunch
of integrity errors as a result - to get around that, just rm churndb.sql from the working directory (that's
the default name of the db)
'''
BE_DESTRUCTIVE = False

class TestSQLiteBackend(unittest.TestCase):
    def setUp(self):
        self.backend = SQLiteBackend()

    def test_creation_no_existing(self):
        if BE_DESTRUCTIVE:
            self.backend._drop_tables()
            self.backend._verify_tables()
        else:
            pass

    def test_creation_existing(self):
        self.backend._verify_tables()
        self.backend._verify_tables()

    def test_add_single_file(self):
        row = ['DEADBEEF', '2014-09-06 15:00', 'dom/content/foo', 42]
        self.backend.add_single_file_value(row[0], 'user1@foo.com', row[1], row[2], row[3])
        result = self.backend.get_changeset_values_per_file(row[0], row[2])
        # print "Got single result: %s" % result
        # tuples vs. unicode strings make this difficult I'm sure there is a fancy list
        # comprehension that can do this, but for three values, copy/paste works.
        # Note that when querying just by changeset we are currently returning:

        self.assertEqual(row[0], str(result[0][0]))
        self.assertEqual(row[1], str(result[0][1]))
        self.assertEqual(row[2], str(result[0][2]))
        self.assertEqual(row[3], result[0][3])

    def test_store_churn(self):
        path = 'dom/content/foo'
        encodedpath = base64.b64encode(path)
        row = [encodedpath, 'dom/content/foo', '2014-09-01 - 2014-10-12', 42]
        self.backend.store_churn_hash(row[0], row[1], row[2], row[3])
        result = self.backend.get_aggregate_churn_by_file(encodedpath)
        # The result we get back should be:
        # (<path>, <daterange>, <churnvalue>)
        # Once again we get back unicode tuples and we have litaral strings, so...
        # print "Got aggregate result: %s" % result
        self.assertEqual(row[1], str(result[0][0]))
        self.assertEqual(row[2], str(result[0][1]))
        self.assertEqual(row[3], result[0][2])
