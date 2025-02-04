CREATE TABLE IF NOT EXISTS plots (
    created_at TIMESTAMP PRIMARY KEY DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', '-5 hours')),
    json TEXT
)
