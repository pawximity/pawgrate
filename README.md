
## Pawgrate

**Pawgrate** is a lightweight command-line utility for importing geospatial files into PostGIS using `ogr2ogr`. It simplifies the import process by prompting for parameters and generating the appropriate commands behind the scenes.
---

## Features

- Simple CLI interface for importing files  
- Supports overwrite or append mode  
- Prompts for Postgres password if needed  
- Promotes single-part geometries to multi (via `PROMOTE_TO_MULTI`)  
- Adds spatial index automatically  
- Displays formatted command output and result  

---

## Requirements

- Python 3.8+
- `ogr2ogr` (from the GDAL suite) installed and available on PATH
- PostGIS-enabled PostgreSQL database

Install Python dependencies:

```bash
pip install -r requirements.txt

