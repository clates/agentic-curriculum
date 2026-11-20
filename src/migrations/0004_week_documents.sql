-- 0004 week_documents: structured weeks (WeekDoc) and a derived index of their prep checks.
-- The document is the source of truth (D3); prep_checks is rebuilt from it in the same
-- transaction on every save and exists so feedback and mastery can address checks without
-- parsing JSON (D4). Every row carries family_id (D2). A legacy-shaped summary row in
-- weekly_packets (written by week_store) keeps the existing list/get endpoints working.

CREATE TABLE week_documents (
    family_id TEXT NOT NULL REFERENCES family(family_id),
    packet_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    doc_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (family_id, packet_id),
    FOREIGN KEY (family_id, packet_id) REFERENCES weekly_packets(family_id, packet_id)
        ON DELETE CASCADE
);

CREATE TABLE prep_checks (
    family_id TEXT NOT NULL,
    packet_id TEXT NOT NULL,
    check_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    day TEXT NOT NULL,
    standard_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    PRIMARY KEY (family_id, packet_id, check_id),
    FOREIGN KEY (family_id, packet_id) REFERENCES week_documents(family_id, packet_id)
        ON DELETE CASCADE
);
CREATE INDEX idx_prep_checks_standard ON prep_checks(family_id, standard_id);
