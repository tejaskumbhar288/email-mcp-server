 Complete Explanation: How We Built the Email MCP Server

  Let me break down everything we did step by step:

  ---
  📐 Architecture Overview

  ┌─────────────────────────┐
  │   AI Agent (Claude)     │  ← User asks: "Show me my emails"
  └───────────┬─────────────┘
              │
              │ MCP Protocol (JSON-RPC)
              │ Tool Calls & Responses
              │
  ┌───────────▼─────────────┐
  │   MCP Server            │  ← Our server.py
  │   (server.py)           │     Exposes 4 tools
  └───────────┬─────────────┘
              │
              │ Python functions
              │
  ┌───────────▼─────────────┐
  │   Email Client          │  ← Our email_client.py
  │   (email_client.py)     │     Handles SMTP/IMAP
  └───────────┬─────────────┘
              │
              │ SMTP/IMAP protocols
              │
  ┌───────────▼─────────────┐
  │   Gmail Server          │  ← Your Gmail account
  │   (Google)              │
  └─────────────────────────┘

  ---
  🔧 Components We Built

  1. Email Client (email_client.py) - The Email Worker

  This handles all the actual email operations:

  class EmailClient:
      # Connects to Gmail using IMAP (reading) and SMTP (sending)

      def read_emails():
          # Uses IMAP to fetch emails from Gmail
          # Parses email headers, body, attachments
          # Returns clean email data

      def filter_emails():
          # Searches emails by sender, subject, unread status
          # Uses IMAP search commands

      def send_email():
          # Composes email with MIME format
          # Sends via SMTP

      def get_unread_count():
          # Counts UNSEEN emails via IMAP

  Key Technologies:
  - imaplib - For reading emails (IMAP protocol)
  - smtplib - For sending emails (SMTP protocol)
  - email module - For parsing/composing email messages

  ---
  2. MCP Server (server.py) - The Bridge

  This is the heart of the system - it speaks the MCP protocol:

  from mcp.server import Server

  app = Server("email-alert-server")

  # 1. Register Tools (tells Claude what's available)
  @app.list_tools()
  async def list_tools() -> list[Tool]:
      return [
          Tool(name="read_emails", description="...", inputSchema={...}),
          Tool(name="filter_emails", ...),
          Tool(name="send_email", ...),
          Tool(name="get_unread_count", ...)
      ]

  # 2. Handle Tool Calls (when Claude wants to use a tool)
  @app.call_tool()
  async def call_tool(name: str, arguments: dict):
      if name == "read_emails":
          emails = email_client.read_emails(...)
          return formatted_response
      # ... handle other tools

  What's Happening:

  1. Tool Registration: Claude asks "What can you do?"
    - Server responds with 4 tools and their parameters
  2. Tool Execution: Claude says "Call read_emails with count=5"
    - Server calls email_client.read_emails(count=5)
    - Returns formatted results to Claude

  ---
  🔌 How MCP Protocol Works

  MCP = Model Context Protocol (created by Anthropic)

  It's a standardized way for AI models to use external tools:

  Message Flow Example:

  User: "Show me my 3 recent emails"

  Claude → MCP Server:
  {
    "method": "tools/call",
    "params": {
      "name": "read_emails",
      "arguments": {
        "count": 3,
        "folder": "INBOX"
      }
    }
  }

  MCP Server → Email Client:
  email_client.read_emails(count=3, folder="INBOX")

  Email Client → Gmail:
  IMAP Command: FETCH 1:3 (RFC822)

  Gmail → Email Client:
  Returns raw email data

  Email Client → MCP Server:
  [
    {"subject": "...", "from": "...", "body": "..."},
    {"subject": "...", "from": "...", "body": "..."},
    ...
  ]

  MCP Server → Claude:
  {
    "content": [
      {
        "type": "text",
        "text": "📧 Found 3 emails:\n\n1. From: John..."
      }
    ]
  }

  Claude → User:
  "You have 3 recent emails:
  1. From John about Meeting..."

  ---
  🔐 Authentication & Configuration

  .env File - Your Credentials

  EMAIL_USER=tejaskumbhar55555@gmail.com
  EMAIL_PASS=ouvg izhm azhe cfxa  ← App Password (NOT regular password!)

  IMAP_SERVER=imap.gmail.com     ← Gmail's IMAP server
  SMTP_SERVER=smtp.gmail.com     ← Gmail's SMTP server
  IMAP_PORT=993                  ← Secure IMAP port
  SMTP_PORT=587                  ← Secure SMTP port (with STARTTLS)

  Why App Password?
  - Gmail blocks regular passwords for security
  - App Passwords are specific to one application
  - Can be revoked without changing main password

  ---
  🔄 How Claude Desktop Connects

  claude_desktop_config.json

  {
    "mcpServers": {
      "email-alert": {
        "command": "python.exe",           ← Run Python
        "args": ["server.py"]              ← Execute our server
      }
    }
  }

  What Happens:

  1. Startup: Claude Desktop reads config file
  2. Launch: Runs python.exe server.py as a subprocess
  3. Connection: Communicates via stdin/stdout (stdio transport)
  4. Discovery: Asks server "What tools do you have?"
  5. Ready: Tools appear in Claude's available tools

  ---
  🛠️ The 4 Tools We Created

  1. read_emails - Fetch Recent Emails

  Input: {
    "count": 10,          # How many emails
    "folder": "INBOX"     # Which folder
  }

  Output: List of emails with:
  - Subject
  - From (sender)
  - Date
  - Body preview

  2. filter_emails - Search Emails

  Input: {
    "sender": "john@example.com",   # Optional
    "subject": "meeting",           # Optional
    "is_unread": true              # Optional
  }

  Output: Matching emails

  3. send_email - Send Emails

  Input: {
    "to": "recipient@example.com",
    "subject": "Hello",
    "body": "Email content",
    "cc": "other@example.com"      # Optional
  }

  Output: Success confirmation

  4. get_unread_count - Count Unread

  Input: {
    "folder": "INBOX"
  }

  Output: Number of unread emails

  ---
  📊 Data Flow Example

  Let's trace: "Send email to john@test.com saying hi"

  1. User speaks to Claude
     ↓
  2. Claude understands: "Need to send email"
     ↓
  3. Claude calls: send_email(to="john@test.com", subject="Hi", body="Hello!")
     ↓
  4. MCP Server receives call
     ↓
  5. email_client.send_email() runs
     ↓
  6. Creates MIME message:
     From: tejaskumbhar55555@gmail.com
     To: john@test.com
     Subject: Hi
     Body: Hello!
     ↓
  7. Connects to smtp.gmail.com:587
     ↓
  8. Authenticates with App Password
     ↓
  9. Sends email via SMTP
     ↓
  10. Returns success to MCP Server
      ↓
  11. MCP Server formats response
      ↓
  12. Claude receives "Email sent successfully"
      ↓
  13. Claude tells user: "I've sent the email!"

  ---
  🎯 Key Concepts

  1. MCP (Model Context Protocol)

  - Standardized protocol for AI ↔ Tools
  - Like a USB port - works with any compatible device
  - Claude can use ANY MCP server

  2. IMAP (Internet Message Access Protocol)

  - For reading emails from server
  - Keeps emails on server (not downloaded)
  - Supports folders, search, flags

  3. SMTP (Simple Mail Transfer Protocol)

  - For sending emails
  - Standard email sending protocol
  - Port 587 with STARTTLS for security

  4. Async/Await

  - MCP uses async Python
  - Allows handling multiple requests
  - Non-blocking operations

  ---
  📁 File Structure Review

  Email MCP server/
  ├── server.py              ← MCP Protocol Handler
  │   └── Defines 4 tools
  │   └── Handles tool calls
  │   └── Formats responses
  │
  ├── email_client.py        ← Email Operations
  │   └── IMAP connection
  │   └── SMTP sending
  │   └── Email parsing
  │
  ├── .env                   ← Your Credentials
  │   └── EMAIL_USER
  │   └── EMAIL_PASS (App Password)
  │   └── IMAP/SMTP settings
  │
  ├── requirements.txt       ← Dependencies
  │   └── mcp (MCP SDK)
  │   └── python-dotenv
  │   └── openai (for future features)
  │
  └── test_email.py         ← Testing Script
      └── Verifies connection
      └── Tests email operations

  ---
  🚀 Why This is Powerful

  Before MCP:
  User: "Send email to John"
  AI: "I can't send emails, but here's how you can do it..."

  With MCP:
  User: "Send email to John"
  AI: [Uses send_email tool] "Done! Email sent to John."

  Natural Language → Actual Actions!

  ---
  💡 What Makes It Work

  1. Standardized Protocol - MCP is like HTTP for AI tools
  2. Tool Schema - Clear input/output contracts
  3. Async Communication - Fast, non-blocking
  4. Secure Authentication - App Passwords, not main password
  5. Standard Protocols - SMTP/IMAP are universal

  ---
  🎨 Summary

  You now have:

  ✅ Email reading via IMAP✅ Email sending via SMTP✅ Search & filtering capabilities✅ Natural language interface through Claude✅ Secure authentication      
  with App Passwords✅ MCP-compliant server that works with any MCP client

  This is a real AI agent that can actually DO things in the real world (manage your email), not just talk about them!