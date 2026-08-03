import io
from datetime import datetime
from typing import Dict, Any, List
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
except ImportError:
    pass # In production, ensure reportlab is installed

from backend.schemas import CandidateProfileSchema

class ReportGenerator:
    def generate_pdf(self, analysis: Dict[str, Any], candidate: CandidateProfileSchema, gaps: List[Dict[str, Any]], shap: Dict[str, Any]) -> bytes:
        """
        Generate a PDF report using ReportLab.
        """
        buffer = io.BytesIO()
        
        try:
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom Dark Theme Styles
            title_style = ParagraphStyle(
                'DarkTitle',
                parent=styles['Heading1'],
                textColor=colors.HexColor('#000080'), # Navy
                fontSize=24,
                spaceAfter=20
            )
            
            elements = []
            
            # Cover Page / Header
            elements.append(Paragraph(f"Candidate Evaluation Report: {candidate.name}", title_style))
            elements.append(Paragraph(f"Role: {analysis.get('role', 'N/A')}", styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Score Summary
            final_score = analysis.get("final_score", 0.0)
            elements.append(Paragraph(f"Final Score: {final_score:.2f}/100", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            # Competency Table
            comp_data = [["Competency", "Score"]]
            for k, v in analysis.get("competency_scores", {}).items():
                comp_data.append([k.title(), f"{v:.2f}"])
                
            t = Table(comp_data, colWidths=[200, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#008080')), # Teal
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F0F8FF')),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))
            
            # Top SHAP Factors
            elements.append(Paragraph("Key Score Drivers (SHAP)", styles['Heading2']))
            shap_data = [["Factor", "Impact"]]
            for pos in shap.get("top_positive", []):
                shap_data.append([pos["display_name"], f"+{pos['shap_value']:.2f}"])
            for neg in shap.get("top_negative", []):
                shap_data.append([neg["display_name"], f"{neg['shap_value']:.2f}"])
                
            if len(shap_data) > 1:
                t2 = Table(shap_data, colWidths=[200, 100])
                t2.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4B0082')), # Indigo
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('GRID', (0,0), (-1,-1), 1, colors.black)
                ]))
                elements.append(t2)
                
            # Footer
            elements.append(Spacer(1, 40))
            elements.append(Paragraph(f"Generated on: {datetime.now().isoformat()} | Model v1.0", styles['Italic']))
            
            doc.build(elements)
        except Exception as e:
            # Fallback if ReportLab fails
            buffer.write(f"Error generating PDF: {str(e)}".encode('utf-8'))
            
        return buffer.getvalue()
