"""Validate expanded manuscript artifacts and package compilation sources.

Expected counts come from canonical LaTeX, not a fixed draft page/figure count.
Execution/testing is delegated to Antigravity under the current user instruction.
"""
import hashlib
import json
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree as ET
import pymupdf
from PIL import Image, ImageOps
from docx import Document
from build_manuscript_docx import analyze_source, expanded_source, without_comments, EXPECTED_AUTHORS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/research_draft_v2'

def hash_file(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def input_files(path,seen=None):
    seen=set() if seen is None else seen
    path=path.resolve()
    if not path.is_relative_to(OUT.resolve()):raise ValueError(f'Input outside manuscript: {path}')
    if path in seen:return seen
    seen.add(path)
    for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',without_comments(path.read_text(encoding='utf-8'))):
        target=path.parent/name
        if not target.suffix:target=target.with_suffix('.tex')
        input_files(target,seen)
    return seen

def replay_status():
    complete=OUT/'release_audit/full_policy_replay.json'
    if complete.exists():
        data=json.loads(complete.read_text(encoding='utf-8'))
        records=data.get('records',[])
        return {'source':str(complete.relative_to(OUT)),'policies':len(records),
                'slots_per_policy':data.get('slots_per_policy'),'all_match':data.get('all_match'),
                'scope':'Saved-policy evaluation replay only; not original training replay or historical working-tree recovery.'}
    bounded=OUT/'verification/replay_seed42_budget10000_slots1000.json'
    if bounded.exists():
        rows=json.loads(bounded.read_text(encoding='utf-8'))
        return {'source':str(bounded.relative_to(OUT)),'policies':len(rows),'slots_per_policy':1000,
                'scope':'Earlier bounded check; no all-policy completion artifact available.'}
    return {'policies':0,'scope':'No completed replay artifact available.'}

def main():
    source=expanded_source();expected=analyze_source(source)
    bibliography=(OUT/'references.bib').read_text(encoding='utf-8')
    citations={key.strip() for group in re.findall(r'\\cite(?:p|t)?(?:\[[^\]]*\])*\{([^}]+)\}',source) for key in group.split(',')}
    entries=set(re.findall(r'@\w+\{([^,]+)',bibliography))
    assert citations==entries,{'missing':sorted(citations-entries),'unused':sorted(entries-citations)}
    inventory=json.loads((OUT/'evidence_manifest.json').read_text(encoding='utf-8'))['files']
    mismatches=[]
    for row in inventory:
        path=ROOT/row['path']
        if not path.exists() or hash_file(path)!=row['sha256']:mismatches.append(row['path'])
    assert not mismatches,mismatches
    log=(OUT/'main.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Overfull|Citation .* undefined|Reference .* undefined|Missing character|^!',log,re.M)
    pdf=pymupdf.open(OUT/'main.pdf');text='\n'.join(page.get_text() for page in pdf)
    assert len(pdf)>0 and '??' not in text
    assert 'References' in text or 'REFERENCES' in text
    assert 'Rima Deka' in text,'Missing separate project-guide acknowledgment'
    word=Document(OUT/'main.docx')
    author_paragraphs=[p.text for p in word.paragraphs if p.style.name=='Author']
    assert author_paragraphs and all('Rima' not in p for p in author_paragraphs)
    names=' '.join(' '.join(author_paragraphs).split())
    assert all(name in names for name in EXPECTED_AUTHORS),author_paragraphs
    assert len(word.tables)==len(expected['tables']),(len(word.tables),len(expected['tables']))
    with zipfile.ZipFile(OUT/'main.docx') as archive:
        root=ET.fromstring(archive.read('word/document.xml'))
        ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math',
            'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'pic':'http://schemas.openxmlformats.org/drawingml/2006/picture'}
        native_math=len(root.findall('.//m:oMathPara',ns))
        drawings=len(root.findall('.//pic:pic',ns))
        media=[name for name in archive.namelist() if name.startswith('word/media/')]
        expected_hashes={hash_file(OUT/name) for name in expected['images']}
        embedded_hashes={hashlib.sha256(archive.read(name)).hexdigest() for name in media}
        assert native_math==len(expected['displays']),(native_math,len(expected['displays']))
        assert drawings==len(expected['images']),(drawings,len(expected['images']))
        assert embedded_hashes==expected_hashes,'Embedded Word figures differ from canonical source PNGs'
        word_text=' '.join(n.text or '' for n in root.findall('.//w:t',ns))
        assert 'Project Guide' in word_text and 'Rima Deka' in word_text
        assert '??' not in word_text and 'RBTABLECAPTION' not in word_text
    figure_captions=[p for p in word.paragraphs if p.text.startswith('Figure ') and p.style.name=='Image Caption']
    table_captions=[p for p in word.paragraphs if p.text.startswith('Table ') and p.style.name=='Image Caption']
    assert len(figure_captions)==len(expected['figures'])
    assert len(table_captions)==len(expected['tables'])
    verification=OUT/'verification';verification.mkdir(exist_ok=True)
    (verification/'pdf_extracted.txt').write_text(text,encoding='utf-8')
    thumbs=[]
    for i,page in enumerate(pdf):
        page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(verification/f'page_{i+1:02}.png')
        pix=page.get_pixmap(matrix=pymupdf.Matrix(.8,.8))
        image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
        thumbs.append(ImageOps.expand(image,border=6,fill='gray'))
    width=max(image.width for image in thumbs);height=max(image.height for image in thumbs)
    canvas=Image.new('RGB',(width*3,height*((len(thumbs)+2)//3)),(220,220,220))
    for i,image in enumerate(thumbs):canvas.paste(image,((i%3)*width,(i//3)*height))
    canvas.save(verification/'contact_sheet.png')
    files=set(input_files(OUT/'main.tex'))
    for name in ['main.pdf','main.docx','main.bbl','references.bib','README.md','AUTHOR_REVIEW_NOTES.md',
                 'claim_evidence.md','citation_audit.md','review_and_revision.md','verified_results.json','evidence_manifest.json']:
        path=OUT/name
        if not path.is_file():raise FileNotFoundError(path)
        files.add(path.resolve())
    # Preserve all vector figures; Word embeds its images in the docx itself.
    files.update(path.resolve() for path in (OUT/'figures').glob('*.pdf'))
    package=OUT/'source_package.zip'
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):archive.write(path,path.relative_to(OUT.resolve()))
    report={
        'date':'2026-11-18','compiler':'Tectonic (XeTeX/BibTeX); see preserved main.log for build details',
        'pages':len(pdf),'bibliography_entries':len(entries),'missing_or_unused_citations':[],
        'unresolved_reference_markers':0,'overfull_boxes':0,'underfull_box_warnings':len(re.findall('Underfull',log)),
        'source_and_evidence_hashes_checked':len(inventory),'pdf_sha256':hash_file(OUT/'main.pdf'),
        'source_package_sha256':hash_file(package),'word_sha256':hash_file(OUT/'main.docx'),
        'expected_source_display_equations':len(expected['displays']),'word_display_equations':native_math,
        'expected_source_figures':len(expected['figures']),'word_figure_captions':len(figure_captions),
        'word_image_instances':drawings,'word_embedded_figures':len(media),
        'expected_source_tables':len(expected['tables']),'word_tables':len(word.tables),
        'word_table_captions':len(table_captions),'authors':list(EXPECTED_AUTHORS),'guide_separate':True,
        'policy_replay':replay_status(),
        'checks':'Source/data inventory, source-derived counts, citations, compiled log, Word structure/assets, PDF extraction and rendered pages. Scientific validity and visual inspection are separate checks.'
    }
    (OUT/'BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
