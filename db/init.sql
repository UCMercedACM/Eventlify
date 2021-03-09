CREATE TABLE event (
    id SERIAL,
    name TEXT,
    date TIMESTAMPTZ,
    description TEXT,
    link TEXT,
    guild_id BIGINT
);

CREATE TABLE guild (
    guild_id BIGINT,
    code TEXT,
    permissions INT
);
