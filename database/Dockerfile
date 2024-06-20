FROM alpine:latest

RUN apk add --update sqlite

WORKDIR /database

COPY backup.sq3 /database/

RUN sqlite3 /database/database.db -init /database/backup.sq3
