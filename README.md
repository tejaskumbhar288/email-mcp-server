# 📧 Email Alert MCP Server

An MCP (Model Context Protocol) server that exposes email operations as tools for AI agents. This allows Claude or other LLM-based agents to naturally read, filter, send emails, and check unread counts through the MCP protocol.

## 🎯 Features

- **Read Emails**: Fetch recent emails from your inbox
- **Filter Emails**: Search emails by sender, subject, or unread status
- **Send Emails**: Compose and send emails through your account
- **Unread Count**: Check how many unread messages you have
- **Works with Gmail**: Uses SMTP/IMAP for universal compatibility

## 🛠️ Prerequisites

- Python 3.10 or higher
- Gmail account with App Password enabled (see setup below)
- Claude Desktop or any MCP-compatible client

## 📦 Installation

### 1. Clone or Navigate to the Project

```bash
cd "C:\Users\tejas\OneDrive\Desktop\Email MCP server"
```

### 2. Create Virtual Environment (if not already created)

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔐 Gmail Setup (App Password)

For security, Gmail requires an **App Password** instead of your regular password when using SMTP/IMAP.

### Steps to Get Gmail App Password:

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already enabled)
3. Scroll down to **App passwords**
4. Click **Select app** → Choose "Mail"
5. Click **Select device** → Choose "Other" → Name it "MCP Server"
6. Click **Generate**
7. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
8. Update your `.env` file with this App Password

### Update .env File

Your `.env` file should look like this:

```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-char-app-password

IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
IMAP_PORT=993
SMTP_PORT=587

OPENAI_API_KEY=your-openai-api-key (optional)
```

## 🚀 Running the Server

### Test Locally

```bash
python server.py
```

The server will start and listen for MCP protocol messages via stdin/stdout.

## 🔧 Connecting to Claude Desktop

To use this MCP server with Claude Desktop, you need to add it to your Claude Desktop configuration.

### 1. Find Your Claude Config File

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Add MCP Server Configuration

Edit the config file and add (see `claude_desktop_config.example.json` for reference):

```json
{
  "mcpServers": {
    "email-alert": {
      "command": "python",
      "args": [
        "/absolute/path/to/your/project/server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/your/project"
      }
    }
  }
}
```

**Windows Example:**
```json
{
  "mcpServers": {
    "email-alert": {
      "command": "C:\\Users\\YourName\\path\\to\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourName\\path\\to\\Email MCP server\\server.py"
      ]
    }
  }
}
```

**Mac/Linux Example:**
```json
{
  "mcpServers": {
    "email-alert": {
      "command": "/usr/bin/python3",
      "args": [
        "/home/username/Email-MCP-server/server.py"
      ]
    }
  }
}
```

**Note:** Replace paths with your actual project location.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

## 🧪 Testing the Tools

Once connected to Claude Desktop, you can test the email tools with natural language:

### Examples:

**Check Unread Emails:**
```
"How many unread emails do I have?"
```

**Read Recent Emails:**
```
"Show me my 5 most recent emails"
```

**Filter by Sender:**
```
"Show me all emails from john@example.com"
```

**Search by Subject:**
```
"Find emails with 'meeting' in the subject"
```

**Send an Email:**
```
"Send an email to sangeeta@example.com with subject 'Meeting Reminder' and tell her about the 4 PM meeting"
```

## 🔧 Available MCP Tools

### 1. `read_emails`
Read recent emails from inbox or specified folder.

**Parameters:**
- `count` (number, optional): Number of emails to retrieve (default: 10)
- `folder` (string, optional): Email folder (default: "INBOX")

### 2. `filter_emails`
Search and filter emails by criteria.

**Parameters:**
- `sender` (string, optional): Filter by sender email address
- `subject` (string, optional): Filter by subject (substring match)
- `is_unread` (boolean, optional): Filter by unread status
- `folder` (string, optional): Email folder (default: "INBOX")

### 3. `send_email`
Send an email to a recipient.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body content
- `cc` (string, optional): CC recipient email address

### 4. `get_unread_count`
Get count of unread emails.

**Parameters:**
- `folder` (string, optional): Email folder (default: "INBOX")

## 🏗️ Project Structure

```
Email MCP server/
├── server.py              # Main MCP server
├── email_client.py        # Email operations (SMTP/IMAP)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (NOT in git)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔒 Security Notes

⚠️ **Important:**

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use App Passwords** - Never use your main Gmail password
3. **Restrict Access** - Keep your MCP server local and trusted
4. **Monitor Usage** - Review sent emails periodically

## 📤 Pushing to GitHub

### ✅ Safe to Push:
- `server.py` - Your MCP server code
- `email_client.py` - Email operations
- `test_email.py` - Testing script
- `requirements.txt` - Dependencies list
- `README.md` - Documentation
- `.env.example` - Template (NO real credentials)
- `claude_desktop_config.example.json` - Config template
- `.gitignore` - Git ignore rules

### ❌ NEVER Push:
- `.env` - Contains your email password! (Auto-ignored)
- `claude_desktop_config.json` - Has your specific paths (Auto-ignored)
- `venv/` - Virtual environment folder (Auto-ignored)
- `__pycache__/` - Python cache (Auto-ignored)

The `.gitignore` file is already configured to protect sensitive files.

## 🐛 Troubleshooting

### "Authentication failed" Error

- Make sure you're using a Gmail **App Password**, not your regular password
- Verify 2-Step Verification is enabled on your Google account
- Check that `EMAIL_USER` and `EMAIL_PASS` in `.env` are correct

### "Connection refused" Error

- Check your internet connection
- Verify firewall isn't blocking SMTP (port 587) or IMAP (port 993)
- Ensure Gmail hasn't flagged your account for suspicious activity

### "MCP server not showing in Claude Desktop"

- Verify the path in `claude_desktop_config.json` is correct
- Check that Python is in your system PATH
- Restart Claude Desktop after config changes
- Check Claude Desktop logs for errors

## 📚 Learn More

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Gmail SMTP/IMAP Settings](https://support.google.com/mail/answer/7126229)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

**Built with ❤️ using the Model Context Protocol**
