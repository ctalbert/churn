import sqlite3
import sys
import traceback

CHURN_PER_CHGSET_TABLE_NAME = 'chgset_churn'
CHURN_TABLE_NAME = 'aggregate_churn'

# TODO Should really fully parameterize table names...future.
create_table_stmts = {CHURN_PER_CHGSET_TABLE_NAME: '''CREATE TABLE chgset_churn(chgset VARCHAR(100), 
                                           time TIMESTAMP, filepath VARCHAR(512), churn INTEGER,
                                           PRIMARY KEY(chgset, filepath))''',
                      CHURN_TABLE_NAME: '''CREATE TABLE aggregate_churn(encodedfile VARCHAR(120), filepath VARCHAR(512),
                                           daterange VARCHAR(50), churn INTEGER,
                                           PRIMARY KEY(encodedfile, daterange))'''}

TABLE_EXIST_STMT = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"

#INSERT_FILE_ID = 'INSERT INTO file_id (filepath) VALUES(?)'
INSERT_CHGSET_CHURN = 'INSERT INTO chgset_churn VALUES(?, ?, ?, ?)'
INSERT_AGG_CHURN = 'INSERT INTO aggregate_churn VALUES(?, ?, ?, ?)'

# Could not get this to parameterize properly with ?'s
DROP_TABLE_STMT = "DROP TABLE %s"

GET_VALUES_PER_CHANGESET = 'SELECT * FROM chgset_churn WHERE chgset=?'
GET_VALUES_PER_CHANGESET_PER_FILE = 'SELECT * FROM chgset_churn WHERE (chgset = ?) AND (filepath LIKE ?)'
GET_AGGREGATE_VALUE_FROM_ENCODED_FILE = 'SELECT filepath, daterange, churn FROM aggregate_churn WHERE encodedfile = ?'

class SQLiteBackend(object):
    def __init__(self, dbname='churndb.sql'):
        if dbname:
            self._dbconn = sqlite3.connect(dbname)
        else:
            self._dbconn = sqlite3.connect('churndb.sql')
        self._verify_tables()

    def _run_execute(self, cursor, query, queryparams = None):
        # Just a utility to keep from having to type try...finallies everywhere
        # Note that queryparams is expected to be a list
        try:
            if cursor == None:
                print "WARNING: Getting new cursor"
                cursor = self._dbconn.cursor()
            if queryparams:
                cursor.execute(query, queryparams)
            else:
                cursor.execute(query)
        except:
            print "Exception during query: %s" % query
            if queryparams:
                print "Query Params for this query: %s" % queryparams
            traceback.print_exc()
            cursor.close()
            cursor = None

        return cursor

    def _verify_tables(self):
        # Verify that tables exist in our database and create them if not
        c = self._dbconn.cursor()
        for t in create_table_stmts:
            if not self._table_exists(t):
                self._run_execute(c, create_table_stmts[t])

    def _drop_tables(self):
        c = self._dbconn.cursor()
        for t in create_table_stmts:
            if self._table_exists(t):
                self._run_execute(c, DROP_TABLE_STMT % t)
        self._dbconn.commit()

    def _table_exists(self, name):
        c = self._dbconn.cursor()
        c = self._run_execute(c, TABLE_EXIST_STMT, [name])
        r = c.fetchone()
        return (r and (r[0] == name))

    def add_single_file_value(self, chgset, user, timestamp, filepath, churnvalue):
        # Add two records one into the files table and one into the churnvalue
        # table to track that paths' churns over time
        c = self._dbconn.cursor()
        
        self._run_execute(c, INSERT_CHGSET_CHURN, [chgset, timestamp, filepath, churnvalue])
        self._dbconn.commit()
 
    def store_churn_hash(self, encodedfile, filepath, daterange, churnhash):
        # Store the entire exploded churn hash
        c = self._dbconn.cursor()
        self._run_execute(c, INSERT_AGG_CHURN, [encodedfile, filepath, daterange, churnhash])
        self._dbconn.commit()

    def get_changeset_values_per_file(self, chgset, filepath=''):
        # Without a filepath we return all files for that changeset. With a file path,
        # we return all values for that changeset whose filepaths contain the specified
        # filepath
        c = self._dbconn.cursor()
        if filepath != '':
            c = self._run_execute(c, GET_VALUES_PER_CHANGESET_PER_FILE, [chgset, filepath])
        else:
            c = self._run_execute(c, GET_VALUES_PER_CHANGESET, [chgset])
        return c.fetchall()

    def get_aggregate_churn_by_file(self, encodedfile):
        c = self._dbconn.cursor()
        c = self._run_execute(c, GET_AGGREGATE_VALUE_FROM_ENCODED_FILE, [encodedfile])
        return c.fetchall()
