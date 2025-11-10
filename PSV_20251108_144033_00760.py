from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path

out_dir = Path('output')
out_dir.mkdir(parents=True, exist_ok=True)

pdf_path = out_dir / '_test_reportlab.pdf'

c = canvas.Canvas(str(pdf_path), pagesize=letter)
width, height = letter
c.setFont('Helvetica', 14)
c.drawString(72, height - 72, 'ReportLab OK: test PDF generated successfully.')
c.save()

print(f'Wrote: {pdf_path.resolve()}')
