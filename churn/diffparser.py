import subprocess
import os.path
import re

class DiffParserError(Exception):
    def __init__(self, msg):
        self.value = msg
    def __str__(self):
        return repr(self.value)


class DiffParser(object):
    def __init__(self, repo_type = "hg"):        
        self.hash = {} # Hash is our final copy holding only diffs that are complete
        self.current_diff = {} # self.current_diff is in-process parsing
        self.current_cset = '' # Current cset we are parsing
        self.file_reading_mode = False
        self.repo_type = repo_type

    def parse(self, input):
        if self.repo_type == "hg":
            self._parse_hg(input)
        else:
            raise DiffParserError("Cannot yet parse repo type: %s" % self.repo_type)
        return self.get_parsed_diffs()

    def _parse_hg(self, input):
        chgsetRE = re.compile('(^changeset: +)(.*)')
        usernameRE = re.compile('(^user: +)(.*)')
        summaryRE = re.compile('^summary: ')
        summarylineRE = re.compile('.*d* files changed, d*')
        #print "DIFFPARSR INPUT: %s" % input
        for line in input:
            if line == '':
                continue

            if self.file_reading_mode:
                # Then we are reading files until we find a summary line
                if summarylineRE.match(line):
                    # For the final hash, we store in format:
                    # { 
                    #   '<chgsetID>': { '<file1>': <lines_changed>,
                    #                   '<file2>': <lines_changed>,
                    #                    .....
                    #                 },
                    #   '<chgsetID>': {...},
                    # }                    
                    self.hash.update(self.current_diff)
                    self.current_cset = ''
                    self.current_diff = {}
                    self.file_reading_mode = False
                    continue
                else:
                    # Read file lines by splitting using spaces
                    fileline = line.split()
                    if '|' not in fileline:
                        # spurious new line can happen with long summaries
                        continue

                    # Make sure we have the line we're expecting
                    if fileline[1] != '|':
                        raise DiffParserError('Invalid file line detected: %s' % line)
                    
                    self.current_diff[self.current_cset][fileline[0]] = int(fileline[2])
                    continue

            if self.current_cset == '':
                m = chgsetRE.match(line)
                if m:
                    self.current_cset = m.group(2).split(':')[1]
                    self.current_diff[self.current_cset] = {}
                    continue
            else:
                m = usernameRE.match(line)
                if m:
                    self.current_diff[self.current_cset]['user'] = m.group(2)
                    continue

                if summaryRE.match(line):
                    self.file_reading_mode = True
                    continue


    def get_parsed_diffs(self):
        # Returns the self.hash list of parsed items if there is anything in it
        # (it only contains fully parsed diffs)
        if len(self.hash) > 0:
            return self.hash
        else:
            return None       

