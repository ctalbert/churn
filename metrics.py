# getmetrics.py

'''command to display statistics about repository history'''

from mercurial.i18n import _
from mercurial import patch, cmdutil, scmutil, util, templater, commands
from mercurial import encoding
import os
import re
import time, datetime
import json

cmdtable = {}
command = cmdutil.command(cmdtable)
testedwith = 'internal'

# From original churn code, not using yet, might in the future
#def maketemplater(ui, repo, tmpl):
#    tmpl = templater.parsestring(tmpl, quoted=False)
#    try:
#        t = cmdutil.changeset_templater(ui, repo, False, None, tmpl,
#                                        None, False)
#    except SyntaxError, inst:
#        raise util.Abort(inst.args[0])
#    return t

def parse_commit_msg(msg):
    ''' Returns:
    bugnumber,     # The bug number
    is_backout,    # Whether this seems to be a backout
    backout_rev,   # The rev we think is being backed out
    reviewer,      # Reviewer of the patch
    approver,      # Approver of the patch
    
    If any of these things cannot be determined, they will be the empty string
    '''
    bugRE = re.compile('.*[b|B]ug (\d{3,15}).*')
    std_backoutRE = re.compile('.*[backout|backed out|back out] .* ([0-9A-F]{12,12}) .*', re.IGNORECASE)
    full_backoutRE = re.compile('.*[b|B]ackout.*')
    reviewerRE = re.compile('.* r=(.*).*', re.IGNORECASE)
    approverRE = re.compile('.* a=(.*).*', re.IGNORECASE)
    
    bug = ''
    is_backout = False
    backout_rev = ''
    reviewer = ''
    approver = ''

    m = bugRE.match(msg)
    if m:
        bug = m.groups()[0]
    m = full_backoutRE.match(msg)
    if m:
        is_backout = True
        # Try to get the backout rev
        m = std_backoutRE.match(msg)
        if m:
            backout_rev = m.groups()[0]
    m = reviewerRE.match(msg)
    if m:
        reviewer = m.groups()[0]
    m = approverRE.match(msg)
    if m:
        approver = m.groups()[0]

    return bug, is_backout, backout_rev, reviewer, approver

def get_lines_and_files(ui, repo, ctx1, ctx2, fns):
    # Returns a list of dicts:
    # [{'filename': <file>, 'added': nn, 'removed': nn},
    #  {....},
    # ]
    files = []
    currentfile = {}
    fmatch = scmutil.matchfiles(repo, fns)
    diff = ''.join(patch.diff(repo, ctx1.node(), ctx2.node(), fmatch))
    for l in diff.split('\n'):
        if l.startswith("diff -r"):
            # If we have anything in currentfile, append to list
            if currentfile:
                files.append(currentfile)
                currentfile = {}

            # This is the first line of a file set current file
            currentfile['filename'] = l.split(' ')[-1]
            currentfile['added'] = 0
            currentfile['removed'] = 0
            
        if l.startswith("+") and not l.startswith("+++ "):
            currentfile['added'] += 1
        elif l.startswith("-") and not l.startswith("--- "):
            currentfile['removed'] += 1
    # The last file won't have been added to files, so add it now
    files.append(currentfile)
    return files

def gather_metrics(ui, repo, *pats, **opts):
    # This is my code to gather what we need for metrics
    state = {'count': 0}
    metrics = {}
    m = scmutil.match(repo[None], pats, opts)

    def walker(ctx, fns):
        #import pdb
        #pdb.set_trace()

        # Create the chgset's object in our tracker
        chgsetID = ctx.hex()
        metrics[chgsetID] = {}
        metrics[chgsetID]['is_merge'] = len(ctx.parents()) > 1
        ctx1 = ctx.parents()[0]
        metrics[chgsetID]['parents'] = ctx.parents()[0].hex()
        
        user = ctx.user()
        metrics[chgsetID]['committer'] = user
        metrics[chgsetID]['committer_email'] = user[user.find('<')+1:user.find('>')]
        metrics[chgsetID]['committer_name'] = user.split('<')[0].strip()

        t, tz = ctx.date()
        d = datetime.datetime(*time.gmtime(float(t) - tz)[:6])
        metrics[chgsetID]['datestamp'] = d.strftime('%Y-%m-%dT%H:%M:%SZ')

        # If we have a robot committer, don't bother parsing the commit message
        metrics[chgsetID]['msg'] = ctx.description()
        if 'b2gbumper@mozilla.com' not in user:
            metrics[chgsetID]['bug'], metrics[chgsetID]['is_backout'], \
            metrics[chgsetID]['backout_rev'], metrics[chgsetID]['reviewer'], \
            metrics[chgsetID]['approver'] = parse_commit_msg(ctx.description())
        
        metrics[chgsetID]['files'] = get_lines_and_files(ui, repo, ctx1, ctx, fns)

        state['count'] += 1
        ui.progress(_('analyzing'), state['count'], total=len(repo))

    for ctx in cmdutil.walkchangerevs(repo, m, opts, walker):
        continue

    ui.progress(_('analyzing'), None)
    return metrics

@command('metrics',
    [('r', 'rev', [],
     _('get metrics for the specified revision or range'), _('REV')),
    ('d', 'date', '',
     _('get metrics for revisions matching date spec'), _('DATE')),
    ('f', 'file', '',
     _('File to dump JSON data to'), _('FILE'))
    ] + commands.walkopts,
    _("hg metrics [-d DATE] [-r REV] [-f FILE]"),
    inferrepo=True)
def metrics(ui, repo, *pats, **opts):
    '''Dump a bunch of stats about changes in a repo

    This command will dump lots of stats about a repo into json:
    {
    <chgsetID>: {
        <msg>: <commit message>,
        <isBackout>:True|False,
        <Bug>: <bug ID parsed from commit message>,
        <Reviewer>: ''|<parsed from commit message>,
        <Approver>: ''|<parsed from commit message>,
        files: [{filename: <file>, removed: <lines removed>, added: <lines added>},
                {filename: <file>, removed: nn, added: nn},
                ...
               ],
        <parent>: <chgsetID>
        <author>: <full name email address pair of person that pushed change>
        <authorname>: <name>
        <authoremail>: <email>
        <date>: <date/time stamp change commited in GMT>
        },
    <chgsetID>:....
    }

    '''
    import pdb
    pdb.set_trace()
    info = gather_metrics(ui, repo, *pats, **opts)
    fp = open(opts.get('file'), "w")
    json.dump(info, fp, indent=2)
    fp.close()
    
    
