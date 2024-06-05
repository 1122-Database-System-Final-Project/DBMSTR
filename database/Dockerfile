FROM alpine:latest

RUN apk add --update sqlite

WORKDIR /database

COPY create_database.sql /database/

RUN sqlite3 /database/database.db -init /database/create_database.sql

CMD ["sqlite3", "/database/database.db"]
