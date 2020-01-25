import sys

sys.executable

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

h40 = pd.read_csv("C://Users/zcole/my_projects/wx_maps/inputs/csv_hok_13-17/psam_h40.csv")

pma = gpd.read_file("C://Users/zcole/my_projects/wx_maps/inputs/tl_2017_40_puma10/tl_2017_40_puma10.shp")

h40['ele'] = h40.ADJHSG / 1000000 * h40.ELEP[(h40.ELEP >= 3)]
h40['gas'] = h40.ADJHSG / 1000000 * h40.GASP[(h40.GASP >= 4)]
h40['ful'] = h40.ADJHSG / 1000000 * h40.FULP[(h40.FULP >= 3)] / 12

h40['hia'] = h40.ADJINC / 1000000 * h40.HINCP

h40['ree'] = h40.ele + h40.gas + h40.ful
h40['reb'] = h40.ree / h40.hia

h40['pov'] = h40.hia - 24120
h40['p'] = h40.pov / 8360

nvh = h40[(h40.NP >= 1)]

lin = nvh[nvh.NP >= nvh.p]

hreu = lin[lin.ree > lin.ree.median()]

hebh = lin[lin.reb > lin.reb.median()]

hesdr = hreu.loc[:,'WGTP1':'WGTP80'].groupby(hreu.PUMA).sum()
hesdr['WGTP'] = hreu.loc[:,'WGTP'].groupby(hreu.PUMA).sum()

dif = hesdr.sub(hesdr.WGTP, axis=0)

sqd = dif * dif

var = sqd.loc[:,'WGTP1':'WGTP80'].sum(axis=1) * 0.05

ser = var ** (0.5)

moe90 = ser * 1.645

ci90up = hesdr.WGTP + moe90

ci90lo = hesdr.WGTP - moe90

hesdr['var'] = var
hesdr['ser'] = ser
hesdr['moe90'] = moe90
hesdr['ci90up'] = ci90up
hesdr['ci90lo'] = ci90lo

df = pd.DataFrame({'estimate':hesdr.WGTP,
                   'variance':var,
                   'standard-error':ser,
                   'moe-90':moe90,
                   'ci-90-lower':ci90lo,
                   'ci-90-upper':ci90up})

pma['PUMA'] = pma.PUMACE10.str.lstrip('00').astype('int64')

dfin = pd.merge(pma, 
                df, 
                how='left', 
                on='PUMA')

fig, ax = plt.subplots(figsize=(40, 40), subplot_kw={'aspect':'equal'})

dfin.plot(column='estimate',
          cmap='YlGn',
          legend=False,
          ax=ax,
          edgecolor='white',
          k=56,
          linewidth=4)

ax.set_axis_off()

plt.title("High Residential Energy Users: 2013-2017 ACS 5-Year PUMS", fontsize=40)

plt.show()

dfin[['PUMA','NAMELSAD10','estimate','variance','standard-error','moe-90','ci-90-lower','ci-90-upper']].sort_values(by=['estimate'], ascending=False).to_csv("C://Users/zcole/my_projects/wx_maps/outputs/acs-pums_13-17/hreu_acs-pums-40_13-17_FIN2.csv")