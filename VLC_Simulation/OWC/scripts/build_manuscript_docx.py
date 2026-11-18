"""Build an editable Word companion from canonical LaTeX.

Counts, labels and captions come from main.tex and its local inputs. Native
Word equations and rich caption content are retained. Run builds through
Antigravity under the user's current execution instruction.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile
from xml.etree import ElementTree as ET
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/research_draft_v2'
EXPECTED_AUTHORS=('Mahidul Ahasan','Atikur Rahman','Md Amit Hasan Robi','Md Samiur Rahman Tanim')

def without_comments(text):
    """Remove comments, leaving escaped percent characters intact."""
    lines=[]
    for line in text.splitlines():
        cut=len(line)
        for i,char in enumerate(line):
            if char!='%':continue
            backslashes=0;j=i-1
            while j>=0 and line[j]=='\\':backslashes+=1;j-=1
            if backslashes%2==0:cut=i;break
        lines.append(line[:cut])
    return '\n'.join(lines)

def group_at(text,start,opening='{',closing='}'):
    """Read a balanced TeX group, including nested and escaped braces."""
    if start>=len(text) or text[start]!=opening:raise ValueError('Expected balanced group')
    depth=1;i=start+1
    while i<len(text):
        char=text[i]
        if char=='\\':i+=2;continue
        if char==opening:depth+=1
        elif char==closing:
            depth-=1
            if depth==0:return text[start+1:i],i+1
        i+=1
    raise ValueError('Unclosed TeX group')

def command_argument(text,command):
    """Return (content, command start, argument end), allowing a short option."""
    match=re.search(r'\\'+re.escape(command)+r'(?![A-Za-z])\*?',text)
    if not match:return None
    pos=match.end()
    while pos<len(text) and text[pos].isspace():pos+=1
    if pos<len(text) and text[pos]=='[':
        _,pos=group_at(text,pos,'[',']')
        while pos<len(text) and text[pos].isspace():pos+=1
    value,end=group_at(text,pos)
    return value,match.start(),end

def expanded_source(path=None,active=()):
    path=(path or OUT/'main.tex').resolve()
    if path in active:raise ValueError(f'Recursive LaTeX input: {path}')
    if not path.is_relative_to(OUT.resolve()):raise ValueError(f'Input outside manuscript directory: {path}')
    text=without_comments(path.read_text(encoding='utf-8'))
    def expand(match):
        target=path.parent/match.group(1)
        if not target.suffix:target=target.with_suffix('.tex')
        return expanded_source(target,active+(path,))
    return re.sub(r'\\(?:input|include)\s*\{([^}]+)\}',expand,text)

def analyze_source(text):
    figures=[];tables=[];labels={};displays=[]
    for kind,target in [('figure',figures),('table',tables)]:
        pattern=r'\\begin\{'+kind+r'\*?\}(.*?)\\end\{'+kind+r'\*?\}'
        for number,match in enumerate(re.finditer(pattern,text,re.S),1):
            block=match.group(0);caption=command_argument(block,'caption')
            if caption is None:raise ValueError(f'{kind} {number} has no caption')
            target.append({'number':number,'caption':caption[0]})
            for label in re.findall(r'\\label\{([^}]+)\}',block):labels[label]=number
    # A paragraph in Word corresponds to each display environment. Numbered
    # multirow environments need explicit row labels/tags rather than guessing.
    if re.search(r'\\begin\{(?:align|gather|multline)\*?\}',text):
        raise ValueError('Use equation environments (with aligned inside if needed) for unambiguous Word numbering')
    equation_number=0
    pattern=r'\\begin\{(equation\*?|displaymath)\}(.*?)\\end\{\1\}|\\\[(.*?)\\\]'
    for match in re.finditer(pattern,text,re.S):
        numbered=match.group(1)=='equation'
        if numbered:equation_number+=1
        number=equation_number if numbered else None
        body=match.group(2) or match.group(3) or ''
        displays.append({'number':number,'source':body})
        if numbered:
            for label in re.findall(r'\\label\{([^}]+)\}',body):labels[label]=number
    images=[]
    for match in re.finditer(r'\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}',text):
        image=Path(match.group(1))
        if image.suffix.lower()=='.pdf':image=image.with_suffix('.png')
        images.append(str(image).replace('\\','/'))
    author=command_argument(text,'author')
    if author is None or 'Rima' in author[0]:raise ValueError('Four students must be authors; Dr. Rima Deka must remain separate as guide')
    for name in EXPECTED_AUTHORS:
        normalized=' '.join(author[0].replace('~',' ').split())
        if name not in normalized:raise ValueError(f'Missing student author: {name}')
    return {'figures':figures,'tables':tables,'displays':displays,'labels':labels,'images':images,'authors':EXPECTED_AUTHORS}

def modern_math(text):
    text=re.sub(r'\{\\rm\s+([^{}]*)\}',lambda m:'{\\mathrm{'+m.group(1)+'}}',text)
    return re.sub(r'\\(mathcal|mathbf)\s*([A-Za-z0-9])',lambda m:'\\'+m.group(1)+'{'+m.group(2)+'}',text)

def main():
    pandoc=next((ROOT/'.tools/pandoc').rglob('pandoc.exe'))
    reference=ROOT/'.tools/pandoc/manuscript_reference.docx'
    reference.write_bytes(subprocess.run([str(pandoc),'--print-default-data-file','reference.docx'],check=True,stdout=subprocess.PIPE).stdout)
    template=Document(reference);section=template.sections[0]
    section.page_width=Inches(8.27);section.page_height=Inches(11.69)
    section.top_margin=section.bottom_margin=Inches(.85)
    section.left_margin=section.right_margin=Inches(.85)
    for name in ['Normal','Body Text','First Paragraph','Bibliography','Image Caption','Table Caption']:
        if name in template.styles:
            style=template.styles[name];style.font.name='Times New Roman';style.font.size=Pt(10 if 'Caption' in name else 11)
            style.paragraph_format.space_after=Pt(5)
    for name in ['Title','Heading 1','Heading 2','Heading 3']:
        if name in template.styles:
            style=template.styles[name];style.font.name='Times New Roman';style.font.color.rgb=RGBColor(0,0,0)
            style.font.size=Pt(18 if name=='Title' else 13 if name=='Heading 1' else 11)
    template.save(reference)
    tex=expanded_source();expected=analyze_source(tex)
    # Pandoc's LaTeX reader may discard table float captions. Preserve each
    # caption as a marked ordinary paragraph before its float, so the same
    # Pandoc/citeproc conversion retains inline equations and citations.
    table_number=0
    def preserve_table_caption(match):
        nonlocal table_number
        table_number+=1;block=match.group(0);caption,start,end=command_argument(block,'caption')
        return f'\n\nRBTABLECAPTION{table_number:04d} '+caption+'\n\n'+block[:start]+block[end:]
    tex=re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}',preserve_table_caption,tex,flags=re.S)
    tex=re.sub(r'(figures/[^}]+)\.pdf',r'\1.png',tex)
    tex=re.sub(r'\\IEEEPARstart\{([^}]+)\}\{([^}]+)\}',r'\1\2',tex)
    tex=re.sub(r'\\eqref\{([^}]+)\}',lambda m:'('+str(expected['labels'][m.group(1)])+')',tex)
    tex=re.sub(r'\\ref\{([^}]+)\}',lambda m:str(expected['labels'][m.group(1)]),tex)
    tex=re.sub(r'\\label\{[^}]+\}','',tex)
    tex=re.sub(r'\\bibliographystyle\{[^}]+\}|\\bibliography\{[^}]+\}','',tex)
    verification=OUT/'verification';verification.mkdir(exist_ok=True)
    temp=verification/'word_source.tex';temp.write_text(modern_math(tex),encoding='utf-8')
    command=[str(pandoc),str(temp),'--from=latex','--to=docx','--standalone','--citeproc','--bibliography='+str(OUT/'references.bib'),'--csl='+str(verification/'ieee.csl'),'--reference-doc='+str(reference),'--resource-path='+str(OUT),'--metadata=reference-section-title:References','--output='+str(OUT/'main.docx')]
    result=subprocess.run(command,cwd=OUT,check=True,text=True,capture_output=True)
    (verification/'docx_build.log').write_text(result.stderr,encoding='utf-8')
    if 'Could not convert TeX math' in result.stderr:raise ValueError(result.stderr)
    word=Document(OUT/'main.docx');formulas=word.element.xpath('.//m:oMathPara/m:oMath')
    assert len(formulas)==len(expected['displays']),(len(formulas),len(expected['displays']))
    for formula,display in zip(formulas,expected['displays']):
        if display['number'] is None:continue
        run=OxmlElement('m:r');props=OxmlElement('m:rPr');props.append(OxmlElement('m:nor'));run.append(props)
        text=OxmlElement('m:t');text.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        text.text=f"   ({display['number']})";run.append(text);formula.append(run)
    figure_count=0;table_count=0
    for paragraph in word.paragraphs:
        if paragraph.style.name=='Image Caption':
            figure_count+=1
            # Insert a separate run; paragraph.text would erase OMML,
            # hyperlinks and citeproc fields already present in the caption.
            run=paragraph.add_run(f'Figure {figure_count}. ')
            paragraph._p.remove(run._r)
            insert=1 if paragraph._p.pPr is not None else 0
            paragraph._p.insert(insert,run._r)
        for node in paragraph._p.xpath('.//w:t'):
            if not node.text:continue
            match=re.search(r'RBTABLECAPTION(\d{4})',node.text)
            if match:
                number=int(match.group(1));table_count+=1
                node.text=node.text.replace(match.group(0),f'Table {number}.',1)
                paragraph.style='Image Caption';paragraph.paragraph_format.keep_with_next=True
    assert figure_count==len(expected['figures']),(figure_count,len(expected['figures']))
    assert table_count==len(expected['tables']) and len(word.tables)==len(expected['tables']),(table_count,len(word.tables),len(expected['tables']))
    authors=[p.text for p in word.paragraphs if p.style.name=='Author']
    assert authors and all('Rima' not in p for p in authors),authors
    normalized=' '.join(' '.join(authors).split())
    assert all(name in normalized for name in EXPECTED_AUTHORS),authors
    word.save(OUT/'main.docx')
    with zipfile.ZipFile(OUT/'main.docx') as archive:
        root=ET.fromstring(archive.read('word/document.xml'))
        ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','pic':'http://schemas.openxmlformats.org/drawingml/2006/picture'}
        math=len(root.findall('.//m:oMath',ns));display_math=len(root.findall('.//m:oMathPara',ns))
        drawings=len(root.findall('.//pic:pic',ns))
        media=[name for name in archive.namelist() if name.startswith('word/media/')]
        expected_hashes={hashlib.sha256((OUT/path).read_bytes()).hexdigest() for path in expected['images']}
        actual_hashes={hashlib.sha256(archive.read(path)).hexdigest() for path in media}
        text=' '.join(n.text or '' for n in root.findall('.//w:t',ns))
        assert display_math==len(expected['displays']) and drawings==len(expected['images'])
        assert actual_hashes==expected_hashes,'Word image assets differ from source PNGs'
        assert 'Project Guide' in text and 'Rima Deka' in text and '??' not in text
        assert 'RBTABLECAPTION' not in text,'Unresolved table-caption marker'
    summary={'source_figure_count':len(expected['figures']),'source_table_count':len(expected['tables']),
             'source_display_equations':len(expected['displays']),'word_display_equations':display_math,
             'word_math_expressions':math,'word_image_instances':drawings,'word_unique_media':len(media),
             'author_paragraphs':authors,'guide_separate':True,'caption_rich_content_preserved':True,
             'source_sha256':hashlib.sha256((OUT/'main.tex').read_bytes()).hexdigest()}
    (verification/'docx_structure.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('Word built:',OUT/'main.docx');print(json.dumps(summary,indent=2))
    if result.stderr:print('Pandoc warnings:',result.stderr[:1600])

if __name__=='__main__':main()
