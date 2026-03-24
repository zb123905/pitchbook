# Quick Setup Guide - QQ Email Configuration

## Step-by-Step Instructions

### Step 1: Enable QQ Mail IMAP Service

1. **Login to QQ Mail**
   - Visit: https://mail.qq.com
   - Login with your QQ account

2. **Enable IMAP Service**
   - Click **Settings** (设置) in top right
   - Select **Account** (账户)
   - Find **IMAP/SMTP Service**
   - Click **Enable** (开启服务)

3. **Generate Authorization Code**
   - Follow the verification process (SMS or security question)
   - You will receive a **16-digit authorization code**
   - **IMPORTANT**: Save this code, you'll need it for configuration

### Step 2: Configure Email MCP Server

1. **Navigate to email-mcp directory**
   ```bash
   cd E:\pitch\email-mcp
   ```

2. **Edit .env file**
   - Open `.env` in a text editor
   - Replace with your actual credentials:
   ```env
   EMAIL_USER=123456789@qq.com
   EMAIL_PASS=abcdefghijklmnop
   EMAIL_HOST=imap.qq.com
   EMAIL_PORT=993
   PORT=3000
   ```

3. **Install dependencies**
   ```bash
   npm install --registry=https://registry.npmmirror.com
   ```

4. **Test the server**
   ```bash
   npm start
   ```

You should see:
```
Email MCP Server running on port 3000
IMAP Config: imap.qq.com:993
User: your_qq@qq.com

Waiting for requests...
```

### Step 3: Start the Automation System

1. **Run start.bat**
   ```bash
   cd E:\pitch
   start.bat
   ```

Or manually:

2. **Start email server in one terminal**
   ```bash
   cd E:\pitch\email-mcp
   npm start
   ```

3. **Run main program in another terminal**
   ```bash
   cd E:\pitch
   .venv\Scripts\activate
   python main.py
   ```

## Troubleshooting

### Problem: "LOGIN failed"
**Solution:**
- Make sure you're using the 16-digit **authorization code**, NOT your QQ password
- Re-generate the authorization code in QQ Mail settings
- Verify IMAP service is enabled

### Problem: "Connection timeout"
**Solution:**
- Check internet connection
- Verify IMAP service is enabled
- Try a different network

### Problem: Server won't start
**Solution:**
- Check if port 3000 is already in use
- Run `netstat -ano | findstr :3000` to check
- Change PORT in `.env` if needed

### Problem: No emails found
**Solution:**
- Make sure you have emails with "pitchbook" in subject or sender
- Check that emails are in INBOX folder
- Try adjusting search query in code

## Quick Test

Test email server separately:

```bash
# Start server
cd E:\pitch\email-mcp
npm start

# In another terminal, test health endpoint
curl http://localhost:3000/health
```

Expected response:
```json
{"status":"ok","message":"Email MCP Server is running"}
```

## Configuration Files

- `.env` - Email credentials (create this)
- `server.js` - Main server code
- `package.json` - Node.js dependencies

## Need Help?

1. Check QQ Mail IMAP documentation
2. Review server console output for errors
3. Test with simple IMAP client first
