--
-- OV-chipkaart stations
--

CREATE TABLE stations_data (
                company INT NOT NULL,			-- transport company number
                ovcid INT NOT NULL,			-- OV-chipkaart station number
                name VARCHAR(50),			-- name as used by transport company
		city VARCHAR(50),			-- city/municipality
		longname VARCHAR(120),			-- long name, should be fully clear
		haltenr INT,				-- dutch general halte nummer
                zone INT,				-- dutch public transport zone
                lon FLOAT,				-- longitude
                lat FLOAT,				-- lattitude
                PRIMARY KEY (company, ovcid)
        );

-- stations view with title based on available fields in stations_data
CREATE VIEW stations AS
	SELECT	*,
		(CASE company
			WHEN 4 THEN name
			ELSE COALESCE(longname, city||', '||name, name)
		END) AS title
	 FROM stations_data;

