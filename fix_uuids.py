import sqlite3
import uuid

conn = sqlite3.connect('e:\\SmartShop\\SmartShop\\db.sqlite3')
c = conn.cursor()
c.execute('SELECT id FROM users_profile')
rows = c.fetchall()
for row in rows:
    new_uuid = str(uuid.uuid4()).replace('-', '')
    c.execute('UPDATE users_profile SET email_verification_token = ? WHERE id = ?', (new_uuid, row[0]))
conn.commit()
conn.close()
print("Fixed duplicate UUIDs in users_profile")
