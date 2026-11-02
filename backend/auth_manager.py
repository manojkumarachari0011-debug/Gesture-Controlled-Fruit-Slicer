import sqlite3
import hashlib
import os

class AuthManager:
    def __init__(self, db_name="game_users.db"):
        # The database file will be created in your root folder automatically
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Create Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                high_score INTEGER DEFAULT 0
            )
        ''')
        
        # 2. Create Match History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        if not username or not password:
            return False, "Username and password cannot be empty."
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # lower() ensures usernames are case-insensitive
            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (username.lower(), self._hash_password(password)))
            conn.commit()
            return True, "Registration successful! You can now login."
        except sqlite3.IntegrityError:
            return False, "Username already exists. Please choose another."
        finally:
            conn.close()

    def login(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, high_score FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username.lower(), self._hash_password(password)))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {"id": user[0], "username": user[1], "high_score": user[2]}
        else:
            return False, "Invalid username or password."

    def update_high_score(self, username, score):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT high_score FROM users WHERE username = ?', (username.lower(),))
        current_high = cursor.fetchone()[0]
        
        if score > current_high:
            cursor.execute('UPDATE users SET high_score = ? WHERE username = ?', (score, username.lower()))
            conn.commit()
            new_high = score
        else:
            new_high = current_high
            
        conn.close()
        return new_high

    def record_match(self, user_id, score):
        """Inserts the final score of a game into the match_history table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO match_history (user_id, score)
            VALUES (?, ?)
        ''', (user_id, score))
        
        conn.commit()
        conn.close()

    def get_dashboard_stats(self, user_id):
        """Fetches total plays and the full array of historical scores for the grid."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count total games played
        cursor.execute("SELECT COUNT(*) FROM match_history WHERE user_id = ?", (user_id,))
        total_plays = cursor.fetchone()[0]

        # Fetch ALL match history for the full screen grid
        cursor.execute("SELECT score FROM match_history WHERE user_id = ? ORDER BY id ASC", (user_id,))
        history = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return total_plays, history