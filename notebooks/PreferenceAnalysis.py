# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
from functools import partial
from datetime import datetime, timedelta

# <codecell>

sex_data = pd.read_csv('projectdata/willdata.tsv', sep = '\t', parse_dates = [0], index_col=0)
sex_data.head()

# <codecell>

stress_data = pd.read_csv('results/stress.tsv', sep = '\t', parse_dates = [0])

# <codecell>

final_data = pd.merge(sex_data, stress_data.groupby('nDateTime')[['Stress']].first(),
                      left_index=True, 
                      right_index = True,
                      how = 'left')
final_data.head()

         

# <codecell>

fig, ax = plt.subplots(3,1, figsize = (15, 10))

pd.rolling_mean(final_data.any(axis=1).resample('W', how='sum'), 4, min_periods = 1).plot(ax = ax[0])
ax[0].set_ylabel('#/week')

week_counts = final_data[['missionary', 'cowgirl', 'doggy', 'kinky']].resample('W', how = 'sum')
pd.rolling_mean(week_counts, 2, min_periods=1).plot(ax = ax[1])
ax[1].set_ylabel('#/week')
ax[1].set_ylim(0, 10);

week_ratings = final_data[['HerRanking', 'MyRanking']].resample('W', how='median')
pd.rolling_median(week_ratings, 4, min_periods = 3).plot(ax = ax[2])
ax[2].set_ylabel('Mean Satisfaction')
ax[2].set_ylim(4, 10);
fig.savefig('figures/frequency.png', dpi = 400)

# <codecell>

from statsmodels.tools.tools import maybe_unwrap_results
from statsmodels.graphics import utils
import statsmodels.formula.api as smf

def ccpr_data(results, exog_idx):
    
    exog_name, exog_idx = utils.maybe_name_or_idx(exog_idx, results.model)
    results = maybe_unwrap_results(results)
    
    x1 = results.model.exog[:, exog_idx]
    x1beta = x1*results.params[exog_idx]
    
    return x1, x1beta + results.resid
    

# <codecell>

from scipy.stats import linregress

eqns = [('b', 'MyRanking ~ PreOrgs + missionary + doggy + cowgirl + reversecowgirl + kinky + Stress'),
        ('r', 'HerRanking ~ PreOrgs + missionary + doggy + cowgirl + reversecowgirl + kinky + Stress')]
plot_cols = [('PreOrgs', 'Cont'),  
             ('Stress', 'Cont'),
             ('missionary', 'bool'), 
             ('doggy', 'bool'), 
             ('cowgirl', 'bool'), 
             ('reversecowgirl', 'bool'), 
             ('kinky', 'bool')]
groups = ['J1', 'J2', 'M']

fig, axs = plt.subplots(len(plot_cols), 3, figsize = (20, 20))

for color, endog in eqns:
    
    for axcol, g in enumerate(groups):
        tdata = final_data.query("Name == '%s'" % g)
        res = smf.ols(endog, data = tdata).fit()
        for ax, (val, typ) in zip(axs[:,axcol].flatten(), sorted(plot_cols)):
            #try:
            x, y = ccpr_data(res, val)
            #except ValueError:
            #    print 'bad error'
            #    continue
                
            if ax.is_first_row():
                ax.set_title(g)
            
            if typ == 'bool':
                tmp = pd.DataFrame({'X': x, 'y':y})
                try:
                    tmp.query('X == 1')['y'].plot(kind = 'kde', 
                                                  ax = ax, 
                                                  linewidth = 8, 
                                                  alpha = 0.4,
                                                  color = color, 
                                                  grid=False)
                except:
                    pass
                ax.set_xlim(-10, 10)
                if ax.is_last_row():
                    ax.set_xlabel('Rating')
                ax.set_ylabel('')
                ax.set_title(val)
                ax.vlines(0, *ax.get_ylim())
                ax.set_ylim(0, ax.get_ylim()[1])
            else:
                ax.scatter(x, y, alpha = 0.1, color = color, s=30)
                tup = linregress(x, y)
                m, b = tup[0], tup[1]
                xp = np.linspace(x.min(), x.max())
                ax.plot(xp, m*xp+b, color = color, linewidth = 10, alpha = 0.5)
                ax.set_ylim(-5, 5)
                ax.set_xlabel(val)
                ax.set_ylabel('Rating')
fig.tight_layout()
fig.savefig('figures/position_preference.png', dpi = 600)

# <codecell>

eqns = [('b', 'Me', 'MyRanking ~ PreOrgs + missionary + doggy + cowgirl + reversecowgirl + kinky + Stress'),
        ('r', 'Her', 'HerRanking ~ PreOrgs + missionary + doggy + cowgirl + reversecowgirl + kinky + Stress')]
#plot_cols = set(['PreOrg', 'missionary[T.True]', 'doggy[T.True]', 'cowgirl[T.True]', 'reversecowgirl[T.True]', 'kinky[T.True]'])
groups = ['J1', 'J2', 'M']

tres = []
for _, per, eqn in eqns:
    for g in groups:
        tdata = final_data.query("Name == '%s'" % g)
        res = smf.ols(eqn, data = tdata).fit()
        tmp = res.params.copy()
        tmp['Name'] = g
        tmp['Person'] = per
        tres.append(tmp.copy())

res_df = pd.DataFrame(tres)

# <codecell>

import matplotlib as mpl

tcols = sorted([c for c, _ in plot_cols])

cmap = mpl.cm.BrBG
norm = mpl.colors.Normalize(vmin=-5, vmax=5)

fig, axs = plt.subplots(3,1, figsize = (10, 10))
axs[1].imshow(res_df.query('Person == "Her"')[tcols].values,
           interpolation='nearest', norm=norm, aspect='auto', cmap = cmap)
axs[1].set_yticks([0, 1, 2])
axs[1].set_yticklabels(groups)
axs[1].set_title('Her Effect')
axs[1].set_xticks([])

axs[2].imshow(res_df.query('Person == "Me"')[tcols].values,
           interpolation='nearest', norm=norm, aspect='auto', cmap = cmap)
axs[2].set_yticks([0, 1, 2])
axs[2].set_yticklabels(groups)
axs[2].set_xticks(range(len(tcols)))
axs[2].set_xticklabels(tcols, rotation = 90)
axs[2].set_title('My Effect')

cb3 = mpl.colorbar.ColorbarBase(axs[0], cmap=cmap,
                                     norm=norm,
                                     extend='both',
                                     # Make the length of each extension
                                     # the same as the length of the
                                     # interior colors:
                                     extendfrac='auto',
                                     spacing='uniform',
                                     orientation='horizontal')
fig.tight_layout()
fig.savefig('figures/effect_heatmap.png', dpi = 400)

# <codecell>


