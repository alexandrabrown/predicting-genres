import sqlite3
conn = sqlite3.connect('mxm_dataset.db')

def get_track(track_id):
    c = conn.cursor()
    c.execute('SELECT word, count FROM Lyrics WHERE track_id="%s"' % track_id)
    words = c.fetchall()
    c.close()

    return words