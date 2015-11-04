#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    DB_cursor.execute("TRUNCATE matches;")
    DB_connection.commit()
    DB_connection.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    DB_cursor.execute("TRUNCATE players CASCADE;")
    DB_connection.commit()
    DB_connection.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    DB_cursor.execute("SELECT COUNT(*) FROM players;")
    query_result = DB_cursor.fetchone()
    player_count = query_result[0]
    DB_connection.close()
    return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
    Args:
      name: the player's full name (need not be unique).
    """
    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    DB_cursor.execute(
        """INSERT INTO players (name) VALUES (%s);""", (name,))
    DB_connection.commit()
    DB_connection.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    DB_cursor.execute(
        """
        SELECT win_count.id, win_count.name, wins, number_of_matches
        FROM win_count LEFT JOIN match_count
        ON win_count.id=match_count.id
        ORDER BY wins DESC;
        """)
    query_results = DB_cursor.fetchall()
    player_list = []
    for item in query_results:
        player_list.append(item)
    DB_connection.close()
    return player_list


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    DB_cursor.execute(
        """INSERT INTO matches (winner, loser) VALUES (%s, %s);""",
        (winner, loser))
    DB_connection.commit()
    DB_connection.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    DB_connection = connect()
    DB_cursor = DB_connection.cursor()
    number_of_players = countPlayers()

    if(number_of_players % 2 == 0):
        DB_cursor.execute(
            """
            SELECT id, name
            FROM win_count ORDER BY wins DESC;
            """)
    else:
        # this path takes care of tournaments with odd number of players
        DB_cursor.execute(
            """
            SELECT id, name
            FROM player_for_bye;
            """)
        # this player gets a bye for this round
        odd_player = DB_cursor.fetchone()

        DB_cursor.execute(
            """
            SELECT id, name
            FROM players_not_for_bye ORDER BY wins DESC;
            """)

    more_results = True
    result_list = []

    while(more_results):
        query_results = DB_cursor.fetchmany(2)
        if len(query_results) == 2:
            result_list.append(query_results[0] + query_results[1])
        else:
            more_results = False
    if(number_of_players % 2 != 0):
        odd_id = odd_player[0]
        DB_cursor.execute(
            """
            UPDATE players SET bye=least_bye FROM
            (SELECT min(bye)+1 AS least_bye FROM win_count) AS subq WHERE id=%s
            """, (str(odd_id),))
        DB_connection.commit()

    DB_connection.close()
    return result_list
