
from database import engine
from sqlalchemy import text

with engine.connect() as connection:
    result = connection.execute(text("""
        SELECT
            current_database(),
            current_user,
            inet_server_addr()::text,
            inet_server_port(),
            current_setting('data_directory')
    """))

    print("PYTHON DATABASE SERVER:")
    print(result.fetchone())

    result = connection.execute(text("""
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'users'
        ORDER BY ordinal_position
    """))

    print("\nPYTHON USERS TABLE:")
    for row in result:
        print(row)
