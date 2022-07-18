import sqlite3

def create_db():
    conn = sqlite3.connect('voice.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS "guild" (
        `guildID`       INTEGER,
        `ownerID`       INTEGER,
        `voiceChannelID`        INTEGER,
        `voiceCategoryID`       INTEGER
);''')
    c.execute('''CREATE TABLE `guildSettings` (
        `guildID`       INTEGER,
        `channelName`   TEXT,
        `channelLimit`  INTEGER
);''')
    c.execute('''CREATE TABLE `userSettings` (
        `userID`        INTEGER,
        `channelName`   TEXT,
        `channelLimit`  INTEGER
);''')
    c.execute('''CREATE TABLE `voiceChannel` (
        `userID`        INTEGER,
        `voiceID`       INTEGER
);''')
    conn.commit()
    conn.close()

create_db()