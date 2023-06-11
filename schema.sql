DROP TABLE IF EXISTS urls_data;

CREATE TABLE urls_data (
    shortcode TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    created TIMESTAMP NOT NULL,
    lastRedirect TIMESTAMP,
    redirectCount INTEGER NOT NULL
);