#!/usr/bin/env python3
"""
Email Alert MCP Server

Exposes email operations (read, filter, send, unread count) as MCP tools
so that LLM agents can interact with email naturally.
"""
import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

from email_client import EmailClient


# Initialize MCP server
app = Server("email-alert-server")

# Initialize email client
email_client = EmailClient()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available email tools."""
    return [
        Tool(
            name="read_emails",
            description="Read recent emails from inbox or specified folder. Returns a list of emails with subject, sender, date, and preview.",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "number",
                        "description": "Number of emails to retrieve (default: 10)",
                        "default": 10
                    },
                    "folder": {
                        "type": "string",
                        "description": "Email folder to read from (default: INBOX)",
                        "default": "INBOX"
                    }
                }
            }
        ),
        Tool(
            name="filter_emails",
            description="Search and filter emails by sender, subject, or unread status. Useful for finding specific emails.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sender": {
                        "type": "string",
                        "description": "Filter by sender email address (optional)"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Filter by subject (case-insensitive substring match) (optional)"
                    },
                    "is_unread": {
                        "type": "boolean",
                        "description": "Filter by unread status (optional)"
                    },
                    "folder": {
                        "type": "string",
                        "description": "Email folder to search in (default: INBOX)",
                        "default": "INBOX"
                    }
                }
            }
        ),
        Tool(
            name="send_email",
            description="Send an email to a recipient with subject and body. Can optionally include CC.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content (plain text)"
                    },
                    "cc": {
                        "type": "string",
                        "description": "CC recipient email address (optional)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="get_unread_count",
            description="Get the count of unread emails in inbox or specified folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "Email folder to check (default: INBOX)",
                        "default": "INBOX"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from the MCP client."""

    try:
        if name == "read_emails":
            count = arguments.get("count", 10)
            folder = arguments.get("folder", "INBOX")

            emails = email_client.read_emails(count=count, folder=folder)

            # Format response
            if not emails:
                response = f"No emails found in {folder}."
            else:
                response = f"📧 Found {len(emails)} email(s) in {folder}:\n\n"
                for i, email_data in enumerate(emails, 1):
                    response += f"{i}. **From:** {email_data['from']}\n"
                    response += f"   **Subject:** {email_data['subject']}\n"
                    response += f"   **Date:** {email_data['date']}\n"
                    response += f"   **Preview:** {email_data['preview']}\n\n"

            return [TextContent(type="text", text=response)]

        elif name == "filter_emails":
            sender = arguments.get("sender")
            subject = arguments.get("subject")
            is_unread = arguments.get("is_unread")
            folder = arguments.get("folder", "INBOX")

            emails = email_client.filter_emails(
                sender=sender,
                subject=subject,
                is_unread=is_unread,
                folder=folder
            )

            # Format response
            filters = []
            if sender:
                filters.append(f"sender: {sender}")
            if subject:
                filters.append(f"subject contains: {subject}")
            if is_unread is not None:
                filters.append(f"unread: {is_unread}")

            filter_text = ", ".join(filters) if filters else "no filters"

            if not emails:
                response = f"🔍 No emails found matching criteria ({filter_text})."
            else:
                response = f"🔍 Found {len(emails)} email(s) matching criteria ({filter_text}):\n\n"
                for i, email_data in enumerate(emails, 1):
                    response += f"{i}. **From:** {email_data['from']}\n"
                    response += f"   **Subject:** {email_data['subject']}\n"
                    response += f"   **Date:** {email_data['date']}\n"
                    response += f"   **Preview:** {email_data['preview']}\n\n"

            return [TextContent(type="text", text=response)]

        elif name == "send_email":
            to = arguments["to"]
            subject = arguments["subject"]
            body = arguments["body"]
            cc = arguments.get("cc")

            result = email_client.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc
            )

            response = f"✅ Email sent successfully!\n\n"
            response += f"**To:** {to}\n"
            if cc:
                response += f"**CC:** {cc}\n"
            response += f"**Subject:** {subject}\n"
            response += f"**Sent at:** {result['timestamp']}"

            return [TextContent(type="text", text=response)]

        elif name == "get_unread_count":
            folder = arguments.get("folder", "INBOX")

            count = email_client.get_unread_count(folder=folder)

            response = f"📬 You have **{count}** unread email(s) in {folder}."

            return [TextContent(type="text", text=response)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        error_response = f"❌ Error: {str(e)}"
        return [TextContent(type="text", text=error_response)]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
