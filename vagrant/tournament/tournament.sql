-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players (
       id SERIAL PRIMARY KEY,
       name TEXT NOT NULL,
       bye INTEGER NOT NULL DEFAULT 0
       );

CREATE TABLE matches (
       id SERIAL PRIMARY KEY,
       winner INTEGER NOT NULL REFERENCES players(id),
       loser INTEGER NOT NULL REFERENCES players(id)
       );

CREATE VIEW win_count AS 
       SELECT 
       players.id, 
       players.name, 
       players.bye, 
       (COUNT(matches.winner)+players.bye) AS wins 
       FROM players LEFT JOIN matches ON matches.winner=players.id 
       GROUP BY players.id 
       ORDER BY wins, players.bye;

CREATE VIEW match_count AS 
       SELECT 
       players.id, 
       players.name, 
       COUNT(matches.id) AS number_of_matches 
       FROM players LEFT JOIN matches ON matches.winner=players.id 
       	    OR matches.loser=players.id 
       GROUP BY players.id 
       ORDER BY players.id;

-- query to figure out who should get a bye
CREATE VIEW player_for_bye 
       AS SELECT *
	  FROM win_count, (SELECT min(bye) AS least_bye FROM win_count) AS subq
	  WHERE bye=least_bye
	  LIMIT 1;

CREATE VIEW players_not_for_bye
       AS (SELECT * FROM win_count) EXCEPT 
       (SELECT id, name, bye, wins FROM player_for_bye);
