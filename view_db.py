import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_users.db")

if not os.path.exists(db_path):
    print("Database not found! Run main.py first so it generates automatically.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("========================================")
    print("          REGISTERED USERS              ")
    print("========================================")
    print(f"{'ID':<5} | {'Username':<15} | {'High Score':<10} | {'Password Hash (SHA-256)'}")
    print("-" * 70)
    
    cursor.execute("SELECT id, username, high_score, password_hash FROM users")
    for row in cursor.fetchall():
        print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:<10} | {row[3][:15]}...")

    print("\n========================================")
    print("          MATCH HISTORY LOG             ")
    print("========================================")
    print(f"{'Match ID':<10} | {'User ID':<10} | {'Score'}")
    print("-" * 40)
    
    cursor.execute("SELECT id, user_id, score FROM match_history")
    for row in cursor.fetchall():
        print(f"{row[0]:<10} | {row[1]:<10} | {row[2]}")

    conn.close()