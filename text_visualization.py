###
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import squarify
from collections import OrderedDict
from math import log, sqrt


from six.moves import cStringIO as StringIO

from bokeh.plotting import figure, show, output_file

###
df_beta = pd.read_excel('DSC_FINAL/data/NAVER_report.xlsx')
df_text = pd.read_excel('DSC_FINAL/data/NAVER_report_text.xlsx')
df = pd.merge(df_beta, df_text, how = 'outer')
df.columns


df1 = df.groupby(df.name)
data = pd.DataFrame(df1.mean()['beta'])
df2 = df1.sum()
df3 = df1.mean()
#data['view'] = df2['view']
#data['length'] = df2['length'] / df3['length']
data['pos'] = df3['pos'] / (df2['pos']+df2['neg']+df2['neut'])
data['neg'] = df3['neg'] / (df2['pos']+df2['neg']+df2['neut'])
data['neut'] = df3['neut'] / (df2['pos']+df2['neg']+df2['neut'])

data = data.drop(['메리츠종금'])

xxx = ['negative' if i < 0 else 'positive' for i in data['beta']]
data['beta'] = xxx

data = data.sort_values(["beta"], ascending=[False])

data.to_csv("kapital_beta.csv", mode='w')

########################
data = '''
name,beta,pos,neg,neut
미래에셋대우,positive,0.023357587261415163,0.019834536443204587,0.002262421749925704
IBK투자증권,positive,0.030954379437853043,0.02511286041605227,0.0027562895578593953
하나대투증권,positive,0.589247311827957,0.34838709677419355,0.06236559139784946
하나금융투자,positive,0.022905722624032485,0.015487882248445628,0.001606395127521888
케이프투자증권,positive,0.06129814024550866,0.04428112322849165,0.005531847637110795
이트레이드증권,positive,0.03934915935286031,0.028114095379084273,0.003965316696626837
이베스트투자증권,positive,0.03476640610798037,0.024188783857480457,0.0035448100345391747
이베스트증권,positive,0.0468739023533544,0.03224446786090622,0.004214963119072708
현대차증권,positive,0.016682984643924557,0.013919664021436668,0.001655415850767804
대신증권,positive,0.09335306449623874,0.0635713404858799,0.009742261684548033
LIG투자증권,positive,0.14951708766716196,0.08748142644873699,0.01300148588410104
KTB투자증권,positive,0.06165893271461717,0.05614849187935035,0.0071925754060324825
KDB대우증권,positive,0.07748940284078233,0.05841451624897746,0.00695322376738306
메리츠종금증권,negative,0.07836165825215102,0.05674464907914385,0.0077508355258479695
교보증권,negative,0.06022340942204954,0.046246829636824784,0.004640872052236792
키움증권,negative,0.04483169496574322,0.034207129381392115,0.004294508986197994
DB금융투자,negative,0.02490222168460949,0.020733034958267813,0.0019837909761703156
'''

###########################
drug_color = OrderedDict([
    ("pos",   "#0d3362"),
    ("neg", "#c64737"),
    ("neut",     "#340a58"  ),
])

gram_color = OrderedDict([
    ("negative", "#e69584"),
    ("positive", "#aeaeb8"),
])
    
df = pd.read_csv(StringIO(data),
                 skiprows=1,
                 skipinitialspace=True,
                 engine='python')

#################
width = 700 # 원 크기
height = 700 # 원 크기
inner_radius = 90
outer_radius = 300 - 10

minr = sqrt(log(.001 * 1E4))
maxr = sqrt(log(1 * 1E4))
a = (outer_radius - inner_radius) / (minr - maxr)
b = inner_radius - a * maxr

def rad(mic):
    return a * np.sqrt(np.log(mic * 1E4)) + b

big_angle = 2.0 * np.pi / (len(df) + 1)
small_angle = big_angle / 7

p = figure(plot_width=width, plot_height=height, title="",
    x_axis_type=None, y_axis_type=None,
    x_range=(-420, 420), y_range=(-420, 420),
    min_border=0, outline_line_color="black",
    background_fill_color="#f0e1d2")

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

# annular wedges
angles = np.pi/2 - big_angle/2 - df.index.to_series()*big_angle
colors = [gram_color[gram] for gram in df.beta]
p.annular_wedge(
    0, 0, inner_radius, outer_radius, -big_angle+angles, angles, color=colors,
)

# small wedges
p.annular_wedge(0, 0, inner_radius, rad(df.pos),
                -big_angle+angles+5*small_angle, -big_angle+angles+6*small_angle,
                color=drug_color['pos'])
p.annular_wedge(0, 0, inner_radius, rad(df.neg),
                -big_angle+angles+3*small_angle, -big_angle+angles+4*small_angle,
                color=drug_color['neg'])
p.annular_wedge(0, 0, inner_radius, rad(df.neut),
                -big_angle+angles+1*small_angle, -big_angle+angles+2*small_angle,
                color=drug_color['neut'])



# circular axes and lables
labels = np.array([0.001, 0.01, 0.1, 1])
radii = a * np.sqrt(np.log(labels * 1E4)) + b
p.circle(0, 0, radius=radii, fill_color=None, line_color="white")
p.text(0, radii[:-1], [str(r) for r in labels[:-1]],
       text_font_size="8pt", text_align="center", text_baseline="middle")

# radial axes
p.annular_wedge(0, 0, inner_radius-10, outer_radius+10,
                -big_angle+angles, -big_angle+angles, color="black")

# bacteria labels
xr = radii[0]*np.cos(np.array(-big_angle/2 + angles))
yr = radii[0]*np.sin(np.array(-big_angle/2 + angles))
label_angle=np.array(-big_angle/2+angles)
label_angle[label_angle < -np.pi/2] += np.pi # easier to read labels on the left side
p.text(xr, yr, df.name, angle=label_angle,
       text_font_size="9pt", text_align="center", text_baseline="middle")

# OK, these hand drawn legends are pretty clunky, will be improved in future release
p.circle([-40, -40], [-370, -390], color=list(gram_color.values()), radius=5)
p.text([-30, -30], [-370, -390], text=[gr + "-beta" for gr in gram_color.keys()],
       text_font_size="7pt", text_align="left", text_baseline="middle")

p.rect([-40, -40, -40], [18, 0, -18], width=30, height=13,
       color=list(drug_color.values()))
p.text([-15, -15, -15], [18, 0, -18], text=list(drug_color),
       text_font_size="9pt", text_align="left", text_baseline="middle")

output_file("DSC_FINAL/data/kapital1.html", title="kapital_beta_sent")

show(p)



