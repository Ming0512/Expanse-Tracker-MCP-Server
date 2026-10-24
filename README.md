# Expense Tracker MCP Server

A lightweight **Model Context Protocol (MCP) server** built with Python, FastMCP, and SQLite that enables AI assistants to manage, retrieve, update, and analyze personal expenses using natural language.

The server exposes expense management operations as MCP tools and provides predefined expense categories through an MCP resource. It supports remote integration with MCP-compatible AI clients when deployed on a publicly accessible server.

## Features

- **Add Expenses:** Record expenses with dates, amounts, categories, subcategories, and optional notes.
- **View Expenses:** Retrieve expense records within a specified date range.
- **Update Expenses:** Modify existing expense records using their unique IDs.
- **Delete Expenses:** Remove expense records by ID.
- **Expense Summaries:** Calculate total spending grouped by category, with optional category filtering.
- **Expense Categories:** Access predefined categories and subcategories through an MCP resource.
- **SQLite Database:** Lightweight persistent storage without requiring an external database service.
- **Remote MCP Access:** HTTP transport support for integration with compatible AI applications.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastMCP | MCP server framework |
| SQLite | Expense data storage |
| JSON | Category and subcategory configuration |
| MCP | AI tool and resource integration |
| HTTP | Remote client-server communication |

## Project Structure

```text
Expense-Tracker-MCP-Server/
│
├── main.py              # FastMCP server and expense tools
├── categories.json      # Expense categories and subcategories
├── expenses.db          # SQLite database (auto-generated)
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock              # Locked dependencies (if using uv)
├── .gitignore
└── README.md
```

## MCP Tools

The server provides five MCP tools for expense management.

| Tool | Description |
|---|---|
| `add_expanse` | Add a new expense record |
| `list_expanses` | Retrieve expenses within a date range |
| `update_expense` | Update selected fields of an existing expense |
| `delete_expense` | Delete an expense using its ID |
| `summarize` | Calculate total expenses grouped by category |

*Note: Tool names match the current implementation.*

### 1. Add Expense

**Tool:** `add_expanse`

Adds a new expense record to the SQLite database.

**Parameters:**
- `date`: Expense date
- `amount`: Expense amount
- `category`: Main expense category
- `subcategory`: Optional subcategory
- `note`: Optional description

Example request:

> Add an expense of ₹250 for lunch under Food, subcategory Restaurant, on 2026-10-24.

Example response:

```json
{
  "status": "Successfully added!",
  "id": 1
}
```

### 2. List Expenses

**Tool:** `list_expanses`

Retrieves all expenses within an inclusive date range, ordered by expense ID.

Example request:

> Show all my expenses between October 1 and October 24, 2026.

### 3. Update Expense

**Tool:** `update_expense`

Updates an existing expense using its unique ID. Only the fields provided are modified.

Example request:

> Update expense ID 1 and change its amount to ₹300.

### 4. Delete Expense

**Tool:** `delete_expense`

Deletes an expense record using its unique ID.

Example request:

> Delete expense ID 1.

### 5. Summarize Expenses

**Tool:** `summarize`

Calculates total spending grouped by category within a specified date range.

Example request:

> Summarize my expenses by category for October 2026.

Example response:

```json
[
  {
    "category": "Food",
    "total_amount": 3500.0
  },
  {
    "category": "Transport",
    "total_amount": 1200.0
  },
  {
    "category": "Utilities",
    "total_amount": 2000.0
  }
]
```

## MCP Resources

### Expense Categories

**Resource URI:** `expense://categories`

**MIME Type:** `application/json`

Provides predefined expense categories and subcategories from `categories.json`.

The resource reads the JSON file dynamically, allowing category updates without restarting the server.

## Installation and Local Setup

### Prerequisites

- Python 3.10 or later
- uv package manager (recommended)
- An MCP-compatible client

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Expense-Tracker-MCP-Server.git
cd Expense-Tracker-MCP-Server
```

Replace `<your-username>` with your GitHub username.

### 2. Install Dependencies

Using uv:

```bash
uv sync
```

Alternatively, install FastMCP using pip:

```bash
pip install fastmcp
```

### 3. Start the MCP Server

```bash
uv run python main.py
```

The server runs locally at:

```text
http://127.0.0.0:8000/mcp
```

The SQLite database is automatically initialized when the application starts.

## Deployment on MCP Cloud

The application is designed to support remote MCP communication using HTTP transport.

### Deployment Steps

1. Push the project to a GitHub repository.
2. Sign in to your preferred MCP Cloud hosting platform.
3. Create a new MCP server deployment.
4. Connect the GitHub repository or upload the required project files.
5. Configure the Python environment and dependencies.
6. Set the server start command according to the hosting platform's requirements.
7. Configure the server to listen on the host and port required by the platform.
8. Deploy the application and obtain its public MCP endpoint.

**Example remote endpoint:**

```text
https://your-server.example.com/mcp
```

The actual URL depends on the deployment provider.

### Remote MCP Client Configuration

For MCP clients that support remote HTTP servers, an example configuration is:

```json
{
  "mcpServers": {
    "expense-tracker": {
      "type": "http",
      "url": "https://your-server.example.com/mcp"
    }
  }
}
```

Configuration formats vary across MCP clients.

## Database Schema

The application uses SQLite to store expense records.

**Table:** `expenses`

| Column | Data Type | Description |
|---|---|---|
| id | INTEGER | Primary key, auto-incremented |
| date | TEXT | Expense date |
| amount | REAL | Expense amount |
| category | TEXT | Main expense category |
| subcategory | TEXT | Optional subcategory |
| note | TEXT | Optional description |

## Example Natural Language Queries

Once connected to an MCP-compatible AI assistant, users can perform operations such as:

- "Add ₹500 spent on groceries today."
- "Show my expenses for the last seven days."
- "How much did I spend on food this month?"
- "Update expense ID 5 to ₹750."
- "Delete expense ID 3."
- "Summarize my spending by category this month."

The AI assistant can invoke the appropriate MCP tools based on the user's request.

## Security and Deployment Considerations

- Use HTTPS for remote MCP connections.
- Configure authentication before exposing expense modification tools publicly.
- Avoid committing personal expense records or database files to GitHub.
- Use persistent storage for SQLite when deploying to cloud infrastructure.
- Validate expense inputs and use consistent date formatting (`YYYY-MM-DD`).
- Use separate databases or access controls when supporting multiple users.

**Important:** The current implementation does not include authentication or per-user data isolation. It should not be exposed as a publicly writable service without additional access controls.

## Future Improvements

- User authentication and authorization
- Multi-user expense management
- Monthly and yearly spending analytics
- Budget planning and spending limits
- Expense visualization and reporting
- Export expenses to CSV
- Cloud-hosted database integration
- Automated expense categorization
