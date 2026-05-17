from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
import json


def serialize_geometry(location):
    if not location:
        return None

    if isinstance(location, str):
        return location

    if isinstance(location, WKBElement):
        geom = to_shape(location)

        if geom.geom_type == "Point":
            return json.dumps({
                "type": "Point",
                "coordinates": [geom.x, geom.y]
            })

        if geom.geom_type == "LineString":
            return json.dumps({
                "type": "LineString",
                "coordinates": list(geom.coords)
            })

        if geom.geom_type == "Polygon":
            return json.dumps({
                "type": "Polygon",
                "coordinates": [list(geom.exterior.coords)]
            })

    return location