import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import get_settings


def send_otp_email(
    recipient_email: str,
    otp: str,
) -> None:
    if len(otp) != 6 or not otp.isdigit():
        raise ValueError("OTP must contain exactly 6 digits")

    settings = get_settings()

    message = EmailMessage()
    message["Subject"] = "Your Password Reset Verification Code"
    message["From"] = settings.MAIL_FROM
    message["To"] = recipient_email

    message.set_content(
    f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
        </head>

        <body style="
            margin: 0;
            padding: 0;
            background-color: #f4f6f8;
            font-family: Arial, Helvetica, sans-serif;
            color: #1f2937;
">
            <table
                role="presentation"
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="background-color: #f4f6f8; padding: 40px 16px;"
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
                                border-radius: 16px;
                                overflow: hidden;
                                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
                            "
                        >
                            <tr>
                                <td
                                    align="center"
                                    style="
                                        background-color: #7c3aed;
                                        padding: 32px 24px;
                                    "
                                >
                                    <div style="
                                        display: inline-block;
                                        background-color: rgba(255, 255, 255, 0.16);
                                        border-radius: 50%;
                                        padding: 14px;
                                        margin-bottom: 14px;
                                        font-size: 30px;
                                    ">
                                        ✉️
                                    </div>

                                    <h1 style="
                                        margin: 0;
                                        color: #ffffff;
                                        font-size: 26px;
                                        font-weight: 700;
                                    ">
                                        Email Verification
                                    </h1>

                                    <p style="
                                        margin: 10px 0 0;
                                        color: #ede9fe;
                                        font-size: 15px;
                                    ">
                                        PCOS Application
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
                                        color: #4b5563;
                                    ">
                                        Use the verification code below to complete
                                        your email verification.
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
                                                    background-color: #f5f3ff;
                                                    border: 2px dashed #8b5cf6;
                                                    border-radius: 12px;
                                                    color: #6d28d9;
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
                                        color: #6b7280;
                                        text-align: center;
                                    ">
                                        Enter this code in the application to verify
                                        your email address.
                                    </p>

                                    <div style="
                                        margin-top: 28px;
                                        padding: 16px;
                                        background-color: #fff7ed;
                                        border-left: 4px solid #f97316;
                                        border-radius: 8px;
                                    ">
                                        <p style="
                                            margin: 0;
                                            color: #9a3412;
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
                                        color: #9ca3af;
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
                                        background-color: #f9fafb;
                                        border-top: 1px solid #e5e7eb;
                                    "
                                >
                                    <p style="
                                        margin: 0;
                                        color: #9ca3af;
                                        font-size: 12px;
                                        line-height: 1.5;
                                    ">
                                        This is an automated message from the PCOS Application.
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
    """,
    subtype="html",
)
    
    message.add_alternative(
        f"Your verification code is: {otp}\n\n"
        "Do not share this code with anyone."
    )


    try:
        tls_context = ssl.create_default_context()

        with smtplib.SMTP(
            settings.MAILTRAP_HOST,
            settings.MAILTRAP_PORT,
            timeout=10,
        ) as smtp:
            smtp.ehlo()
            smtp.starttls(context=tls_context)
            smtp.ehlo()

            smtp.login(
                settings.MAILTRAP_USERNAME,
                settings.MAILTRAP_PASSWORD,
            )

            smtp.send_message(message)

    except (smtplib.SMTPException, OSError) as error:
        raise RuntimeError("Unable to send OTP email") from error