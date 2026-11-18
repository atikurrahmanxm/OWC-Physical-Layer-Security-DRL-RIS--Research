"""Draw system geometry and controller workflow as vector scientific figures."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/research_draft_v2/figures'

def save(fig,name):
    for ext in ('pdf','png'):
        fig.savefig(OUT/f'{name}.{ext}',dpi=250,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def main():
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig=plt.figure(figsize=(7.2,4.1))
    ax=fig.add_axes([0,.06,.72,.90],projection='3d')
    floor=[[(0,0,0),(5,0,0),(5,5,0),(0,5,0)]]
    ax.add_collection3d(Poly3DCollection(floor,facecolors='#edf2f6',alpha=.55,edgecolors='#adb8c3',linewidths=.7))
    for x in (0,5):
        for y in (0,5): ax.plot([x,x],[y,y],[0,3],color='#aebac5',lw=.7)
    for z in (0,3):
        ax.plot([0,5,5,0,0],[0,0,5,5,0],[z]*5,color='#aebac5',lw=.7)
    alice=np.array([2.5,2.5,3.]);bob=np.array([1.8,1.6,.85]);eve=np.array([3.2,3.4,.85]);ris=np.array([2.5,.25,2.6])
    jammers=[(1.5,1.5,3),(1.5,3.5,3),(3.5,1.5,3),(3.5,3.5,3)]
    def point(p,label,c,marker,offset):
        ax.scatter(*p,color=c,s=65,marker=marker,depthshade=False,edgecolors='white',linewidths=.6)
        ax.text(*(np.array(p)+offset),label,color=c,fontsize=9,weight='bold')
    point(alice,'Alice','#194e84','*',np.array([.1,.1,.20]))
    point(bob,'Bob','#00754e','o',np.array([-.40,-.16,-.20]))
    point(eve,'Eve','#ae3544','o',np.array([.12,.12,-.12]))
    for i,p in enumerate(jammers): point(p,f'J{i+1}','#b16d16','s',np.array([-.20,-.13,.18]))
    # Nominal panel envelope and six actual-size square facets at their centers.
    ax.add_collection3d(Poly3DCollection([[(2,.25,2.35),(3,.25,2.35),(3,.25,2.85),(2,.25,2.85)]],facecolors='#cce3db',edgecolors='#438574',alpha=.40))
    side=.159099
    for z in (2.475,2.725):
        for x in (2+1/6,2.5,3-1/6):
            h=side/2
            ax.add_collection3d(Poly3DCollection([[(x-h,.24,z-h),(x+h,.24,z-h),(x+h,.24,z+h),(x-h,.24,z+h)]],facecolors='#438574',edgecolors='white',linewidths=.4))
    ax.text(1.85,-.05,2.9,'Optical RIS',fontsize=9,color='#225e50',weight='bold')
    def path(a,b,c,ls='-',lw=1.6):
        a,b=np.asarray(a),np.asarray(b)
        ax.plot(*np.array([a,b]).T,color=c,ls=ls,lw=lw)
        v=(b-a)*.10; origin=b-v
        ax.quiver(*origin,*v,color=c,arrow_length_ratio=.65,linewidth=.8)
    path(alice,bob,'#2878ad');path(alice,eve,'#ae3544','--')
    path(alice,ris,'#23846e',lw=2);path(ris,bob,'#23846e',lw=2)
    path(jammers[3],eve,'#bf831f',':');path(jammers[3],bob,'#bf831f',':')
    ax.set(xlim=(0,5),ylim=(0,5),zlim=(0,3.45),xlabel='x (m)',ylabel='y (m)',zlabel='z (m)')
    ax.set_xticks([0,2.5,5]);ax.set_yticks([0,2.5,5]);ax.set_zticks([0,.85,3]);ax.view_init(elev=23,azim=-58);ax.set_box_aspect((5,5,3.5));ax.grid(False)
    for axis in (ax.xaxis,ax.yaxis,ax.zaxis): axis.pane.fill=False
    lx=.75
    fig.text(lx,.86,'Nominal room',fontsize=10,weight='bold')
    fig.text(lx,.75,'5 × 5 × 3 m\nFour ceiling jammers\nUpward-facing receivers',fontsize=8.5,linespacing=1.5)
    legends=[('#2878ad','—','Alice → Bob'),('#ae3544','--','Alice → Eve'),('#23846e','—','Alice → RIS → Bob'),('#bf831f','···','Jammer paths')]
    for i,(c,s,t) in enumerate(legends):
        y=.57-i*.075
        fig.text(lx,y,s,color=c,fontsize=13,weight='bold');fig.text(lx+.055,y,t,fontsize=8.2)
    fig.text(lx,.14,'Six facets; ρ = 0.85\nPanel center:\n(2.5, 0.25, 2.6) m',fontsize=8.4,linespacing=1.4)
    fig.text(.08,.005,'Representative paths only; facet orientation is schematic.',fontsize=8,color='#4a535b')
    save(fig,'fig_system_model')

    fig,ax=plt.subplots(figsize=(7.2,3.1))
    ax.set(xlim=(0,12),ylim=(0,5));ax.axis('off')
    def box(x,y,w,h,text,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.10,rounding_size=0.09',facecolor=color,edgecolor='#456070',lw=.9))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=8.2,linespacing=1.35)
    def arrow(a,b,label=None,rad=0):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,color='#425969',lw=1,connectionstyle=f'arc3,rad={rad}'))
        if label: ax.text((a[0]+b[0])/2+.12,(a[1]+b[1])/2+.12,label,ha='left',fontsize=7.5)
    box(.25,3.1,2.8,1.05,'Observation + 11-step history\nPrevious BER, secrecy, cost;\ninstalled Alice–Bob gain','#edf3f8')
    box(4.1,3.1,2.6,1.05,'CNN feature extractor\n11 × 11 padded input\n180-value feature key','#edf3f8')
    box(7.8,3.1,3.5,1.05,'Action-indexed DND\nEstimate Q; ε-greedy in training\nGreedy in frozen evaluation','#edf3f8')
    box(7.8,.75,3.5,1.15,'Selected action\nFour jammer weights w\nJoint only: RIS index q','#e8f4ed')
    box(4.1,.75,2.6,1.15,'Optical environment\nDirect + reflected gains\nShared facet normals','#e8f4ed')
    box(.25,.75,2.8,1.15,'Metric calculation\nSecrecy, Bob BER, L1 cost\nUtility U and next observation','#fff3e0')
    arrow((3.15,3.62),(4,3.62));arrow((6.8,3.62),(7.7,3.62));arrow((9.55,3),(9.55,2))
    arrow((7.7,1.32),(6.8,1.32));arrow((4,1.32),(3.15,1.32));arrow((1.65,2),(1.65,3),'next state')
    ax.plot([1.65,1.65,11.65,11.65],[.65,.23,.23,4.55],color='#6c7780',ls='--',lw=.85)
    arrow((11.65,4.55),(9.55,4.55));arrow((9.55,4.55),(9.55,4.25))
    ax.plot([9.55,5.4],[4.55,4.55],color='#6c7780',ls='--',lw=.85)
    arrow((5.4,4.55),(5.4,4.25))
    ax.text(6.2,.30,'Utility / replay updates during training only',ha='center',fontsize=8,color='#57636d')
    ax.text(5.9,4.72,'Known scenario geometry defines the RIS codebook before each run',ha='center',fontsize=8,color='#57636d')
    fig.tight_layout(pad=.4)
    save(fig,'fig_control_workflow')
    print('Created vector PDF and PNG system-model and controller figures.')

if __name__=='__main__': main()
