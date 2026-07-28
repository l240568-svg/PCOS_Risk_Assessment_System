from html import escape

def otp_template_html(otp: str) -> str:
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset</title>
            </head>
    
            <body style="
                margin: 0;
                padding: 0;
                background-color: #f4f8f8;
                font-family: Arial, Helvetica, sans-serif;
                color: #173438;
    ">
                <table
                    role="presentation"
                    width="100%"
                    cellspacing="0"
                    cellpadding="0"
                    border="0"
                    style="background-color: #f4f8f8; padding: 40px 16px;"
                >
                    <tr>
                        <td align="center">
    
                            <table
                                role="presentation"
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                border="0"
                                style="
                                    max-width: 560px;
                                    background-color: #ffffff;
                                    border: 1px solid #dce8e8;
                                    border-radius: 12px;
                                    overflow: hidden;
                                    box-shadow: 0 16px 42px rgba(15, 68, 72, 0.12);
                                "
                            >
                                <tr>
                                    <td
                                        align="center"
                                        style="
                                            background-color: #08727b;
                                            padding: 32px 24px;
                                        "
                                    >
                                        <div style="
                                            display: inline-block;
                                            background-color: #d8f0f0;
                                            border-radius: 50%;
                                            padding: 14px;
                                            margin-bottom: 14px;
                                            color: #075861;
                                            font-size: 0;
                                        ">
                                            <span style="
                                                font-size: 26px;
                                                line-height: 1;
                                            ">&#9993;</span>
                                        </div>
    
                                        <h1 style="
                                            margin: 0;
                                            color: #ffffff;
                                            font-size: 26px;
                                            font-weight: 700;
                                        ">
                                            Password Reset
                                        </h1>
    
                                        <p style="
                                            margin: 10px 0 0;
                                            color: #d8f0f0;
                                            font-size: 15px;
                                        ">
                                            PCOS Care
                                        </p>
                                    </td>
                                </tr>
    
                                <tr>
                                    <td style="padding: 36px 32px;">
                                        <p style="
                                            margin: 0 0 18px;
                                            font-size: 17px;
                                            line-height: 1.6;
                                        ">
                                            Hello,
                                        </p>
    
                                        <p style="
                                            margin: 0 0 24px;
                                            font-size: 16px;
                                            line-height: 1.6;
                                            color: #667b7e;
                                        ">
                                            Use the verification code below to complete
                                            your password reset.
                                        </p>
    
                                        <table
                                            role="presentation"
                                            width="100%"
                                            cellspacing="0"
                                            cellpadding="0"
                                            border="0"
                                        >
                                            <tr>
                                                <td align="center">
                                                    <div style="
                                                        display: inline-block;
                                                        padding: 18px 32px;
                                                        background-color: #edf8f8;
                                                        border: 2px dashed #0b8790;
                                                        border-radius: 12px;
                                                        color: #075861;
                                                        font-size: 34px;
                                                        font-weight: 700;
                                                        letter-spacing: 10px;
                                                        line-height: 1;
                                                    ">
                                                        {otp}
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>
    
                                        <p style="
                                            margin: 28px 0 0;
                                            font-size: 14px;
                                            line-height: 1.6;
                                            color: #667b7e;
                                            text-align: center;
                                        ">
                                            This code will expire in 1 minute.
                                        </p>
    
                                        <div style="
                                            margin-top: 28px;
                                            padding: 16px;
                                            background-color: #fff0c9;
                                            border-left: 4px solid #926211;
                                            border-radius: 8px;
                                        ">
                                            <p style="
                                                margin: 0;
                                                color: #6f4a0d;
                                                font-size: 14px;
                                                line-height: 1.5;
                                            ">
                                                <strong>Security notice:</strong>
                                                Do not share this verification code with
                                                anyone. Our team will never ask you for it.
                                            </p>
                                        </div>
    
                                        <p style="
                                            margin: 28px 0 0;
                                            font-size: 14px;
                                            line-height: 1.6;
                                            color: #667b7e;
                                        ">
                                            If you did not request this code, you can safely
                                            ignore this email.
                                        </p>
                                    </td>
                                </tr>
    
                                <tr>
                                    <td
                                        align="center"
                                        style="
                                            padding: 22px 24px;
                                            background-color: #f8fbfb;
                                            border-top: 1px solid #dce8e8;
                                        "
                                    >
                                        <p style="
                                            margin: 0;
                                            color: #667b7e;
                                            font-size: 12px;
                                            line-height: 1.5;
                                        ">
                                            This is an automated message from PCOS Care.
                                            Please do not reply to this email.
                                        </p>
                                    </td>
                                </tr>
                            </table>
    
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """

from html import escape


def assessment_template_html(
    patient_name: str,
    doctor_name: str,
) -> str:
    patient_name = escape(patient_name)
    doctor_name = escape(doctor_name)

    return f"""
    <!DOCTYPE html>
    <html>
        <body style="
            margin: 0;
            padding: 30px;
            background-color: #f3f8f8;
            font-family: Arial, sans-serif;
            color: #173438;
        ">
            <div style="
                max-width: 600px;
                margin: auto;
                background-color: white;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid #dce8e8;
            ">
                <div style="
                    padding: 24px;
                    background-color: #08727b;
                    color: white;
                ">
                    <h1 style="margin: 0; font-size: 24px;">
                        PCOS Care
                    </h1>

                    <p style="margin: 8px 0 0;">
                        Assessment report
                    </p>
                </div>

                <div style="padding: 28px;">
                    <h2 style="color: #163f36;">
                        Your assessment report is ready
                    </h2>

                    <p>Hello {patient_name},</p>

                    <p style="line-height: 1.6;">
                        Your PCOS risk assessment report has been
                        prepared by <strong>{doctor_name}</strong>.
                    </p>

                    <div style="
                        margin: 24px 0;
                        padding: 16px;
                        background-color: #edf8f8;
                        border-left: 4px solid #08727b;
                    ">
                        The complete report is attached to this email
                        as a PDF document.
                    </div>

                    <p style="
                        font-size: 13px;
                        color: #667b7e;
                        line-height: 1.5;
                    ">
                        This report supports clinical decision-making
                        and does not replace medical diagnosis.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
