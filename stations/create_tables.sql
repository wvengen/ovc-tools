--
-- OV-chipkaart stations
--

CREATE TABLE stations (
                company INT NOT NULL,			-- transport company number
                ovcid INT NOT NULL,			-- OV-chipkaart station number
                title VARCHAR(50),			-- title of station
		haltenr INT,				-- dutch general halte nummer
                zone INT,				-- dutch public transport zone
                lon FLOAT,				-- longitude
                lat FLOAT,				-- lattitude
                PRIMARY KEY (company, ovcid)
        );

