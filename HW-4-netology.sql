CREATE TABLE Genres (
    id SERIAL PRIMARY KEY,       
    name VARCHAR(100) NOT NULL   
);

CREATE TABLE Artists (
    id SERIAL PRIMARY KEY,       
    name VARCHAR(100) NOT NULL   
);


CREATE TABLE ArtistGenres (
    artist_id INT REFERENCES Artists(id) ON DELETE CASCADE, 
    genre_id INT REFERENCES Genres(id) ON DELETE CASCADE,    
    PRIMARY KEY (artist_id, genre_id)                        
);


CREATE TABLE Albums (
    id SERIAL PRIMARY KEY,               
    title VARCHAR(100) NOT NULL,         
    release_year INT,                    
    UNIQUE (title, release_year)         
);


CREATE TABLE ArtistAlbums (
    artist_id INT REFERENCES Artists(id) ON DELETE CASCADE, 
    album_id INT REFERENCES Albums(id) ON DELETE CASCADE,    
    PRIMARY KEY (artist_id, album_id)                       
);


CREATE TABLE Tracks (
    id SERIAL PRIMARY KEY,               
    title VARCHAR(100) NOT NULL,         
    duration INTERVAL NOT NULL,          
    album_id INT REFERENCES Albums(id) ON DELETE CASCADE,  
    UNIQUE (title, album_id)             
);


CREATE TABLE Compilations (
    id SERIAL PRIMARY KEY,               
    title VARCHAR(100) NOT NULL,         
    release_year INT,                    
    UNIQUE (title, release_year)        
);


CREATE TABLE CompilationTracks (
    compilation_id INT REFERENCES Compilations(id) ON DELETE CASCADE,  
    track_id INT REFERENCES Tracks(id) ON DELETE CASCADE,              
    PRIMARY KEY (compilation_id, track_id)                             
);





-- Task 1
INSERT INTO Genres (name) VALUES
('Рок'),
('Поп'),
('Хип-хоп'),
('Джаз'),
('Электроника');


INSERT INTO Artists (name) VALUES
('The Beatles'),
('Queen'),
('Eminem'),
('Louis Armstrong'),
('Daft Punk'),
('Lady Gaga');

INSERT INTO Artists (name) VALUES
('Limp Bizkit');

INSERT INTO ArtistGenres (artist_id, genre_id) VALUES
(1, 1),  -- The Beatles - Рок
(1, 2),  -- The Beatles - Поп
(2, 1),  -- Queen - Рок
(3, 3),  -- Eminem - Хип-хоп
(4, 4),  -- Louis Armstrong - Джаз
(5, 5),  -- Daft Punk - Электроника
(6, 2),  -- Lady Gaga - Поп
(6, 5);  -- Lady Gaga - Электроника

INSERT INTO ArtistGenres (artist_id, genre_id) values
(7, 1);  -- Limp Bizkit - Рок

INSERT INTO Albums (title, release_year) VALUES
('Abbey Road', 1969),
('A Night at the Opera', 1975),
('The Marshall Mathers LP', 2000),
('What a Wonderful World', 1967),
('Random Access Memories', 2013),
('The Fame', 2008);

INSERT INTO Albums (title, release_year) values
('Chocolate Starfish', 2000);

INSERT INTO ArtistAlbums (artist_id, album_id) VALUES
(1, 1),  -- The Beatles - Abbey Road
(2, 2),  -- Queen - A Night at the Opera
(3, 3),  -- Eminem - The Marshall Mathers LP
(4, 4),  -- Louis Armstrong - What a Wonderful World
(5, 5),  -- Daft Punk - Random Access Memories
(6, 6);  -- Lady Gaga - The Fame

INSERT INTO ArtistAlbums (artist_id, album_id) VALUES
(7, 8);  -- Limp Bizkit - Chocolate Starfish

INSERT INTO Tracks (title, duration, album_id) VALUES
('Come Together', '00:04:20', 1),
('Something', '00:03:03', 1),
('Bohemian Rhapsody', '00:05:55', 2),
('Love of My Life', '00:03:39', 2),
('The Real Slim Shady', '00:04:44', 3),
('Stan', '00:06:44', 3),
('What a Wonderful World', '00:02:19', 4),
('Get Lucky', '00:06:09', 5),
('Instant Crush', '00:05:37', 5),
('Poker Face', '00:03:57', 6),
('Just Dance', '00:04:02', 6),
('Bad Romance', '00:04:54', 6);

INSERT INTO Tracks (title, duration, album_id) values
('My Generation', '00:03:41', 8);


INSERT INTO Compilations (title, release_year) VALUES
('Greatest Rock Hits', 2010),
('Best of 2000s', 2015),
('Jazz Classics', 2005),
('Electronic Dance Music', 2018),
('Pop Divas', 2019);

INSERT INTO CompilationTracks (compilation_id, track_id) VALUES
(1, 1),  -- Greatest Rock Hits - Come Together
(1, 3),  -- Greatest Rock Hits - Bohemian Rhapsody
(2, 5),  -- Best of 2000s - The Real Slim Shady
(2, 10), -- Best of 2000s - Poker Face
(3, 7),  -- Jazz Classics - What a Wonderful World
(4, 8),  -- Electronic Dance Music - Get Lucky
(4, 9),  -- Electronic Dance Music - Instant Crush
(5, 10), -- Pop Divas - Poker Face
(5, 11), -- Pop Divas - Just Dance
(5, 12); -- Pop Divas - Bad Romance


INSERT INTO CompilationTracks (compilation_id, track_id) values
(1, 14); -- Greatest Rock Hits - My Generation

INSERT INTO Albums (title, release_year) VALUES ('New Album 2020', 2020);

INSERT INTO ArtistAlbums (artist_id, album_id) 
VALUES ((SELECT id FROM Artists WHERE name = 'Queen'), 
        (SELECT id FROM Albums WHERE title = 'New Album 2020'));

INSERT INTO Compilations (title, release_year) VALUES ('Best Rock Hits 2023', 2023);
INSERT INTO CompilationTracks (compilation_id, track_id)
VALUES ((SELECT id FROM Compilations WHERE title = 'Best Rock Hits 2023'),
        (SELECT id FROM Tracks WHERE title = 'Bohemian Rhapsody'));

-- Task 2
SELECT title, duration from tracks 
where duration = (select MAX(duration) from tracks);

select title, duration from tracks
where duration >= '00:03:30';

select title, release_year from compilations
where release_year >= '2018' 
and release_year <= '2020';

SELECT id, name
FROM Artists
WHERE name NOT LIKE '% %' 
  AND name NOT LIKE '%-%'
  AND name NOT LIKE '%''%';

select title from tracks
where title ilike '%мой%'
or title ilike '%my%';


-- task 3
SELECT g.name AS genre, COUNT(ag.artist_id) AS artists_count
FROM Genres g
LEFT JOIN ArtistGenres ag ON g.id = ag.genre_id
GROUP BY g.name
ORDER BY artists_count DESC;

SELECT COUNT(t.id) AS tracks_count
FROM Tracks t
JOIN Albums a ON t.album_id = a.id
WHERE a.release_year BETWEEN 2019 AND 2020;

SELECT a.title AS album, 
       AVG(EXTRACT(EPOCH FROM t.duration)) AS avg_duration_seconds,
       AVG(EXTRACT(EPOCH FROM t.duration))/60 AS avg_duration_minutes
FROM Albums a
JOIN Tracks t ON a.id = t.album_id
GROUP BY a.title
ORDER BY avg_duration_seconds DESC;

SELECT ar.name AS artist
FROM Artists ar
WHERE ar.id NOT IN (
    SELECT aa.artist_id
    FROM ArtistAlbums aa
    JOIN Albums a ON aa.album_id = a.id
    WHERE a.release_year = 2020
);

SELECT DISTINCT c.title AS compilation
FROM Compilations c
JOIN CompilationTracks ct ON c.id = ct.compilation_id
JOIN Tracks t ON ct.track_id = t.id
JOIN Albums a ON t.album_id = a.id
JOIN ArtistAlbums aa ON a.id = aa.album_id
JOIN Artists ar ON aa.artist_id = ar.id
WHERE ar.name = 'Queen';

