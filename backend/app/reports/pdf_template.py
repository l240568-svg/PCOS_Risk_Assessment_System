from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFTemplate(ABC):
    TEAL = colors.HexColor("#08727B")
    DEEP_GREEN = colors.HexColor("#163F36")
    LIGHT_TEAL = colors.HexColor("#EDF8F8")
    TEXT = colors.HexColor("#173438")
    MUTED = colors.HexColor("#667B7E")
    LINE = colors.HexColor("#DCE8E8")

    def __init__(self):
        self.data: dict | None = None
        self.buffer: BytesIO | None = None
        self.document = None
        self.story: list = []
        self.styles = None
        self.generated_at: datetime | None = None
        self.footer_text = ""

    def build_pdf(self, data: dict) -> BytesIO:
        self.data = data
        self.generated_at = datetime.now()

        self._init_doc()
        self._add_header()
        self._add_title(data)
        self._add_content(data)
        self._add_footer()

        self.document.build(
            self.story,
            onFirstPage=self._draw_footer,
            onLaterPages=self._draw_footer,
        )

        self.buffer.seek(0)
        return self.buffer

    def _init_doc(self) -> None:
        self.buffer = BytesIO()

        self.document = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=22 * mm,
            title="PCOS Risk Assessment Report",
            author=self.data["doctor_name"],
        )

        self.story = []
        self.styles = getSampleStyleSheet()

        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=self.styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=25,
            textColor=self.DEEP_GREEN,
            spaceAfter=5 * mm,
        ))

        self.styles.add(ParagraphStyle(
            name="SectionTitle",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=self.TEAL,
            spaceBefore=5 * mm,
            spaceAfter=2 * mm,
        ))

        self.styles.add(ParagraphStyle(
            name="ReportBody",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=self.TEXT,
        ))

        self.styles.add(ParagraphStyle(
            name="HeaderRight",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_RIGHT,
            textColor=colors.white,
        ))

    def _add_header(self) -> None:
        hospital = (
            self.data.get("doctor_hospital")
            or "Independent Clinic"
        )

        clinic_address = (
            self.data.get("doctor_clinic_address")
            or ""
        )

        left_style = ParagraphStyle(
            name="HeaderLeft",
            parent=self.styles["ReportBody"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=colors.white,
        )

        left_content = Paragraph(
            "<b>PCOS CARE</b><br/>"
            "Clinical Decision-Support Report",
            left_style,
        )

        right_text = (
            f"<b>{escape(self.data['doctor_name'])}</b><br/>"
            f"{escape(self.data['doctor_specialization'])}<br/>"
            f"{escape(hospital)}"
        )

        if clinic_address:
            right_text += f"<br/>{escape(clinic_address)}"

        right_text += (
            "<br/>Report generated: "
            f"{self.generated_at.strftime('%d %B %Y, %I:%M %p')}"
        )

        right_content = Paragraph(
            right_text,
            self.styles["HeaderRight"],
        )

        header_table = Table(
            [[left_content, right_content]],
            colWidths=[
                self.document.width * 0.42,
                self.document.width * 0.58,
            ],
        )

        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), self.TEAL),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))

        self.story.append(header_table)
        self.story.append(Spacer(1, 7 * mm))

    def _add_footer(self) -> None:
        self.footer_text = (
            "This report supports clinical decision-making "
            "and does not constitute a diagnosis."
        )

    def _draw_footer(self, canvas, document) -> None:
        canvas.saveState()

        canvas.setStrokeColor(self.LINE)
        canvas.line(
            document.leftMargin,
            15 * mm,
            A4[0] - document.rightMargin,
            15 * mm,
        )

        canvas.setFillColor(self.MUTED)
        canvas.setFont("Helvetica", 7)

        canvas.drawString(
            document.leftMargin,
            10 * mm,
            self.footer_text,
        )

        canvas.drawRightString(
            A4[0] - document.rightMargin,
            10 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    @abstractmethod
    def _add_title(self, data: dict) -> None:
        pass

    @abstractmethod
    def _add_content(self, data: dict) -> None:
        pass