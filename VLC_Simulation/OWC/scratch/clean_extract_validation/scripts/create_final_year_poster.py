"""Populate the supplied 36 x 24 inch template with verified project content."""
from pathlib import Path
import sys, json
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scratch/poster_deps'))
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT=ROOT/'supervisor_package/poster';OUT.mkdir(exist_ok=True)
P=Presentation(str(OUT/'Template.pptx'));s=P.slides[0]
for sh in list(s.shapes):
    el=sh._element;el.getparent().remove(el)
NAVY='18324E';BLUE='256B9A';LIGHT='EFF5FA';INK='20384C';TEAL='087E8B';GOLD='E4AF31'
def rgb(c):return RGBColor.from_string(c)
def rect(x,y,w,h,fill,line=None,rounded=False):
    a=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid();a.fill.fore_color.rgb=rgb(fill)
    if line:a.line.color.rgb=rgb(line)
    else:a.line.fill.background()
    if rounded:
        try:a.adjustments[0]=.06
        except Exception:pass
    return a
def text(x,y,w,h,txt,size=25,color=INK,bold=False,align=PP_ALIGN.LEFT):
    a=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=a.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(.03);tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(txt.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.alignment=align;p.space_after=Pt(size*.14);p.line_spacing=Pt(size*1.08)
        p.font.name='Aptos';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
    return a
def panel(x,y,h,title):
    rect(x,y,11.42,h,LIGHT,'C9D6E0',True);rect(x,y,11.42,.56,BLUE)
    text(x+.18,y+.07,11.05,.44,title,25,'FFFFFF',True)
def pic(path,x,y,w,h=None):
    if h is None:return s.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w))
    return s.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))

# University emblem: crop only the seal from the institutional MYBharat asset.
im=Image.open(OUT/'adtu_logo_reference.png');im.crop((145,350,485,681)).save(OUT/'adtu_seal.png')
rect(0,0,36,3.28,NAVY)
rect(.62,.34,2.48,2.48,'FFFFFF',rounded=True);pic(OUT/'adtu_seal.png',.72,.43,2.28,2.28)
text(3.35,.18,31.7,.45,'ASSAM DOWN TOWN UNIVERSITY  |  TEAM RUPOSHI BYTES',29,'C9E6F5',True,PP_ALIGN.CENTER)
text(3.35,.77,31.8,.68,'OPTICAL RIS-ASSISTED SECURE VISIBLE LIGHT COMMUNICATION',48,'FFFFFF',True,PP_ALIGN.CENTER)
text(3.35,1.47,31.8,.55,'Using Friendly Jamming and Deep Reinforcement Learning',41,'FFFFFF',True,PP_ALIGN.CENTER)
members='MAHIDUL AHASAN — ADTU/0/2023-27/BTCS/174     |     ATIKUR RAHMAN — ADTU/0/2023-27/BTCS/191\nMD AMIT HASAN ROBI — ADTU/0/2023-27/BTCS/210     |     MD SAMIUR RAHMAN TANIM — ADTU/0/2023-27/BTCS/212'
text(3.35,2.13,31.8,.60,members,21,'FFFFFF',False,PP_ALIGN.CENTER)
text(3.35,2.78,31.8,.38,'Guide: Dr. Rima Deka, Assistant Professor  |  Department of Electronics',25,'D9E9F7',False,PP_ALIGN.CENTER)

L=.56;C=12.29;R=24.02
panel(L,3.62,5.35,'1. ABSTRACT & KEYWORDS')
abstract=('Visible light communication can carry indoor data over LED light, but an unintended receiver may also collect the signal. Friendly jamming can reduce interception while adding interference at the legitimate receiver. This project extends a 2024 VLC friendly-jamming model with a six-mirror optical reconfigurable intelligent surface (RIS). A deep reinforcement learning controller selects four jammer weights and one of five mirror configurations. The simulator combines direct and finite specular reflected channels, including receiver field of view and optical-power bounds. We compare no RIS, fixed RIS and joint control in a static room using ten independent seeds. Training is separated from frozen greedy evaluation. Fixed RIS raises the mean evaluation secrecy rate from 1.3205 to 1.4978 bps/Hz, with a positive paired confidence interval. Joint control reaches 1.4565 bps/Hz, but its advantage is not statistically established. An interactive 3D demo links controls to Python calculations. Near-Bob and colocated cases expose limits under the tested settings.')
text(L+.24,4.42,10.94,3.96,abstract,20)
text(L+.24,8.51,10.94,.33,'Keywords: VLC • Optical RIS • Friendly jamming • DRL • Secrecy',20,TEAL,True)
panel(L,9.23,3.32,'2. PROBLEM STATEMENT & MOTIVATION')
text(L+.24,10.03,10.92,2.28,'• Indoor optical broadcasts may reach an eavesdropper (Eve).\n• Friendly jamming can also degrade the intended receiver (Bob).\n• A controllable mirror array may redirect useful light and change the jamming trade-off.\n• The study targets confidential indoor optical communication.',27)
panel(L,12.82,9.95,'3. OBJECTIVES & SCOPE')
text(L+.24,13.64,10.92,3.0,'• Add finite optical RIS paths to the VLC/FJ baseline.\n• Implement joint jammer and mirror control with CNN + DND learning.\n• Compare matched schemes using separate policy evaluation.\n• Record secrecy, Bob BER, cost and adverse cases.',28)
text(L+.24,16.75,10.92,.5,'MODEL & CONTROL',25,TEAL,True)
eqs=[r'$h_{uv}^{\mathrm{eff}}(q)=h_{uv}^{\mathrm{direct}}+h_{uv}^{\mathrm{RIS}}(q)$',r'$a_t=[w_1,w_2,w_3,w_4,\tilde{q}],\quad |\mathcal{A}|=5^4\times5=3125$',r'$r_t=c_s(t)-3.5\,p_e(t)-0.4\,E(t)$']
fig=plt.figure(figsize=(10.8,2.0),facecolor='#EFF5FA')
for i,e in enumerate(eqs):fig.text(.025,.79-i*.31,e,fontsize=22,color='#18324E')
fig.savefig(OUT/'poster_equations.png',dpi=300,bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)
pic(OUT/'poster_equations.png',L+.22,17.37,10.92,2.15)
text(L+.24,19.78,10.92,2.65,'Scope: static 5 × 5 × 3 m room; known Eve geometry; scalar DC optical model. The main comparison uses nonnegative L1 jammer cost. RIS actuation energy, body blockage and delay/ISI are excluded.\nE is model-defined jammer cost, not measured total hardware energy.',25)

panel(C,3.62,6.38,'4. PROPOSED METHODOLOGY / SYSTEM DESIGN')
def node(x,y,w,h,t,fill=BLUE):rect(x,y,w,h,fill,rounded=True);text(x+.06,y+.10,w-.12,h-.1,t,22,'FFFFFF',True,PP_ALIGN.CENTER)
def arrow(x1,y1,x2,y2,color=BLUE):
    a=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2));a.line.color.rgb=rgb(color);a.line.width=Pt(2.5)
    from pptx.oxml.xmlchemy import OxmlElement
    e=OxmlElement('a:tailEnd');e.set('type','triangle');a.line._get_or_add_ln().append(e)
node(C+.38,4.55,2.2,.72,'Alice LED');node(C+.38,6.0,2.2,.88,'4 friendly\njammers')
node(C+4.15,5.30,2.45,.92,'Optical RIS\n6 mirrors',TEAL)
node(C+8.45,4.55,2.3,.72,'Bob');node(C+8.45,6.22,2.3,.72,'Eve')
arrow(C+2.6,4.9,C+8.45,4.9);arrow(C+2.6,5.08,C+4.15,5.60,TEAL);arrow(C+2.6,6.43,C+4.15,5.98,TEAL)
arrow(C+6.6,5.6,C+8.45,5.04,TEAL);arrow(C+6.6,5.98,C+8.45,6.52,TEAL)
node(C+3.1,7.45,5.2,.77,'CNN + DND controller',NAVY)
arrow(C+3.1,7.83,C+1.47,6.88);arrow(C+5.7,7.45,C+5.7,6.22)
text(C+.25,8.51,10.92,1.17,'Direct + reflected gains → secrecy / BER / reward feedback.\nTrain controller → freeze learning → compare paired seeds.\nOne shared mirror configuration affects all optical links.',24)
panel(C,10.26,3.48,'5. IMPLEMENTATION / TECHNOLOGIES')
text(C+.24,11.07,10.92,2.3,'Python, NumPy, PyTorch and Matplotlib; local HTML/JavaScript interface.\nFinite specular mirror optics, receiver FoV and power bounds.\n625 jammer actions; 5 RIS patterns; 3,125 joint actions.\nBackend-linked 3D view, live controls and recorded-action replay.',26)

panel(C,14.0,8.77,'6. RESULTS & DISCUSSION')
d=json.loads((ROOT/'output_figures/ris/final_evaluation/ris_study_data.json').read_text())
schemes=['baseline','fixed_ris','joint_ris'];labels=['No RIS','Fixed RIS','Joint RIS'];colors=['#2769A3','#138A86','#B15C51']
fig,ax=plt.subplots(figsize=(10.7,3.55));fig.patch.set_facecolor('#EFF5FA');ax.set_facecolor('#EFF5FA')
for i,scheme in enumerate(schemes):
    rr=[r for r in d['runs'] if r['scheme']==scheme];vals=[np.mean(r['evaluation']['history']['secrecy_rate']) for r in rr]
    g=next(g for g in d['aggregates'] if g['scheme']==scheme);v=g['evaluation']['secrecy_rate'];ci=v['ci95']
    ax.scatter(np.linspace(i-.12,i+.12,len(vals)),vals,color=colors[i],s=35,alpha=.55,zorder=3)
    ax.errorbar(i,v['mean'],yerr=[[v['mean']-ci[0]],[ci[1]-v['mean']]],fmt='D',color=colors[i],capsize=9,markersize=9,lw=3,zorder=4)
    ax.text(i,2.04,f"{v['mean']:.4f}",ha='center',fontsize=17,fontweight='bold',color=colors[i])
ax.set_xticks(range(3),labels,fontsize=16);ax.set_ylabel('Secrecy rate (bps/Hz)',fontsize=15);ax.tick_params(axis='y',labelsize=13);ax.set_ylim(.75,2.2);ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
fig.tight_layout();fig.savefig(OUT/'poster_results.png',dpi=350,facecolor=fig.get_facecolor());plt.close(fig)
text(C+.24,14.82,10.92,.7,'Nominal L1 study: 10 seeds × 3 schemes\n2,000 training + 1,000 frozen evaluation slots/run',24)
pic(OUT/'poster_results.png',C+.22,15.62,10.98,3.65)
text(C+.24,19.40,10.92,1.13,'Dots: seed means. Diamonds: group means; bars: 95% CI.\nFixed − baseline: +0.1773 bps/Hz; paired 95% CI [0.0378, 0.3167].',24)
rect(C+.23,20.68,10.96,1.70,'DFEDF5',rounded=True)
text(C+.42,20.85,10.58,1.41,'Fixed RIS improves secrecy in this setting. Joint superiority is not established: joint − baseline CI [−0.0440, 0.3158]. Tested near-Bob and colocated cases give zero secrecy.',25,NAVY,True)

panel(R,3.62,9.65,'7. APPLICATION / USE CASE')
text(R+.24,4.43,10.92,1.1,'Indoor optical security study for offices, classrooms and laboratories. The local demo lets a user change positions, jamming weights and RIS configurations.',26)
im=Image.open(ROOT/'supervisor_package/figures/demo_3d_nominal.png');w,h=im.size
# Retain the 3D scene, remove navigation/header for poster readability.
im.crop((40,330,min(w-15,1230),min(h,960))).save(OUT/'poster_demo_crop.png')
pic(OUT/'poster_demo_crop.png',R+.25,5.8,10.92,5.65)
text(R+.24,11.67,10.92,1.18,'3D simulation screenshot: actual backend coordinates and mirror normals. Animated link paths are illustrative; they do not measure packets or propagation delay.',24)
panel(R,13.54,4.97,'8. CONCLUSION & FUTURE WORK')
text(R+.24,14.35,10.92,3.8,'Implemented optical RIS channels and joint FJ/RIS learning, with a working 3D demo and matched evaluation.\nFixed RIS benefits the nominal link; joint control remains a learning trade-off under the tested budget.\nNext: uncertain Eve geometry, broader position tests and more sample-efficient joint control.\nPublished 2024 curves are not reproduced; results are simulation-based.',26)
panel(R,18.78,2.57,'9. REFERENCES')
text(R+.24,19.57,10.92,1.56,'[1] “Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication,” IEEE TWC, 2024. DOI: 10.1109/TWC.2024.3458046.\n[2] A. Pritzel et al., “Neural Episodic Control,” ICML, 2017.',22)
panel(R,21.62,1.15,'ACKNOWLEDGEMENT')
text(R+.24,22.28,10.92,.35,'We thank Dr. Rima Deka and Assam down town University.',22)
text(.65,23.24,34.7,.42,'RUPOSHI BYTES  |  Department of Electronics  |  Final-year Project Poster Presentation  |  14 November 2026',23,BLUE,True,PP_ALIGN.CENTER)
P.save(OUT/'Ruposhi_Bytes_Project_Poster.pptx')
(OUT/'POSTER_NOTES.md').write_text('''# Poster delivery notes\n\nTemplate: C:/Users/victu/Downloads/Template.pptx. Original landscape size retained: 36 x 24 inches.\n\nProject title proposed from the agreed scope. Team/rolls and guide details are as supplied. Department label uses the provided Department of Electronics; no different student department was invented.\n\nResults recomputed from output_figures/ris/final_evaluation/ris_study_data.json. Mean/CI plot is frozen evaluation, nominal L1; three schemes, ten seeds. Joint superiority is not established.\n\nNative PowerPoint text, panels and architecture objects remain editable. Equations and scientific plot are high-resolution rendered assets; no LaTeX placeholders.\n\nLogo reference: university seal cropped from https://cdn-prod.mybharats.in/organization/DL-ns-efbbdbfe-5574-464f-b917-631576699f60_AdtUlogo2.png (institutional listing on MYBharat); official website logo also archived as adtu_official_logo.png. Original user-attached seal informed selection; no logo was invented.\n\nPrint at 100% on 36 x 24 inch stock or scale proportionally if the organizer requires another size. Verify member spellings and affiliations before printing.\n''',encoding='utf-8')
print(OUT/'Ruposhi_Bytes_Project_Poster.pptx')
