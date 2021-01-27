CREATE TABLE event (
    id SERIAL,
    name TEXT,
    date TIMESTAMPTZ,
    description TEXT,
    link TEXT,
    guild_id BIGINT
);
