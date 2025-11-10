
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from io import BytesIO

COURT_FILE_NO = "FDSJ-739-2024"
RESPONDENT_NAME = "CRAIG SCHULZ"
APPLICANT_NAME = "SONNY RYAN" # Placeholder

def create_form_81c_pdf(text_content):
    """
    Generates a court-compliant PDF for Form 81C.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.fontName = 'Helvetica'
    styleN.fontSize = 12
    styleN.leading = 18 # 1.5 line spacing

    # --- Header ---
    p.setFont('Helvetica-Bold', 12)
    p.drawString(0.5 * inch, 10.5 * inch, f"COURT FILE NO. {COURT_FILE_NO}")
    p.drawRightString(8 * inch, 10.5 * inch, "Form 81C")
    
    p.setFont('Helvetica-Bold', 14)
    p.drawCentredString(4.25 * inch, 10 * inch, "COURT OF KING'S BENCH OF NEW BRUNSWICK")
    p.setFont('Helvetica-Bold', 12)
    p.drawCentredString(4.25 * inch, 9.75 * inch, "Family Division")
    
    p.setFont('Helvetica', 12)
    p.drawString(1 * inch, 9 * inch, f"BETWEEN:")
    p.drawString(1 * inch, 8.5 * inch, f"APPLICANT: {APPLICANT_NAME}")
    p.drawString(1 * inch, 8.25 * inch, "AND:")
    p.drawString(1 * inch, 8 * inch, f"RESPONDENT: {RESPONDENT_NAME}")

    p.setFont('Helvetica-Bold', 14)
    p.drawCentredString(4.25 * inch, 7.25 * inch, "ANSWER AND COUNTER-CLAIM")

    # --- Body / Counter-Claim ---
    p.setFont('Helvetica-Bold', 12)
    p.drawString(0.5 * inch, 6.5 * inch, "COUNTER-CLAIM OF THE RESPONDENT")
    p.line(0.5 * inch, 6.45 * inch, 8 * inch, 6.45 * inch)

    # Create Paragraph object to handle text wrapping
    text_lines = text_content.replace('\n', '<br/>')
    para = Paragraph(text_lines, styleN)
    
    # Calculate height and draw
    w, h = para.wrapOn(p, 7 * inch, 5 * inch)
    para.drawOn(p, 0.75 * inch, 6.25 * inch - h)

    # --- Footer / Signature ---
    # This would contain the signature block, which we'll add later.

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
