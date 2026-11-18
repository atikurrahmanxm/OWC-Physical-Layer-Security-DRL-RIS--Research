"""Generate verified bibliography and readable Markdown companion to main.tex."""
from pathlib import Path
import html
import json
import re
from build_manuscript_docx import expanded_source, analyze_source, command_argument

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/research_draft_v2'
ENTRIES={
 'liu2024smart':'10.1109/TWC.2024.3458046',
 'pathak2015visible':'10.1109/COMST.2015.2476474',
 'bloch2008wireless':'10.1109/TIT.2008.921908',
 'qian2021secure':'10.1109/ICC42927.2021.9500409',
 'saifaldeen2022drl':'10.1109/JPHOT.2022.3178852',
 'liu2026oris':'10.1109/TWC.2026.3708130',
}

def escape(s):
    return html.unescape(str(s)).replace('&',r'\&').replace('_',r'\_').replace('%',r'\%')

def main():
    bib=[]
    readable=[]
    for key,doi in ENTRIES.items():
        j=json.loads((OUT/'verification'/(doi.replace('/','_')+'.json')).read_text(encoding='utf-8'))
        author=' and '.join(f"{a['family']}, {a.get('given','')}" for a in j['author'])
        title=j['title'][0]
        year=j['published']['date-parts'][0][0]
        conference=j['type']=='proceedings-article'
        fields={'author':author,'title':'{'+title+'}', 'booktitle' if conference else 'journal':j['container-title'][0], 'year':year,'doi':doi}
        for f in ['volume','issue','page']:
            if f in j: fields[{'issue':'number','page':'pages'}.get(f,f)]=j[f].replace('-','--') if f=='page' else j[f]
        bib.append('@'+('inproceedings' if conference else 'article')+'{'+key+',\n'+',\n'.join(f'  {k} = {{{escape(v)}}}' for k,v in fields.items())+'\n}')
        readable.append(f'- [{key}] {author.replace(" and ", "; ")}. {title}. {j["container-title"][0]}, {year}. https://doi.org/{doi}')
    bib.append(r'''@inproceedings{pritzel2017neural,
  author={Pritzel, Alexander and Uria, Benigno and Srinivasan, Sriram and Puigdom{\`e}nech Badia, Adri{\`a} and Vinyals, Oriol and Hassabis, Demis and Wierstra, Daan and Blundell, Charles},
  title={Neural Episodic Control},
  booktitle={Proceedings of the 34th International Conference on Machine Learning},
  series={Proceedings of Machine Learning Research},
  volume={70}, pages={2827--2836}, year={2017},
  url={https://proceedings.mlr.press/v70/pritzel17a.html}
}''')
    (OUT/'references.bib').write_text('\n\n'.join(bib)+'\n',encoding='utf-8')
    readable.append('- [pritzel2017neural] A. Pritzel et al. Neural Episodic Control. PMLR 70:2827–2836, 2017. https://proceedings.mlr.press/v70/pritzel17a.html')
    tex=expanded_source()
    source_labels=analyze_source(tex)['labels']
    title=re.search(r'\\title\{([^}]+)\}',tex).group(1)
    body=tex.split(r'\begin{abstract}',1)[1].split(r'\bibliographystyle',1)[0]
    body='## Abstract\n\n'+body
    body=body.replace(r'\end{abstract}','').replace(r'\begin{IEEEkeywords}','\nKeywords: ').replace(r'\end{IEEEkeywords}','')
    body=re.sub(r'\\IEEEPARstart\{([^}]+)\}\{([^}]+)\}',r'\1\2',body)
    body=re.sub(r'\\section\*?\{([^}]+)\}',r'\n## \1\n',body)
    body=re.sub(r'\\subsection\{([^}]+)\}',r'\n### \1\n',body)
    counter=[0]; labels={}
    for match in re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}',body,re.S):
        counter[0]+=1
        lab=re.search(r'\\label\{([^}]+)\}',match.group(1))
        if lab: labels[lab.group(1)]=str(counter[0])
    body=re.sub(r'\\eqref\{([^}]+)\}',lambda m:'('+labels.get(m.group(1),m.group(1))+')',body)
    body=re.sub(r'\\label\{[^}]+\}','',body)
    body=body.replace(r'\begin{equation}','\n$$\n').replace(r'\end{equation}','\n$$\n')
    body=re.sub(r'\\cite\{([^}]+)\}',lambda m:'['+', '.join(m.group(1).split(','))+']',body)
    body=re.sub(r'\\ref\{([^}]+)\}',lambda m:str(source_labels.get(m.group(1),m.group(1))),body)
    results=json.loads((OUT/'verified_results.json').read_text())
    def table(m):
        text=m.group(0)
        caption=command_argument(text,'caption')[0]
        tabular=re.search(r'\\begin\{tabular\}\{[^}]+\}(.*?)\\end\{tabular\}',text,re.S)
        if tabular:
            raw=re.sub(r'\\(?:toprule|midrule|bottomrule)\b','',tabular.group(1))
            cells=[[cell.strip() for cell in row.strip().split('&')] for row in raw.split('\\\\') if '&' in row]
            if cells:
                lines=['| '+' | '.join(cells[0])+' |','| '+' | '.join(['---']*len(cells[0]))+' |']
                lines+=['| '+' | '.join(row)+' |' for row in cells[1:]]
                return '\n'+caption+'\n\n'+'\n'.join(lines)+'\n'
        raise ValueError('Could not convert manuscript table to Markdown')
    body=re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}',table,body,flags=re.S)
    def figure(m):
        name=re.search(r'\{(figures/[^}]+)\}',m.group(0)).group(1).replace('.pdf','.png')
        cap=command_argument(m.group(0),'caption')[0]
        return f'\n![{cap}]({name})\n'
    body=re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}',figure,body,flags=re.S)
    body=body.replace(r'\%', '%').replace('~',' ').replace('---','—').replace('--','–')
    intro='# '+title.replace('--','–')+'\n\nAuthors: Mahidul Ahasan; Atikur Rahman; Md Amit Hasan Robi; Md Samiur Rahman Tanim.\n\nProject Guide: Dr. Rima Deka, Assistant Professor, Department of Electronics, Assam down town University.\n\nGenerated reading companion to `main.tex`; edit that source and rerun `scripts/build_manuscript_sources.py` to keep the two versions synchronized. Author details remain provisional.\n\n'
    (OUT/'draft.md').write_text(intro+body+'\n## References\n\n'+'\n'.join(readable)+'\n',encoding='utf-8')
    print('Generated bibliography (7 primary-source-checked entries) and Markdown companion.')

if __name__=='__main__': main()
