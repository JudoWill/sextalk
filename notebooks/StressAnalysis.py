# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Gmail Stress Measure

# <markdowncell>

# Since I use Gmail as my main work communication, I can reasonably assume that the number of work-related emails is a proxy for the amount of work-related stress I'm under at any given time. I used the `imaplib` tool in the python standard library to extract emails from my Gmail account. I then used `pandas` to aggregate the data.

# <codecell>

import imaplib
imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
imap_server.login('judowill', open('SUPERSECRET.txt').read())
imap_server.select('[Gmail]/All Mail')

# <markdowncell>

# These are the emails of people that I work with. I assume that most emails to or from these people are work related. So to avoid putting them on the internet, they're saved in a file not present in Github. But if you make a TSV file of Email-Name pairs then the code will work for you as well.

# <codecell>

import csv
work_related_emails = list(csv.reader(open('SECRETEMAILS.tsv'), delimiter = '\t'))

# <codecell>

import dateutil.parser
import email


def get_emails_person(address):
    search = '(OR (TO "%(name)s") (FROM "%(name)s"))'
    status, response = imap_server.search(None, search % {'name':address})
    ids = response[0].split()
    for _id in ids:
        yield _id
        
def get_date_from_ids(ids):
    
    resp, data = imap_server.FETCH(','.join(ids), 'RFC822.HEADER')
    id_iter = iter(ids)
    for d in data:
        try:
            msg = email.message_from_string(d[1])
            try:
                tdate = dateutil.parser.parse(msg['DATE'])
            except TypeError:
                continue
            yield id_iter.next(), tdate
        except (IndexError, ValueError):
            pass
        
from itertools import islice

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

known_dates = {}

# <codecell>

email_res = []

for em, name in work_related_emails:
    print name
    needed_ids = []
    already_have = 0
    for _id in get_emails_person(em):
        if _id in known_dates:
            already_have += 1
            email_res.append({
                          'DateTime': known_dates[_id],
                          'Address':em,
                          'Name': name,
                          'EmailID':_id
                          })
        else:
            needed_ids.append(_id)
    print 'already had', already_have
    needed_iter = iter(needed_ids)
    block = take(50, needed_iter)
    count = 0
    while len(block)>0:
        if count % 10 == 0:
            print 'block', count, 'of', len(needed_ids)/50
        for _id, tdate in get_date_from_ids(block):
            known_dates[_id] = tdate
            email_res.append({
                          'DateTime': known_dates[_id],
                          'Address':em,
                          'Name': name,
                          'EmailID':_id
                          })
                
        count += 1
        block = take(50, needed_iter)

# <codecell>

import pandas as pd

email_df = pd.DataFrame(email_res)
email_df['nDateTime'] = pd.to_datetime(email_df['DateTime'], utc=True)

grouped_emails = email_df.groupby(['Name', 'nDateTime'])['EmailID'].count()
all_emails = email_df.groupby('nDateTime')['EmailID'].count().resample('D', how = 'sum').fillna(0)

# <codecell>

fig, axs = plt.subplots(2,1, sharex=True, sharey=True, figsize=(10,10))

groups = [('Aydin', 'Ertel', 'Yichuan', 'Perry', 'Gormley', 'Noor', 'Ceylan', 'Mahdi'),
          ('BrianW', 'Mike', 'Vanessa', 'Niz', 'Benj')]

for names, ax in zip(groups, axs.flatten()):
    for name in names:
        named_emails = grouped_emails.ix[name].resample('D', how='sum').resample('7D', how = 'sum')
        t, large_named_emails = all_emails.align(named_emails, join = 'left')
        large_named_emails.fillna(0).plot(ax = ax, label = name, lw=4, alpha=0.5)
    ax.legend(loc = 'best')
    ax.set_ylabel('#Emails/Week')
    
fig.savefig('figures/EmailsPerWeek.png', dpi = 600)

# <markdowncell>

# I believe that my stress isn't just the number of emails I get per day, but how that number of emails compares to previosuly stressful days. This shows an expanding-max showing the concept.

# <codecell>

fig, ax = plt.subplots(1,1, figsize = (10, 5))

max_emails = pd.expanding_max(all_emails)
all_emails.plot(ax=ax, color = 'b', label = 'All')
max_emails.plot(ax=ax, color = 'b', lw = 10, alpha = 0.1, label = 'Expanding Max')
ax.set_ylabel('Emails/Day')
ax.legend(loc = 'best')
fig.savefig('figures/ExpandingMax.png', dpi = 600)

# <codecell>

fig, axs = plt.subplots(3,1, sharex=True, figsize=(10,15))

for names, ax in zip(groups, axs.flatten()):
    for name in names:
        named_emails = grouped_emails.ix[name].resample('D', how='sum').resample('7D', how = 'sum')
        t, large_named_emails = all_emails.align(named_emails, join = 'left')
        large_named_emails.fillna(0).plot(ax = ax, label = name)
    #ax.legend(loc = 'best')
    ax.set_ylabel('#Emails/Week')

stress = (all_emails/max_emails)
stress.resample('7D', how = 'mean').plot(ax = axs[-1])
axs[-1].set_ylabel('Stress -- Weekly Avg')
fig.savefig('figures/EmailsPlusStress.png', dpi = 600)

# <codecell>

pd.DataFrame({'Stress': stress}).to_csv('results/stress.tsv', sep = '\t')

# <codecell>


