from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.reports.pdf_template import PDFTemplate


class AssessmentReport(PDFTemplate):
    HIGH_RISK = colors.HexColor("#B94F48")
    HIGH_BACKGROUND = colors.HexColor("#FAE6E2")
    LOW_RISK = colors.HexColor("#2F6B59")
    LOW_BACKGROUND = colors.HexColor("#DFF2EA")

    def _text(self, value) -> str:
        if value is None or value == "":
            return "Not recorded"

        return escape(str(value))

    def _yes_no(self, value: bool) -> str:
        return "Yes" if value else "No"

    def _section(self, title: str) -> None:
        self.story.append(
            Paragraph(
                title,
                self.styles["SectionTitle"],
            )
        )

    def _details(
        self,
        rows: list[tuple[str, object]],
    ) -> None:
        table_data = []

        for label, value in rows:
            table_data.append([
                Paragraph(
                    f"<b>{escape(label)}</b>",
                    self.styles["ReportBody"],
                ),
                Paragraph(
                    self._text(value),
                    self.styles["ReportBody"],
                ),
            ])

        table = Table(
            table_data,
            colWidths=[
                48 * mm,
                self.document.width - 48 * mm,
            ],
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), self.LIGHT_TEAL),
            ("GRID", (0, 0), (-1, -1), 0.4, self.LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        self.story.append(table)

    def _add_title(self, data: dict) -> None:
        self.story.append(
            Paragraph(
                "PCOS Risk Assessment Report",
                self.styles["ReportTitle"],
            )
        )

        subtitle = (
            f"Assessment #{data['assessment_id']} | "
            f"Assessment date: "
            f"{data['assessment_date']:%d %B %Y}"
        )

        self.story.append(
            Paragraph(
                subtitle,
                self.styles["ReportBody"],
            )
        )

        self.story.append(Spacer(1, 5 * mm))

    def _add_risk_result(self, data: dict) -> None:
        risk_class = (
            data.get("prediction_class")
            or "Unavailable"
        )

        probability = data.get("prediction_probability")

        probability_text = (
            f"{float(probability) * 100:.1f}%"
            if probability is not None
            else "Unavailable"
        )

        is_high_risk = risk_class == "High Risk"

        foreground = (
            self.HIGH_RISK
            if is_high_risk
            else self.LOW_RISK
        )

        background = (
            self.HIGH_BACKGROUND
            if is_high_risk
            else self.LOW_BACKGROUND
        )

        risk_style = ParagraphStyle(
            name="RiskText",
            parent=self.styles["ReportBody"],
            fontSize=10,
            leading=17,
            textColor=foreground,
        )

        risk_table = Table(
            [[
                Paragraph(
                    "<b>Risk classification</b><br/>"
                    f"<font size='15'>"
                    f"{escape(risk_class)}</font>",
                    risk_style,
                ),
                Paragraph(
                    "<b>Predicted probability</b><br/>"
                    f"<font size='15'>"
                    f"{probability_text}</font>",
                    risk_style,
                ),
            ]],
            colWidths=[
                self.document.width / 2,
                self.document.width / 2,
            ],
        )

        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), background),
            ("BOX", (0, 0), (-1, -1), 1, foreground),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))

        self.story.append(risk_table)

    def _add_content(self, data: dict) -> None:
        self._section("Risk Result")
        self._add_risk_result(data)

        self._section("Patient Information")
        self._details([
            ("Patient name", data["patient_name"]),
            ("Patient ID", data["patient_id"]),
            (
                "Date of birth",
                data["date_of_birth"].strftime("%d %B %Y"),
            ),
            ("Age", f"{data['age']} years"),
            ("Email", data.get("patient_email")),
            ("Height", f"{data['height_cm']} cm"),
        ])

        self._section("Assessment Overview")
        self._details([
            (
                "Assessment date",
                data["assessment_date"].strftime("%d %B %Y"),
            ),
            ("Weight", f"{data['weight_kg']} kg"),
            ("Calculated BMI", data["bmi"]),
            (
                "Cycle regularity",
                "Regular" if data["cycle_regular"] else "Irregular",
            ),
            ("Cycle length", f"{data['cycle_length']} days"),
        ])

        self._section("Hormonal Markers")
        self._details([
            ("FSH", f"{data['fsh_miu_ml']} mIU/mL"),
            ("LH", f"{data['lh_miu_ml']} mIU/mL"),
            ("FSH/LH ratio", data.get("fsh_lh_ratio")),
            (
                "AMH",
                (
                    f"{data['amh_ng_ml']} ng/mL"
                    if data.get("amh_ng_ml") is not None
                    else None
                ),
            ),
        ])

        self._section("Clinical Symptoms")
        self._details([
            ("Weight gain", self._yes_no(data["weight_gain"])),
            ("Hair growth", self._yes_no(data["hair_growth"])),
            (
                "Skin darkening",
                self._yes_no(data["skin_darkening"]),
            ),
            ("Hair loss", self._yes_no(data["hair_loss"])),
            ("Acne", self._yes_no(data["pimples"])),
        ])

        self._section("Lifestyle Factors")
        self._details([
            (
                "Fast-food intake",
                self._yes_no(data["fast_food"]),
            ),
            (
                "Regular exercise",
                self._yes_no(data["regular_exercise"]),
            ),
        ])

        self._section("Ultrasound Findings")
        self._details([
            ("Left follicles", data["follicle_left"]),
            ("Right follicles", data["follicle_right"]),
            ("Total follicles", data["total_follicles"]),
            (
                "Follicle difference",
                data["follicle_difference"],
            ),
        ])

        self._section("Doctor Notes")

        notes = (
            data.get("doctor_notes")
            or "No clinical notes recorded."
        )

        notes_paragraph = Paragraph(
            self._text(notes).replace("\n", "<br/>"),
            self.styles["ReportBody"],
        )

        notes_table = Table(
            [[notes_paragraph]],
            colWidths=[self.document.width],
        )

        notes_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.7, self.LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))

        self.story.append(notes_table)

        self._section("Clinical Sign-Off")
        self.story.append(Spacer(1, 8 * mm))

        doctor_name = self._text(data["doctor_name"])
        license_number = self._text(
            data.get("doctor_license_number")
        )

        signature_table = Table(
            [[
                Paragraph(
                    "____________________________<br/>"
                    "<b>Doctor signature</b><br/>"
                    f"{doctor_name}<br/>"
                    f"License: {license_number}",
                    self.styles["ReportBody"],
                ),
                Paragraph(
                    "____________________________<br/>"
                    "<b>Date</b>",
                    self.styles["ReportBody"],
                ),
            ]],
            colWidths=[
                self.document.width * 0.65,
                self.document.width * 0.35,
            ],
        )

        signature_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        self.story.append(signature_table)