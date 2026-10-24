from fastmcp import FastMCP
import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP(name="ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

init_db()

@mcp.tool
def add_expanse(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to a database."""
    
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "Successfully added!", "id": cur.lastrowid}
    

@mcp.tool
def list_expanses(start_date, end_date):
    """List expanses entires within the inclusive date range."""
    
    with sqlite3.connect(DB_PATH) as c:
            cur = c.execute(
                    """
                    SELECT id, date, amount, category, subcategory, note 
                    FROM expenses
                    WHERE date BETWEEN ? AND ?
                    ORDER BY id ASC
                    """,
                    (start_date, end_date)
                )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
           

@mcp.tool()
def delete_expense(expense_id: int) -> dict:
    """Delete an expense entry using its unique ID."""

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        if cur.rowcount == 0:
            return {
                "status": "error",
                "message": f"Expense with ID {expense_id} not found."
            }

        return {
            "status": "success",
            "message": f"Expense with ID {expense_id} deleted successfully."
        }


@mcp.tool()
def update_expense(
    expense_id: int,
    date: str | None = None,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    note: str | None = None
) -> dict:
    """Update an existing expense by ID. Only provided fields are updated."""

    updates = []
    params = []

    if date is not None:
        updates.append("date = ?")
        params.append(date)

    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)

    if category is not None:
        updates.append("category = ?")
        params.append(category)

    if subcategory is not None:
        updates.append("subcategory = ?")
        params.append(subcategory)

    if note is not None:
        updates.append("note = ?")
        params.append(note)

    if not updates:
        return {
            "status": "error",
            "message": "No fields provided for updating."
        }

    params.append(expense_id)

    query = f"""
        UPDATE expenses
        SET {", ".join(updates)}
        WHERE id = ?
    """

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(query, params)

        if cur.rowcount == 0:
            return {
                "status": "error",
                "message": f"Expense with ID {expense_id} not found."
            }

        return {
            "status": "success",
            "message": f"Expense with ID {expense_id} updated successfully."
        }
        
        
@mcp.tool()
def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None
) -> list[dict]:
    """Summarize expenses by category within an inclusive date range."""

    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]

        return [dict(zip(cols, r)) for r in cur.fetchall()]
        
        
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.0", port=8000)
        