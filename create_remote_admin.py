import psycopg2
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.hashers import make_password

DATABASE_URL = "postgresql://brollopsplanner_db_user:wNhdgAtPjChqFC0SzFtJbr9S9itiW1cc@dpg-d8snfmjeo5us73enrllg-a.frankfurt-postgres.render.com/brollopsplanner_db"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    hashed_pw = make_password('DittTillfälligaLösenord123!')
    
    cur.execute("""
        INSERT INTO auth_user 
        (username, email, password, is_staff, is_superuser, is_active, date_joined, first_name, last_name)
        VALUES (%s, %s, %s, true, true, true, NOW(), %s, %s)
        ON CONFLICT (username) DO NOTHING
    """, ['admin', 'admin@example.com', hashed_pw, '', ''])
    
    conn.commit()
    print("Admin-användare skapad!")
    print("Användarnamn: admin")
    print("Lösenord: DittTillfälligaLösenord123!")
    
except Exception as e:
    print(f"Fel: {e}")
    
finally:
    if 'conn' in locals():
        cur.close()
        conn.close()