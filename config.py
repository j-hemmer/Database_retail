# config.py
central_db_params = {
    "host": "localhost",
    "user": "root",
    "password": "dsci551",
    "database": "central_db"
}

shard_connections = {
    1: {"host": "localhost", "user": "root", "password": "dsci551", "database": "shard1_db"},
    2: {"host": "localhost", "user": "root", "password": "dsci551", "database": "shard2_db"},
    # Add configurations for other shards as needed
}
