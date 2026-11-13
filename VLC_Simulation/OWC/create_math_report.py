"""Generate current calculated DOCX/PDF reports, with explicit reproduction limits."""
from pathlib import Path
import json
import textwrap
import numpy as np
from vlc import VLCConfig,VLCChannel
from vlc.bounds import compute_zero_forcing_beamformer,compute_theoretical_bounds,corollary_diagnostics
from vlc.secrecy import compute_secrecy_rate,compute_bob_ber,compute_energy_consumption,compute_system_utility


def current_report():
    c=VLCConfig();g=VLCChannel(c).get_all_channel_gains();ab,ae,jb,je=g
    w=compute_zero_forcing_beamformer(jb,je)
    cs=compute_secrecy_rate(*g,w,c);pe=compute_bob_ber(ab,jb,w,c)
    energy=compute_energy_consumption(w,c)
    high,low,upper,_=compute_theoretical_bounds(*g,c)
    rows=[('Simulation model',c.model),('Noise variance (Table I)',f'{c.noise_power_watts:.10e}'),
          ('Alice-Bob electrical gain',f'{ab:.10e}'),('Alice-Eve electrical gain',f'{ae:.10e}'),
          ('ZF weights',np.array2string(w,precision=8)),('ZF Bob residual',f'{jb@w:.10e}'),
          ('ZF Eve amplitude',f'{abs(je@w):.10e}'),('ZF secrecy rate',f'{cs:.10f} bps/Hz'),
          ('ZF BER',f'{pe:.10e}'),(f'Jamming cost ({c.energy_model})',f'{energy:.10f}'),
          ('ZF utility',f'{compute_system_utility(cs,pe,energy,c):.10f}'),
          ('Global rate upper bound',f'{high:.10f} bps/Hz'),('Independent BER lower bound',f'{low:.10e}'),
          ('Independent utility upper bound',f'{upper:.10f}')]
    notes=['Calculated for the paper-equation mode; not a certificate of published-curve reproduction. The separate physical mode is documented in PHYSICAL_MODEL.md.',
           'Eq.14 squares negative effective channels. Default energy is the nonnegative L1 interpretation of Eq.16; the printed signed sum remains opt-in.',
           'The global bounds are independently valid and need not be jointly attainable.',
           corollary_diagnostics(*g,c)['reason'],
           'Missing author code, SNR normalization and channel traces prevent a 100% numerical claim.',
           'The custom baselines are not implementations of references [20], [42], [43].',
           'See PAPER_REPRODUCTION.md and raw output_figures/fig*_data.json for assumptions and actual runs.']
    return rows,notes


def build_verification_document(output_path):
    from docx import Document
    rows,notes=current_report()
    doc=Document();doc.add_heading('Current VLC implementation: calculated report',0)
    doc.add_paragraph('Source: supplied 19 Sep 2024.pdf, DOI 10.1109/TWC.2024.3458046.')
    for note in notes:doc.add_paragraph(note)
    table=doc.add_table(rows=1,cols=2);table.rows[0].cells[0].text='Quantity';table.rows[0].cells[1].text='Calculated value'
    for label,value in rows:
        cells=table.add_row().cells;cells[0].text=label;cells[1].text=value
    doc.save(output_path)
    return rows,notes


def build_pdf(output_path,rows,notes):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(output_path) as pdf:
        fig=plt.figure(figsize=(8.27,11.69));fig.text(.08,.94,'Current VLC calculated report',fontsize=18)
        y=.89
        for note in notes:
            for line in textwrap.wrap(note,95):fig.text(.08,y,line,fontsize=9);y-=.019
            y-=.009
        y-=.02
        for label,value in rows:
            fig.text(.08,y,label,fontsize=9);fig.text(.5,y,value,fontsize=8);y-=.032
        pdf.savefig(fig);plt.close(fig)


if __name__=='__main__':
    out=Path(__file__).resolve().parent/'output_figures';out.mkdir(exist_ok=True)
    rows,notes=build_verification_document(out/'VLC_Current_Implementation_Report.docx')
    build_pdf(out/'VLC_Current_Implementation_Report.pdf',rows,notes)
    print('Generated current calculated reports in output_figures. No exact-reproduction certification is made.')
