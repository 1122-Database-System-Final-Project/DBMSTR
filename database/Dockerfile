FROM alpine:latest

RUN apk add --update sqlite

WORKDIR /db

COPY backup.sq3 /db/

RUN sqlite3 /db/database.db -init /database/backup.sq3

CMD ["tail", "-f", "/dev/null"]