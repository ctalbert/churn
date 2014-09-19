import subprocess
import os.path
import re

class DiffParserError(Exception):
    def __init__(self, msg):
        self.value = msg
    def __str__(self):
        return repr(self.value)


class DiffParser(object):
    def __init__(self, repo_location, repo_type = "hg"):
        self.hash = {}
        self.current_diff = ''
        self.file_reading_mode = False
        self.repo_type = repo_type
        if not os.path.exists(repo_location):
            raise DiffParserError("Repo Location does not exist: %s" % repo_location)
        self.repo_location = repo_location
    
    def parse(self, input):
        if self.repo_type == "hg":
            self.parse_hg(input)
        else:
            raise DiffParserError("Cannot yet parse repo type: %s" % self.repo_type)
        return self.hash

    def parse_hg(self, input):
        chgsetRE = re.compile('(^changeset: +)(.*)')
        usernameRE = re.compile('(^user: +)(.*)')
        summaryRE = re.compile('^summary: ')
        summarylineRE = re.compile('.*d* files changed, d*')

        for line in input:
            if self.file_reading_mode:
                # Then we are reading files until we find a summary line
                if summarylineRE.match(line):
                    self.current_diff = ''
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

                    # store in format:
                    # { 
                    #   '<chgsetID>': { '<file1>': <lines_changed>,
                    #                   '<file2>': <lines_changed>,
                    #                    .....
                    #                 },
                    # }
                    self.hash[self.current_diff][fileline[0]] = int(fileline[2])
                    continue

            if self.current_diff == '':
                m = chgsetRE.match(line)
                if m:
                    self.current_diff = m.group(2).split(':')[1]
                    self.hash[self.current_diff] = {}
                    continue
            else:
                m = usernameRE.match(line)
                if m:
                    self.hash[self.current_diff]['user'] = m.group(2)
                    continue

                if summaryRE.match(line):
                    self.file_reading_mode = True
                    continue

       

