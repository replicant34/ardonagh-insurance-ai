from app.database.connection import get_db_connection


def test_database_connection():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.Policies
        """)

        policy_count = cursor.fetchone()[0]

        print(f"\nConnected successfully!")
        print(f"Policies in database: {policy_count}")

        assert policy_count >= 0

    finally:
        connection.close()