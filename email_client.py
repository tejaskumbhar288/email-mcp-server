"""
Email client for handling SMTP and IMAP operations.
"""
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class EmailClient:
    """Email client for Gmail using SMTP/IMAP."""

    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not self.email_user or not self.email_pass:
            raise ValueError("EMAIL_USER and EMAIL_PASS must be set in .env file")

    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server."""
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.email_user, self.email_pass)
        return mail

    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        decoded = decode_header(header)
        result = ""
        for content, encoding in decoded:
            if isinstance(content, bytes):
                result += content.decode(encoding or 'utf-8', errors='ignore')
            else:
                result += content
        return result

    def _parse_email(self, email_message) -> Dict:
        """Parse email message into a dictionary."""
        subject = self._decode_header(email_message.get("Subject", ""))
        from_ = self._decode_header(email_message.get("From", ""))
        date = email_message.get("Date", "")

        # Get email body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())

        # Create preview (first 150 characters)
        preview = body[:150].replace('\n', ' ').strip() + "..." if len(body) > 150 else body

        return {
            "subject": subject,
            "from": from_,
            "date": date,
            "body": body,
            "preview": preview
        }

    def read_emails(self, count: int = 10, folder: str = "INBOX") -> List[Dict]:
        """
        Read recent emails from the specified folder.

        Args:
            count: Number of emails to retrieve (default: 10)
            folder: Email folder to read from (default: "INBOX")

        Returns:
            List of email dictionaries
        """
        try:
            mail = self._connect_imap()
            mail.select(folder)

            # Search for all emails
            _, message_numbers = mail.search(None, "ALL")
            message_list = message_numbers[0].split()

            # Get the most recent emails
            recent_messages = message_list[-count:] if len(message_list) >= count else message_list
            recent_messages.reverse()  # Most recent first

            emails = []
            for num in recent_messages:
                _, msg_data = mail.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                parsed_email = self._parse_email(email_message)
                parsed_email["id"] = num.decode()
                emails.append(parsed_email)

            mail.close()
            mail.logout()
            return emails

        except Exception as e:
            raise Exception(f"Failed to read emails: {str(e)}")

    def filter_emails(
        self,
        sender: Optional[str] = None,
        subject: Optional[str] = None,
        is_unread: Optional[bool] = None,
        folder: str = "INBOX"
    ) -> List[Dict]:
        """
        Filter emails based on criteria.

        Args:
            sender: Filter by sender email address
            subject: Filter by subject (case-insensitive substring match)
            is_unread: Filter by unread status
            folder: Email folder to search in

        Returns:
            List of matching email dictionaries
        """
        try:
            mail = self._connect_imap()
            mail.select(folder)

            # Build search criteria
            search_criteria = []
            if is_unread is not None:
                search_criteria.append("UNSEEN" if is_unread else "SEEN")
            if sender:
                search_criteria.append(f'FROM "{sender}"')

            # Search emails
            search_string = " ".join(search_criteria) if search_criteria else "ALL"
            _, message_numbers = mail.search(None, search_string)
            message_list = message_numbers[0].split()

            emails = []
            for num in message_list:
                _, msg_data = mail.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                parsed_email = self._parse_email(email_message)

                # Apply subject filter (IMAP doesn't support substring search)
                if subject and subject.lower() not in parsed_email["subject"].lower():
                    continue

                parsed_email["id"] = num.decode()
                emails.append(parsed_email)

            # Return most recent first
            emails.reverse()

            mail.close()
            mail.logout()
            return emails

        except Exception as e:
            raise Exception(f"Failed to filter emails: {str(e)}")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None
    ) -> Dict:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipient (optional)

        Returns:
            Success message dictionary
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.email_user
            msg["To"] = to
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = cc

            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)

                recipients = [to]
                if cc:
                    recipients.append(cc)

                server.send_message(msg)

            return {
                "success": True,
                "message": f"Email sent successfully to {to}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

    def get_unread_count(self, folder: str = "INBOX") -> int:
        """
        Get count of unread emails.

        Args:
            folder: Email folder to check

        Returns:
            Number of unread emails
        """
        try:
            mail = self._connect_imap()
            mail.select(folder)

            _, message_numbers = mail.search(None, "UNSEEN")
            count = len(message_numbers[0].split()) if message_numbers[0] else 0

            mail.close()
            mail.logout()
            return count

        except Exception as e:
            raise Exception(f"Failed to get unread count: {str(e)}")
