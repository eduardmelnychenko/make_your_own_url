--DROP VIEW click_count_view;
--DROP VIEW click_source_count_view;
--DROP VIEW click_daily_cnt;
--DROP VIEW all_url_info;
DROP TABLE IF EXISTS click_log CASCADE;
DROP TABLE IF EXISTS urls CASCADE;
DROP TABLE IF EXISTS users CASCADE;

--stores all user data
CREATE TABLE users (
  id          TEXT PRIMARY KEY,
  name        TEXT        NOT NULL,
  email       TEXT UNIQUE NOT NULL,
  status      TEXT DEFAULT 'free',
  date_added  DATE DEFAULT CURRENT_DATE,
  profile_pic TEXT DEFAULT ''
);

--initial anonymous user
INSERT INTO users (id, name, email) VALUES ('-999', 'Anonymous', 'Anonymous');

--stores all url data
CREATE TABLE urls (
  suffix      TEXT NOT NULL PRIMARY KEY,
  short_url   TEXT UNIQUE NOT NULL,
  long_url    TEXT NOT NULL,
  user_id     TEXT NOT NULL  DEFAULT '-999',
  description TEXT NOT NULL  DEFAULT '',
  date_added  DATE           DEFAULT CURRENT_DATE,
  date_expire DATE           DEFAULT CURRENT_DATE + INTERVAL '30 day',
  FOREIGN KEY (user_id) REFERENCES users (id)
  ON UPDATE CASCADE
  ON DELETE CASCADE
);

--stores all clicks data
CREATE TABLE click_log (
  date_added   DATE          DEFAULT CURRENT_DATE,
  click_source TEXT NOT NULL DEFAULT 'not defined',
  suffix_id    TEXT NOT NULL,
  FOREIGN KEY (suffix_id) REFERENCES urls (suffix)
  ON UPDATE CASCADE
  ON DELETE CASCADE
);

--view to get count of clicks for url level
CREATE VIEW click_count_view AS
  SELECT
    suffix,
    long_url,
    user_id,
    count(*) AS cnt
  FROM ((SELECT
           suffix,
           long_url,
           user_id
         FROM urls) AS url_tb INNER JOIN (SELECT suffix_id
                                          FROM click_log) AS cl_logs
      ON url_tb.suffix = cl_logs.suffix_id) fin_tb
  GROUP BY 1, 2, 3;

--view to get count of clicks for url-source level
CREATE VIEW click_source_count_view AS
  SELECT
    suffix,
    long_url,
    user_id,
    click_source,
    count(*) AS cnt
  FROM ((SELECT
           suffix,
           long_url,
           user_id
         FROM urls) AS url_tb INNER JOIN (SELECT
                                            suffix_id,
                                            click_source
                                          FROM click_log) AS cl_logs
      ON url_tb.suffix = cl_logs.suffix_id) fin_tb
  GROUP BY 1, 2, 3, 4;

-- view to get daily clicks for a user urls
CREATE VIEW click_daily_cnt AS
  SELECT
    click_log.date_added AS date,
    user_id,
    count(*)             AS cnt
  FROM click_log
    JOIN urls ON click_log.suffix_id = urls.suffix
  GROUP BY 1, 2;

-- info on urls
CREATE OR REPLACE VIEW all_url_info AS
  SELECT
    suffix,
    short_url,
    long_url,
    user_id,
    description,
    date_added,
    date_expire,
    coalesce(cnt, 0) cnt
  FROM urls
    LEFT JOIN (SELECT
                 suffix_id,
                 COUNT(*) AS cnt
               FROM click_log
               GROUP BY 1) AS cnt_tab ON urls.suffix = cnt_tab.suffix_id;

INSERT INTO urls (suffix, short_url ,long_url) VALUES ('shaga', 'https://rcmnd.me/1','http://test.com');
INSERT INTO urls (suffix, short_url ,long_url) VALUES ('shaga2', 'https://rcmnd.me/12','http://test.com');
INSERT INTO click_log (suffix_id) VALUES ('shaga');
INSERT INTO click_log (suffix_id) VALUES ('shaga2');
