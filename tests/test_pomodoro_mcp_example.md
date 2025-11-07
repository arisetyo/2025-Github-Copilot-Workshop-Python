# Playwright MCP Testing Guide

## Interactive Testing (via Chat)

You can test your app by asking Copilot to use Playwright MCP tools:

```
"Navigate to http://localhost:5000 and click the Start button"
"Take a screenshot of the timer"
"Wait for 5 seconds and verify the session completed"
```

## Example Test Sequence

1. **Navigate to app**
   - Tool: `mcp_playwright_browser_navigate`
   - Result: Shows page snapshot in chat

2. **Interact with elements**
   - Tool: `mcp_playwright_browser_click`
   - Example: Click Start button (ref: e11)

3. **Evaluate JavaScript**
   - Tool: `mcp_playwright_browser_evaluate`
   - Example: Speed up timer for testing

4. **Wait and verify**
   - Tool: `mcp_playwright_browser_wait_for`
   - Verify changes in page snapshot

5. **Take screenshots**
   - Tool: `mcp_playwright_browser_take_screenshot`
   - Saves to workspace directory

## Benefits

- No test code to write
- Interactive debugging
- See results immediately in chat
- Great for manual QA and exploration

## When to use traditional pytest-playwright instead

- Need automated CI/CD testing
- Want test history/reporting
- Need to run tests unattended
- Multiple test suites to maintain
