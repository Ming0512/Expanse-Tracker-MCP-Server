
import asyncio
import json
import os
from pathlib import Path

import aiosqlite
from fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = Path(os.environ.get("DB_PATH", str(BASE_DIR / "expenses.db")))
CATEGORIES_PATH = BASE_DIR / "categories.json"

mcp = FastMCP(name="ExpenseTracker")


# ---------------- DATABASE ----------------

async def get_db():
    """Create an asynchronous SQLite connection."""
    db = await aiosqlite.connect(
        str(DB_PATH),
        timeout=30
    )
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA busy_timeout = 30000")
    return db


async def init_db():
    """Initialize the database asynchronously."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(DB_PATH), timeout=30) as db:
        await db.execute("PRAGMA journal_mode = WAL")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

        await db.commit()


# ---------------- ADD EXPENSE ----------------

@mcp.tool()
async def add_expanse(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
) -> dict:
    """Add a new expense entry to the database."""

    async with await get_db() as db:
        cur = await db.execute(
            """
            INSERT INTO expenses
            (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note)
        )

        await db.commit()

        return {
            "status": "success",
            "message": "Expense added successfully.",
            "id": cur.lastrowid
        }


# ---------------- LIST EXPENSES ----------------

@mcp.tool()
async def list_expanses(
    start_date: str,
    end_date: str
) -> list[dict]:
    """List expenses within an inclusive date range."""

    async with await get_db() as db:
        async with db.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date)
        ) as cur:
            rows = await cur.fetchall()

        return [dict(row) for row in rows]


# ---------------- DELETE EXPENSE ----------------

@mcp.tool()
async def delete_expense(expense_id: int) -> dict:
    """Delete an expense using its unique ID."""

    async with await get_db() as db:
        cur = await db.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        await db.commit()

        if cur.rowcount == 0:
            return {
                "status": "error",
                "message": f"Expense with ID {expense_id} not found."
            }

        return {
            "status": "success",
            "message": f"Expense with ID {expense_id} deleted successfully."
        }


# ---------------- UPDATE EXPENSE ----------------

@mcp.tool()
async def update_expense(
    expense_id: int,
    date: str | None = None,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    note: str | None = None
) -> dict:
    """Update an existing expense by ID."""

    updates = []
    params = []

    fields = {
        "date": date,
        "amount": amount,
        "category": category,
        "subcategory": subcategory,
        "note": note
    }

    for field, value in fields.items():
        if value is not None:
            updates.append(f"{field} = ?")
            params.append(value)

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

    async with await get_db() as db:
        cur = await db.execute(query, params)
        await db.commit()

        if cur.rowcount == 0:
            return {
                "status": "error",
                "message": f"Expense with ID {expense_id} not found."
            }

        return {
            "status": "success",
            "message": f"Expense with ID {expense_id} updated successfully."
        }


# ---------------- SUMMARIZE EXPENSES ----------------

@mcp.tool()
async def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None
) -> list[dict]:
    """Summarize expenses by category within an inclusive date range."""

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

    async with await get_db() as db:
        async with db.execute(query, params) as cur:
            rows = await cur.fetchall()

        return [dict(row) for row in rows]


# ---------------- MCP RESOURCE ----------------

@mcp.resource("expense://categories", mime_type="application/json")
async def categories() -> str:
    """Read expense categories from JSON."""

    def read_categories():
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return f.read()

    return await asyncio.to_thread(read_categories)


# ---------------- START SERVER ----------------

if __name__ == "__main__":

    async def main():
        await init_db()
        await mcp.run_async(
            transport="http",
            host="127.0.0.1",
            port=8000
        )

    asyncio.run(main())
