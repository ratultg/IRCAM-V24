# Documentation Appendix

This appendix provides information on the methods and classes available for managing and analyzing temperature zones.

| Method/Class            | Type     | Description                                                                 |
|-------------------------|----------|-----------------------------------------------------------------------------|
| add_zone                | Method   | Adds a new zone (rectangle) to watch. Now supports naming and color-coding each zone (fields: name, color). |
| remove_zone             | Method   | Removes a zone from the list.                                             |
| get_zones               | Method   | Returns all currently defined zones, including their names and colors (fields: name, color).    |
| compute_zone_average    | Method   | Calculates the average temperature in a zone for a given snapshot.        |
| Zone                    | Class    | Represents a single rectangular area on the image, with a name and color. |

**Note:**
- The API and database now support `name` and `color` fields for each zone. These are available in all zone-related requests and responses.