{"theme":"one_moz.css"}

# The Joy Of (Quantifying) Sex
A spoonful of sex helps the statistics go down.
Will Dampier, PhD

====

|## Quantification Topics
====*

|## Stress

|Use python `imaplib` to parse emails from work contacts.

====*

|## Sexual Satisfaction

|Sexual satisfaction was tracked during relationships with my three long-term relationships using numerous collection techniques.

|Use python and `statsmodels` to find patterns in which _tags_ I gave to each encounter.

====

|## Gmail Access

Pretty dang easy!
	import imaplib
	imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
	imap_server.login('judowill', open('SUPERSECRET.txt').read())
	imap_server.select('[Gmail]/All Mail')

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
			msg = email.message_from_string(d[1])
			date = dateutil.parser.parse(msg['DATE'])
			yield id_iter.next(), date

====

|## Emails Per Week
!(figures/EmailsPerWeek.png)<<width:1000>>

====*

|## What about scale
It actually seems like _hard_ weeks get easier. This feels more realistic.

!(figures/ExpandingMax.png)<<width:1000>>

====* 

|## Putting it together

!(figures/EmailsPlusStress.png)<<width:1000>>

====

|## Sex Quantification
	import pandas as pd
	
	sex_data = pd.read_csv('projectdata/willdata.tsv', 
				sep = '\t', 
				parse_dates = [0], 
				index_col=0)
	stress_data = pd.read_csv('results/stress.tsv', sep = '\t', parse_dates = [0])
	final_data = pd.merge(sex_data, stress_data.groupby('nDateTime')[['Stress']].first(),
        	              left_index=True, 
	                      right_index = True,
	                      how = 'left')
	final_data.head()

!(images/DataCollection.png)

====*

|## Frequency

!(figures/frequency.png)

====

|## Crazy Statistics

|Use Linear Models to find the effect of the variables on both my and her rankings. 

|This is trivially accomplished using `statsmodels`.

====*

|### Linear Models

	import statsmodels.formula.api as smf
	eqn = 'HerRanking ~ PreOrgs + missionary + doggy + cowgirl + reversecowgirl + kinky + Stress'
	res = smf.ols(eqn, data = final_data).fit()
	res.summary()

!(images/RegressionSummary.png)

====*

|## Observation

|Stress is *not* correlated with her statisfaction or mine.

====

|###CCPR Plot
|A way to show the effect of an indepedent variable on the response variable after subtracting the effect of other items in the model.


[Wikipedia Partial Residual Plots](http://en.wikipedia.org/wiki/Partial_residual_plot)

====*

## Data Dump

!(figures/position_preference.png)

====*

## _Foreplay_ orgasms

!(images/pre_org_preference.png)


====*

## Cowgirl

!(images/cowgirl_preference.png)

====*

## Stress

!(images/stress_preference.png)

====*

## Summary

!(figures/effect_heatmap.png)

====*

|## Observation

Different strokes for different folks.

====

|### Want to do an analysis like this?

This is all on Github.

[http://github.com/judowill/sextalk/](http://github.com/judowill/sextalk/)
[http://judowill.github.io/sextalk/](http://judowill.github.io/sextalk/)

====*

|### How were these slides made?

###|JavaScript    : [reveal.js](http://hakim.se/projects/reveal-js)
###|Markdown      : [Daring Fireball](http://daringfireball.net/)

----

###|Markdown to HTML: [md2reveal.py](https://github.com/thoppe/md2reveal)
|_ (Written by a former Judo student of mine)_

