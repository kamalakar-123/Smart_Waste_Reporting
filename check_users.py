import sqlite3

conn = sqlite3.connect('waste_report.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('SELECT id, username, email, role, firebase_uid FROM users')
users = cur.fetchall()

print(f'Total users: {len(users)}\n')

if len(users) == 0:
    print('No users found in database.')
else:
    print('Users in database:')
    print('-' * 80)
    for user in users:
        firebase_status = '✓ Has Firebase' if user['firebase_uid'] else '✗ No Firebase'
        print(f"{user['id']}. {user['username']} ({user['email']}) - Role: {user['role']} - {firebase_status}")

conn.close()
