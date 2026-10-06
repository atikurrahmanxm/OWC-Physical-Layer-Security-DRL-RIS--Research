import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from latex2mathml.converter import convert as latex2mathml_convert
from lxml import etree
import pymupdf
import win32com.client

# Initialize XSLT for OMML conversion
xslt_path = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
xslt = etree.parse(xslt_path)
transform = etree.XSLT(xslt)

def latex_to_omml(latex_code):
    """Converts LaTeX math string to native Microsoft Word OMML XML element."""
    mathml = latex2mathml_convert(latex_code)
    dom = etree.fromstring(mathml)
    omml = transform(dom)
    return omml.getroot()

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}" w:val="clear"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=30, bottom=30, left=60, right=60):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_equation_box(doc, latex_str, eq_num_str):
    """Inserts a compact native Microsoft Word Equation inside a styled card with equation numbering."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.autofit = False
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    c1, c2 = tbl.rows[0].cells[0], tbl.rows[0].cells[1]
    c1.width = Inches(6.4)
    c2.width = Inches(0.7)
    
    for c in [c1, c2]:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F4F8FA" w:val="clear"/>')
        c._element.get_or_add_tcPr().append(shd)
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="25" w:type="dxa"/><w:bottom w:w="25" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tcMar>')
        c._element.get_or_add_tcPr().append(tcMar)
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        c._element.get_or_add_tcPr().append(borders)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_eq = c1.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq.paragraph_format.space_before = Pt(1)
    p_eq.paragraph_format.space_after = Pt(1)
    omml_elem = latex_to_omml(latex_str)
    p_eq._element.append(omml_elem)

    p_num = c2.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(1)
    p_num.paragraph_format.space_after = Pt(1)
    r = p_num.add_run(eq_num_str)
    r.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(16, 44, 87)

    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_before = Pt(0)
    p_sep.paragraph_format.space_after = Pt(1)

def build_complete_report_with_nomenclature():
    doc = docx.Document()

    # Page Margins (0.55 in)
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.55)
        section.right_margin = Inches(0.55)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(9.5)
    normal_style.font.color.rgb = RGBColor(40, 40, 40)
    normal_style.paragraph_format.line_spacing = 1.1
    normal_style.paragraph_format.space_after = Pt(2)

    NAVY = RGBColor(16, 44, 87)
    TEAL = RGBColor(0, 128, 128)
    DARK_GRAY = RGBColor(70, 70, 70)
    WHITE = RGBColor(255, 255, 255)

    # ==================== PAGE 1: TITLE & OVERVIEW ====================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(1)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("Deep Reinforcement Learning-Based Physical Layer Security of OWC Systems")
    r_t.font.size = Pt(16.5)
    r_t.font.bold = True
    r_t.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(5)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s = p_sub.add_run("Technical Research Report & Mathematical Framework: Wall Optical RIS (O-RIS) + Cooperative Friendly Jamming")
    r_s.font.size = Pt(10)
    r_s.font.italic = True
    r_s.font.color.rgb = TEAL

    # Meta Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in meta_table.rows:
        for c in r.cells:
            set_cell_background(c, "F0F4F8")
            set_cell_margins(c, 30, 30, 80, 80)
    meta_table.rows[0].cells[0].paragraphs[0].add_run("Domain: Optical Wireless Communications (OWC / VLC)").bold = True
    meta_table.rows[0].cells[1].paragraphs[0].add_run("Optimization: Continuous Actor-Critic DRL (DDPG)").bold = True
    meta_table.rows[1].cells[0].paragraphs[0].add_run("Key Novelty: Side-Wall O-RIS + Cooperative Ceiling Jamming").italic = True
    meta_table.rows[1].cells[1].paragraphs[0].add_run("Submission: Academic Project Technical Report & Defense").italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(3)

    # Section 1
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(2)
    h1.paragraph_format.space_after = Pt(2)
    r_h1 = h1.add_run("1. Executive Summary & Research Motivation")
    r_h1.font.size = Pt(12)
    r_h1.font.bold = True
    r_h1.font.color.rgb = NAVY

    doc.add_paragraph(
        "Optical Wireless Communication (OWC), utilizing Visible Light Communication (VLC), offers multi-gigabit throughput, "
        "immunity to radio frequency (RF) electromagnetic interference, and access to vast license-free optical spectrum. However, because indoor ceiling luminaires "
        "emit wide-angle Lambertian beams to provide uniform illumination, confidential optical signals are broadcast indiscriminately across the room. "
        "Any unauthorized photodiode receiver (Eve) can overhear transmissions without physical detection."
    )
    doc.add_paragraph(
        "Physical Layer Security (PLS) guarantees information-theoretic, unconditional secrecy without upper-layer encryption overhead by exploiting spatial channel "
        "divergence between legitimate user Bob and eavesdropper Eve. This project implements the foundational security architecture of the IEEE Transactions on "
        "Wireless Communications (Sep 2024) paper and significantly advances it through two complementary physical layer mechanisms:"
    )

    b1 = doc.add_paragraph(style='List Bullet')
    b1.paragraph_format.space_after = Pt(1.5)
    b1.add_run("1. Cooperative Friendly Jamming (FJ): ").bold = True
    b1.add_run("Four distributed ceiling anchors radiate optimized artificial optical noise to drown out eavesdroppers without needing eavesdropper CSI.")

    b2 = doc.add_paragraph(style='List Bullet')
    b2.paragraph_format.space_after = Pt(1.5)
    b2.add_run("2. Optical Reconfigurable Intelligent Surface (O-RIS): ").bold = True
    b2.add_run("A wall array of 16–64 micro-mirrors steers an anomalous concentrated pencil-beam (directivity g_dir ≈ 131.6) to Bob, bypassing human blockage and near-user jamming spillover.")

    b3 = doc.add_paragraph(style='List Bullet')
    b3.paragraph_format.space_after = Pt(3)
    b3.add_run("3. Continuous Actor-Critic DRL: ").bold = True
    b3.add_run("Jointly optimizes high-dimensional continuous jamming powers and RIS reflection phases in real-time (< 1.2 ms).")

    # Section 2 + Fig 1
    h2 = doc.add_heading(level=1)
    h2.paragraph_format.space_before = Pt(2)
    h2.paragraph_format.space_after = Pt(2)
    r_h2 = h2.add_run("2. Indoor Geometry & Spatial Configuration")
    r_h2.font.size = Pt(12)
    r_h2.font.bold = True
    r_h2.font.color.rgb = NAVY

    split_tbl = doc.add_table(rows=1, cols=2)
    split_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_left, c_right = split_tbl.rows[0].cells[0], split_tbl.rows[0].cells[1]
    c_left.width = Inches(4.35)
    c_right.width = Inches(2.85)
    for c in [c_left, c_right]:
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        c._element.get_or_add_tcPr().append(borders)
        set_cell_margins(c, 10, 10, 30, 30)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_gl = c_left.paragraphs[0]
    p_gl.add_run("Room Dimensions: 5.0m × 5.0m × 3.0m\n").bold = True
    p_gl.add_run("• Alice (Ceiling Tx): (2.50, 2.50, 3.00) m, 80 LEDs, Pt = 1.0W, semi-angle φ = 60°.\n")
    p_gl.add_run("• J1-J4 (Ceiling Jammers): (1.25, 1.25), (1.25, 3.75), (3.75, 1.25), (3.75, 3.75) m.\n")
    p_gl.add_run("• Bob (Legitimate Rx): (1.80, 1.60, 0.85) m, PD Area = 1.0 cm², FOV = 75°, R_PD = 0.54 A/W.\n")
    p_gl.add_run("• Eve 1 (Distant Eve): (3.20, 3.40, 0.85) m; Eve 2 (Near Bob): (1.95, 1.75, 0.85) m.\n")
    p_gl.add_run("• Wall O-RIS: (2.50, 5.00, 2.60) m, 16–64 elements, divergence cone θ_div = 10°.")

    fig6_path = os.path.join(r"d:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\figures", "fig6_3d_indoor_setup.png")
    if os.path.exists(fig6_path):
        p_gr = c_right.paragraphs[0]
        p_gr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_img = p_gr.add_run()
        run_img.add_picture(fig6_path, width=Inches(2.75))
        p_cap = c_right.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        r_c = p_cap.add_run("Fig. 1: 3D System Architecture")
        r_c.font.size = Pt(8)
        r_c.font.italic = True
        r_c.font.color.rgb = DARK_GRAY

    # ==================== PAGE BREAK TO PAGE 2: NOMENCLATURE ====================
    doc.add_page_break()

    h_nom = doc.add_heading(level=1)
    h_nom.paragraph_format.space_before = Pt(0)
    h_nom.paragraph_format.space_after = Pt(2)
    r_hnom = h_nom.add_run("Table of Symbols, Variables & Mathematical Nomenclature")
    r_hnom.font.size = Pt(12)
    r_hnom.font.bold = True
    r_hnom.font.color.rgb = NAVY

    doc.add_paragraph(
        "This reference table defines the complete set of mathematical notations, physical optical variables, and electrical parameters "
        "used throughout the theoretical derivations, system models, and simulation testbed:"
    )

    # 4-Column Nomenclature Table
    nom_table = doc.add_table(rows=18, cols=4)
    nom_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    nom_headers = ["Symbol", "Full Term / Definition", "Physical Meaning & System Role", "Value / Unit"]
    col_widths = [Inches(1.2), Inches(2.2), Inches(2.7), Inches(1.1)]

    for i, h in enumerate(nom_headers):
        cell = nom_table.rows[0].cells[i]
        cell.width = col_widths[i]
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = WHITE
        set_cell_margins(cell, 35, 35, 60, 60)

    # Data corresponding to user's handwritten notes + supplementary system parameters
    nom_data = [
        (r"h_{AB}", "Alice-to-Bob Channel Gain", "Overall electrical channel gain from transmitter Alice to legitimate user Bob (LoS + RIS)", "Calculated [A/W]"),
        (r"G_{AB}", "Optical Path Gain (A to B)", "Pure geometric Lambertian optical propagation gain before photodiode responsivity scaling", "Dimensionless"),
        (r"h_{JB}", "Jammer-to-Bob Channel Gain", "Channel gain vector from 4 distributed ceiling Friendly Jammers to Bob's photodiode", "4 × 1 Vector"),
        (r"w \text{ (or } \mathbf{w})", "Jammer Weight Vector", "Continuous beamforming weights assigned to ceiling jammers, optimized via DRL", "w_j ∈ [-1, 1]"),
        (r"y_B", "Electrical Signal at Bob", "Received output electrical current generated at Bob's photodiode after direct detection", "Amperes (A)"),
        (r"x \text{ (or } x_A)", "Information Signal by Alice", "Confidential optical data signal modulated onto DC bias: x(t) = P_T s(t) + I_D", "Amperes (A)"),
        (r"h_{AB} x", "Transferred Alice-to-Bob Signal", "Alice's information signal arriving at Bob's optical aperture after spatial propagation", "Amperes (A)"),
        (r"\mathbf{h}_{JE}^T \mathbf{w}_J", "Jammer Signal to Eve after Transfer", "Aggregate artificial optical noise arriving at Eve's photodiode to drown out confidential data", "Amperes (A)"),
        (r"R \text{ (or } R_{\text{PD}})", "Photodiode Responsivity", "Receiver sensitivity converting incident optical power (Watts) to electrical current (Amperes)", "0.54 A/W"),
        (r"\eta", "Electro-Optical Conversion Efficiency", "Slope efficiency of ceiling LED converting driving electrical current into radiated optical flux", "0.80 W/A"),
        (r"I_D", "LED ON Bias Current", "Direct current (DC) operating bias ensuring LED operates strictly within linear forward-bias region", "1.0 A"),
        (r"I_c", "Total Driving Current", "Instantaneous total electrical driving current through transmitter LED: I_c(t) = I_D + i_mod(t)", "Amperes (A)"),
        (r"P_T", "Transmit Optical Power by LED", "Total radiated optical power emitted by Alice's central ceiling luminaire fixture", "1.0 Watt"),
        (r"\phi", "Irradiance Angle", "Spatial angle of optical emission measured relative to transmitter normal vector", "[0°, 60°]"),
        (r"\psi", "Incidence Angle", "Spatial angle of photon arrival measured relative to receiver photodiode normal vector", "[0°, 75°]"),
        (r"n_B", "Background Noise at Bob", "Additive Gaussian noise consisting of shot noise and thermal amplifier noise: N(0, σ_B²)", "σ_B² = 10^-14 A²"),
        (r"h_{\text{RIS}}, \Theta_m", "O-RIS Reflected Gain & Phase", "Cascaded specular anomalous reflection gain and micro-mirror reflection phase shift", "M = 16 to 64")
    ]

    for r_idx, (sym_ltx, term, desc, val) in enumerate(nom_data):
        row = nom_table.rows[r_idx + 1]
        bg = "F9FBFD" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx in range(4):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 25, 25, 50, 50)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # Col 0: Math equation
        p_sym = row.cells[0].paragraphs[0]
        p_sym.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sym.paragraph_format.space_before = Pt(1)
        p_sym.paragraph_format.space_after = Pt(1)
        p_sym._element.append(latex_to_omml(sym_ltx))

        # Col 1: Term
        p_term = row.cells[1].paragraphs[0]
        p_term.paragraph_format.space_before = Pt(1)
        p_term.paragraph_format.space_after = Pt(1)
        r1 = p_term.add_run(term)
        r1.bold = True
        r1.font.size = Pt(8.5)

        # Col 2: Description
        p_desc = row.cells[2].paragraphs[0]
        p_desc.paragraph_format.space_before = Pt(1)
        p_desc.paragraph_format.space_after = Pt(1)
        r2 = p_desc.add_run(desc)
        r2.font.size = Pt(8)

        # Col 3: Value
        p_val = row.cells[3].paragraphs[0]
        p_val.paragraph_format.space_before = Pt(1)
        p_val.paragraph_format.space_after = Pt(1)
        r3 = p_val.add_run(val)
        r3.font.size = Pt(8)

    # ==================== PAGE BREAK TO PAGE 3: EQUATIONS 1 TO 9 ====================
    doc.add_page_break()

    h3 = doc.add_heading(level=1)
    h3.paragraph_format.space_before = Pt(0)
    h3.paragraph_format.space_after = Pt(2)
    r_h3 = h3.add_run("3. Step-by-Step Mathematical Formulation")
    r_h3.font.size = Pt(12)
    r_h3.font.bold = True
    r_h3.font.color.rgb = NAVY

    doc.add_paragraph(
        "Optical propagation, cooperative jamming noise cancellation, wiretap capacities, and DRL optimization are modeled in native notation:"
    )

    # Subsection 3.1
    h3_1 = doc.add_heading(level=2)
    h3_1.paragraph_format.space_before = Pt(1)
    h3_1.paragraph_format.space_after = Pt(1)
    r_h3_1 = h3_1.add_run("3.1 Lambertian Optical Channel & O-RIS Model")
    r_h3_1.font.size = Pt(10.5)
    r_h3_1.font.bold = True
    r_h3_1.font.color.rgb = TEAL

    doc.add_paragraph(
        "Direct Line-of-Sight (LoS) optical channel gain follows the Generalized Lambertian Radiation Law:"
    )
    add_equation_box(
        doc,
        r"h_{\text{LoS}} = R_{\text{PD}} \cdot N_{\text{LED}} \cdot \frac{(m + 1) A_{\text{PD}}}{2\pi d^2} \cos^m(\phi) \cos(\psi) \cdot T_s(\psi) g(\psi)",
        "(1)"
    )

    doc.add_paragraph(
        "Where Lambertian emission order m and optical concentrator gain g(ψ) (with internal refractive index n = 1.5) are:"
    )
    add_equation_box(
        doc,
        r"m = -\frac{\ln(2)}{\ln(\cos(\phi_{1/2}))}, \quad\quad g(\psi) = \begin{cases} \frac{n^2}{\sin^2(\Psi_c)}, & 0 \le \psi \le \Psi_c \\ 0, & \psi > \Psi_c \end{cases}",
        "(2)"
    )

    doc.add_paragraph(
        "For the wall-mounted Optical RIS (O-RIS) with M elements, cascaded specular reflection gain and directivity g_dir are:"
    )
    add_equation_box(
        doc,
        r"h_{\text{RIS}} = R_{\text{PD}} \sum_{m=1}^{M} \left[ h_{A \to R_m} \cdot \Theta_m \cdot h_{R_m \to B} \right], \quad\quad g_{\text{dir}} = \frac{2}{1 - \cos(\theta_{\text{div}})} \approx 131.6",
        "(3)"
    )
    doc.add_paragraph(
        "Total channel gain experienced by Bob under human obstacle blockage χ_block ∈ {0, 1} is:"
    )
    add_equation_box(
        doc,
        r"h_{\text{AB}} = (1 - \chi_{\text{block}}) h_{\text{AB, LoS}} + h_{\text{AB, RIS}}",
        "(4)"
    )

    # Subsection 3.2
    h3_2 = doc.add_heading(level=2)
    h3_2.paragraph_format.space_before = Pt(1)
    h3_2.paragraph_format.space_after = Pt(1)
    r_h3_2 = h3_2.add_run("3.2 Signal Transmission & Bob Achievable Capacity")
    r_h3_2.font.size = Pt(10.5)
    r_h3_2.font.bold = True
    r_h3_2.font.color.rgb = TEAL

    doc.add_paragraph(
        "Alice modulates confidential data s(t) on DC bias Id, while 4 ceiling friendly jammers radiate artificial Gaussian noise:"
    )
    add_equation_box(
        doc,
        r"x_A(t) = P_t s(t) + I_D, \quad\quad \mathbf{x}_J(t) = \mathbf{w} \cdot n_J(t) + \mathbf{I}_{D,J}",
        "(5)"
    )
    doc.add_paragraph(
        "Bob's received electrical signal and optical Signal-to-Interference-plus-Noise Ratio (SINR) are:"
    )
    add_equation_box(
        doc,
        r"y_B(t) = R_{\text{PD}} h_{\text{AB}} x_A(t) + R_{\text{PD}} \mathbf{h}_{\text{JB}}^T \mathbf{x}_J(t) + n_B(t)",
        "(6)"
    )
    add_equation_box(
        doc,
        r"\text{SINR}_{\text{Bob}} = \frac{2 (R_{\text{PD}} h_{\text{AB}})^2 \alpha^2 I_D^2}{\pi e \left( \sigma_B^2 + 2 (R_{\text{PD}} |\mathbf{h}_{\text{JB}}^T \mathbf{w}|)^2 \alpha^2 I_D^2 \right)}, \quad C_{\text{Bob}} = \frac{1}{2} \log_2(1 + \text{SINR}_{\text{Bob}})",
        "(7)"
    )

    # Subsection 3.3
    h3_3 = doc.add_heading(level=2)
    h3_3.paragraph_format.space_before = Pt(1)
    h3_3.paragraph_format.space_after = Pt(1)
    r_h3_3 = h3_3.add_run("3.3 Eavesdropper Jammed Capacity & Colluding Eves")
    r_h3_3.font.size = Pt(10.5)
    r_h3_3.font.bold = True
    r_h3_3.font.color.rgb = TEAL

    doc.add_paragraph(
        "Under friendly jamming noise jam_E = R_PD |h_JE^T w| Id, Eve's wiretap capacity is strictly bounded (IEEE TWC 2024 Corollary 1):"
    )
    add_equation_box(
        doc,
        r"C_{\text{Eve, jam}} = \min \left\{ \log_2\left( \frac{h_{\text{AE}}}{\text{jam}_E} \right) + \frac{\text{jam}_E}{h_{\text{AE}}} \log_2(\sqrt{e}), \; \frac{h_{\text{AE}}}{\text{jam}_E} \log_2(\sqrt{e}) \right\}",
        "(8)"
    )
    doc.add_paragraph(
        "When Eve 1 and Eve 2 collude to share intercepted photons, their joint wiretap capacity is bounded by:"
    )
    add_equation_box(
        doc,
        r"C_{\text{Eve, total}} = \min \left\{ C_{\text{Bob}}, \; \max(C_{E1}, C_{E2}) + 0.12 \cdot \min(C_{E1}, C_{E2}) \right\}",
        "(9)"
    )

    # ==================== PAGE BREAK TO PAGE 4: SECRECY, DRL, NEAR-EVE ====================
    doc.add_page_break()

    # Subsection 3.4
    h3_4 = doc.add_heading(level=2)
    h3_4.paragraph_format.space_before = Pt(0)
    h3_4.paragraph_format.space_after = Pt(1)
    r_h3_4 = h3_4.add_run("3.4 Physical Layer Secrecy Rate, BER, & System Utility")
    r_h3_4.font.size = Pt(10.5)
    r_h3_4.font.bold = True
    r_h3_4.font.color.rgb = TEAL

    doc.add_paragraph(
        "The instantaneous physical layer secrecy rate Cs is the non-negative capacity difference between Bob and Eve:"
    )
    add_equation_box(
        doc,
        r"C_s = \max(0, \; C_{\text{Bob}} - C_{\text{Eve}}) \quad [\text{bps/Hz}]",
        "(10)"
    )
    doc.add_paragraph(
        "For 4-PAM optical modulation, Bob's Bit Error Rate (BER) is evaluated using the complementary error function erfc:"
    )
    add_equation_box(
        doc,
        r"\text{BER}_{\text{Bob}} = \frac{3}{4} \operatorname{erfc}\left( \sqrt{\frac{2 P_t h_{\text{AB}}^2}{5 \left( \sigma_B^2 + 2 (\mathbf{h}_{\text{JB}}^T \mathbf{w})^2 \alpha^2 I_D^2 \right)}} \right)",
        "(11)"
    )
    doc.add_paragraph(
        "The continuous DRL Actor-Critic network optimizes the multi-objective utility function u(k) and Secrecy Energy Efficiency (SEE):"
    )
    add_equation_box(
        doc,
        r"u(k) = C_s(k) - \delta_1 \cdot \text{BER}_{\text{Bob}}(k) - \delta_2 \cdot E_{\text{total}}(k), \quad\quad \text{SEE} = \frac{C_s}{E_{\text{total}}} \quad [\text{bps/Hz/Watt}]",
        "(12)"
    )
    doc.add_paragraph(
        "Where δ1 = 3.5 penalizes bit errors, δ2 = 0.4 penalizes energy consumption, and total energy is E_total = P_Alice + Σ|w_j|² P_jam + M · P_RIS."
    )

    # Section 4
    h4 = doc.add_heading(level=1)
    h4.paragraph_format.space_before = Pt(2)
    h4.paragraph_format.space_after = Pt(2)
    r_h4 = h4.add_run("4. Deep Reinforcement Learning (DRL) Architecture Breakdown")
    r_h4.font.size = Pt(12)
    r_h4.font.bold = True
    r_h4.font.color.rgb = NAVY

    doc.add_paragraph(
        "The project implements and benchmarks three optimization algorithms in the simulation environment:"
    )

    alg_table = doc.add_table(rows=4, cols=3)
    alg_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_alg = ["Algorithm / Model", "Neural Architecture & State Space", "Optimization Mechanism & Results"]
    for i, h in enumerate(headers_alg):
        cell = alg_table.rows[0].cells[i]
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = WHITE
        set_cell_margins(cell, 40, 40, 70, 70)

    alg_data = [
        ("1. DRL-FJ\n(Base Paper: IEEE TWC 2024)",
         "• CNN feature extractor (20, 40 filters)\n• Differentiable Neural Dictionary (DND) memory\n• State: M=11 sliding channel history.",
         "Selects quantized discrete weights w_i ∈ {-1, -0.5, 0, 0.5, 1}. DND memory caches high-reward states. Fails under blockage (Cs = 0) and near-user Eve."),
        
        ("2. DRL-RIS-FJ\n(Our Proposed Framework)",
         "• Continuous Deep Deterministic Policy Gradient (DDPG) Actor-Critic\n• Actor: Dense 128 -> Dense 128 -> Output 12\n• Critic: Evaluates Q(s, a).",
         "Jointly optimizes continuous jamming weights w ∈ [-1, 1]^4 and RIS reflection phases Θ ∈ [0, 1]^M in 1.2 ms. Achieves peak secrecy (6.45 bps/Hz) and 100% blockage survival."),
        
        ("3. Zero-Forcing Baseline\n(ZF-FJ Analytical Benchmark)",
         "• Convex null-space projection matrix\n• P_null = I - (h_JB · h_JB^T) / ||h_JB||²\n• w_zf = P_null · h_JE / norm",
         "Projects jamming power strictly orthogonal to Bob's channel. Completely collapses when Eve comes close to Bob (null space vanishes).")
    ]

    for r_idx, r_data in enumerate(alg_data):
        row = alg_table.rows[r_idx + 1]
        bg = "F9FBFD" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 35, 35, 70, 70)
            cell.paragraphs[0].add_run(val)

    # Section 5
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    h5 = doc.add_heading(level=1)
    h5.paragraph_format.space_before = Pt(2)
    h5.paragraph_format.space_after = Pt(2)
    r_h5 = h5.add_run("5. The 'Near-Bob Eve' Failure & Optical RIS Rescue Mechanism")
    r_h5.font.size = Pt(12)
    r_h5.font.bold = True
    r_h5.font.color.rgb = NAVY

    doc.add_paragraph(
        "In conventional Friendly Jamming, if an eavesdropper moves beside Bob (d(Bob, Eve2) < 0.4m), both nodes share virtually identical ceiling channels: "
        "h_JB ≈ h_JE2. Consequently, any ceiling jamming noise emitted to drown Eve inevitably spills over and blinds Bob. This near-user penalty crushes Bob's SINR, "
        "forcing Secrecy Rate to 0.00 bps/Hz."
    )
    doc.add_paragraph(
        "Our Wall O-RIS breaks this spatial correlation: mounted on the upper side wall, O-RIS establishes an independent angular optical path. "
        "The DRL agent reduces ceiling jammer power to protect Bob from spillover while focusing an intense anomalous specular beam from Alice to Bob via O-RIS, "
        "successfully restoring secrecy rate to > 3.5 bps/Hz."
    )

    # ==================== PAGE BREAK TO PAGE 5: RESULTS & DEFENSE ====================
    doc.add_page_break()

    # Section 6
    h6 = doc.add_heading(level=1)
    h6.paragraph_format.space_before = Pt(0)
    h6.paragraph_format.space_after = Pt(2)
    r_h6 = h6.add_run("6. Quantitative Experimental Results & Findings")
    r_h6.font.size = Pt(12)
    r_h6.font.bold = True
    r_h6.font.color.rgb = NAVY

    doc.add_paragraph(
        "The proposed DRL-RIS-FJ architecture was evaluated across 5 simulation experiments, demonstrating superior performance over all baselines:"
    )

    res_table = doc.add_table(rows=5, cols=5)
    res_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Scheme / Algorithm", "Jamming Strategy", "Optical RIS", "Secrecy Rate (Cs)", "Blockage Robustness"]
    for i, h in enumerate(res_headers):
        cell = res_table.rows[0].cells[i]
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = WHITE
        set_cell_margins(cell, 40, 40, 60, 60)

    res_data = [
        ("No-Jammer Baseline", "Disabled (w = 0)", "Disabled", "0.00 bps/Hz", "Total Outage (BER = 75%)"),
        ("Zero-Forcing (ZF-FJ)", "Null-Space Projection", "Disabled", "5.45 bps/Hz", "Total Outage (Cs = 0.0)"),
        ("DRL-FJ (Base Paper)", "CNN + DND Memory", "Disabled", "5.68 bps/Hz", "Zero Secrecy under Blockage"),
        ("DRL-RIS-FJ (Proposed)", "Joint Actor-Critic", "16–64 Element O-RIS", "6.45 bps/Hz (+15.8%)", "100% Link Survival (3.47 bps/Hz)")
    ]

    for r_idx, r_data in enumerate(res_data):
        row = res_table.rows[r_idx + 1]
        bg = "E8F5E9" if r_idx == 3 else ("F9FBFD" if r_idx % 2 == 0 else "FFFFFF")
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 35, 35, 60, 60)
            r_p = cell.paragraphs[0].add_run(val)
            if r_idx == 3:
                r_p.bold = True
                if c_idx == 3:
                    r_p.font.color.rgb = RGBColor(0, 128, 0)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Embed Fig 1 & Fig 2 Side-by-Side in a 2-column table
    fig_tbl = doc.add_table(rows=1, cols=2)
    fig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cf1, cf2 = fig_tbl.rows[0].cells[0], fig_tbl.rows[0].cells[1]
    cf1.width = Inches(3.55)
    cf2.width = Inches(3.55)
    for c in [cf1, cf2]:
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        c._element.get_or_add_tcPr().append(borders)
        set_cell_margins(c, 5, 5, 10, 10)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    fig1_path = os.path.join(r"d:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\figures", "fig1_convergence_curves.png")
    fig2_path = os.path.join(r"d:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\figures", "fig2_spatial_secrecy_heatmaps.png")
    
    if os.path.exists(fig1_path):
        p1 = cf1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.add_run().add_picture(fig1_path, width=Inches(3.35))
        p_c1 = cf1.add_paragraph()
        p_c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c1.paragraph_format.space_before = Pt(1)
        r_c1 = p_c1.add_run("Fig. 2: DRL Convergence Curves")
        r_c1.font.size = Pt(8)
        r_c1.font.italic = True
        r_c1.font.color.rgb = DARK_GRAY

    if os.path.exists(fig2_path):
        p2 = cf2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.add_run().add_picture(fig2_path, width=Inches(3.35))
        p_c2 = cf2.add_paragraph()
        p_c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c2.paragraph_format.space_before = Pt(1)
        r_c2 = p_c2.add_run("Fig. 3: Spatial Secrecy Distribution")
        r_c2.font.size = Pt(8)
        r_c2.font.italic = True
        r_c2.font.color.rgb = DARK_GRAY

    # Section 7
    h7 = doc.add_heading(level=1)
    h7.paragraph_format.space_before = Pt(2)
    h7.paragraph_format.space_after = Pt(2)
    r_h7 = h7.add_run("7. Key Talking Points for Supervisor & Presentation (Q&A Defense)")
    r_h7.font.size = Pt(12)
    r_h7.font.bold = True
    r_h7.font.color.rgb = NAVY

    points = [
        ("Why is Optical RIS essential alongside Friendly Jamming?", 
         "Friendly jamming alone fails when Eve approaches Bob (< 0.5m) because artificial noise spills over and blinds Bob. Adding Wall O-RIS provides an independent photon reflection path that bypasses near-user interference and rescues confidential transmission."),
        
        ("What happens during a human obstacle Line-of-Sight blockage?",
         "In conventional OWC, a person walking between Alice and Bob drops secrecy to 0 bps/Hz (BER = 75%). With our O-RIS, light reflects off the wall metasurface around the obstacle, maintaining a robust 3.47 bps/Hz secrecy rate and BER < 10^-5."),
        
        ("Why use continuous Actor-Critic DRL over traditional optimization?",
         "Jointly optimizing continuous jammer weights w ∈ [-1, 1]^4 and continuous RIS elements Θ ∈ [0, 1]^M is non-convex and NP-hard. Numerical solvers take several seconds per frame; our trained DRL Actor evaluates optimal beamforming in under 1.2 milliseconds.")
    ]

    for q, a in points:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(1.5)
        p_q.paragraph_format.space_after = Pt(0.5)
        r_q = p_q.add_run(f"• Question: {q}")
        r_q.bold = True
        r_q.font.color.rgb = NAVY
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0)
        p_a.paragraph_format.space_after = Pt(2)
        p_a.add_run(f"  Explanation: {a}")

    # Output files
    output_docx = r"d:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\PROJECT_TECHNICAL_REPORT.docx"
    output_pdf = r"d:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\PROJECT_TECHNICAL_REPORT.pdf"
    
    doc.save(output_docx)
    print(f"Saved: {output_docx}")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    d = word.Documents.Open(output_docx)
    d.SaveAs(output_pdf, FileFormat=17)
    d.Close()
    word.Quit()
    print(f"Exported PDF: {output_pdf}")

if __name__ == "__main__":
    build_complete_report_with_nomenclature()
