CREATE TABLE event (
    id SERIAL,
    name TEXT,
    date TIMESTAMPTZ,
    description TEXT,
    link TEXT
);

CREATE TABLE discord_server (
    name TEXT
);
