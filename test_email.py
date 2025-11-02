#!/usr/bin/env python3
"""
Quick test script to verify email configuration.
"""
from email_client import EmailClient

def test_email_client():
    """Test email client functionality."""
    try:
        print("[*] Initializing Email Client...")
        client = EmailClient()
        print(f"[+] Email configured: {client.email_user}")

        print("\n[*] Testing unread count...")
        unread = client.get_unread_count()
        print(f"[+] Unread emails: {unread}")

        print("\n[*] Testing read emails (fetching 3 recent)...")
        emails = client.read_emails(count=3)
        print(f"[+] Successfully retrieved {len(emails)} email(s)")

        if emails:
            print("\n[*] First email preview:")
            first = emails[0]
            print(f"  From: {first['from']}")
            print(f"  Subject: {first['subject']}")
            print(f"  Preview: {first['preview'][:100]}...")

        print("\n[+] All tests passed! Email client is working correctly.")
        print("\n[SUCCESS] Your MCP server is ready to use!")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print("\n[!] Common issues:")
        print("  1. Make sure you're using a Gmail App Password, not your regular password")
        print("  2. Enable 2-Step Verification in Google Account settings")
        print("  3. Generate an App Password at: https://myaccount.google.com/apppasswords")
        print("  4. Check your internet connection")

if __name__ == "__main__":
    test_email_client()
