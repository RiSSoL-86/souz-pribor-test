import datetime as dt

JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_LIFETIME = dt.timedelta(minutes=15)
JWT_REFRESH_TOKEN_LIFETIME = dt.timedelta(days=7)
