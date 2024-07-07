-- in postgresql database (version at least 15.0),
-- with pgvector extension (version 0.5.0)

-- create table sedimentology_paper_paragraph
DROP TABLE IF EXISTS sedimentology_paper_paragraph;
CREATE TABLE sedimentology_paper_paragraph
(
    doi          text,
    journal      text,
    title        text,
    authors      text,
    time         text,
    content      text,
    content_type text,
    content_vec  vector(384)
);

-- create table sedimentology_paper_sentence
DROP TABLE IF EXISTS sedimentology_paper_sentence;
CREATE TABLE sedimentology_paper_sentence
(
    doi          text,
    journal      text,
    title        text,
    authors      text,
    time         text,
    content      text,
    content_type text,
    content_vec  vector(384)
);