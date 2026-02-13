# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "boto3",
#     "datablob",
#     "requests",
#     "simple-env",
# ]
# ///
import boto3
import csv
import datablob
import json
import io
import zipfile
from collections import defaultdict
import requests
import simple_env as se

AWS_BUCKET_NAME = se.get("AWS_BUCKET_NAME")
AWS_BUCKET_PATH = se.get("AWS_BUCKET_PATH")

GTFS_URL = (
    "https://raw.githubusercontent.com/gocarta/gtfs/refs/heads/master/gtfs_current.zip"
)
DATASET_NAME = "simple_bus_routes"
DATASET_VERSION = "1"

shapes = defaultdict(list)
route_to_shapes = defaultdict(set)
results = []

response = requests.get(GTFS_URL)
zip_data = io.BytesIO(response.content)

with zipfile.ZipFile(zip_data) as z:
    with z.open("shapes.txt") as f:
        # decode('utf-8-sig') handles potential Byte Order Marks (BOM)
        reader = csv.DictReader(f.read().decode("utf-8-sig").splitlines())
        for row in reader:
            shapes[row["shape_id"]].append(
                {
                    "seq": int(row["shape_pt_sequence"]),
                    "lat": row["shape_pt_lat"],
                    "lon": row["shape_pt_lon"],
                }
            )

    with z.open(
        "routes.txt",
    ) as f:
        reader = csv.DictReader(f.read().decode("utf-8-sig").splitlines())
        route_info = dict([([row["route_id"], row]) for row in reader])

    with z.open("trips.txt") as f:
        reader = csv.DictReader(f.read().decode("utf-8-sig").splitlines())
        for row in reader:
            route_to_shapes[row["route_id"]].add(row["shape_id"])

# build WKT MultiLineString for each route
for route_id, shape_ids in route_to_shapes.items():
    line_strings = []

    for sid in shape_ids:
        if sid in shapes:
            # sort points by sequence to ensure the line is drawn correctly
            sorted_pts = sorted(shapes[sid], key=lambda x: x["seq"])
            # format: "lon lat, lon lat"
            wkt_pts = ", ".join([f"{p['lon']} {p['lat']}" for p in sorted_pts])
            line_strings.append(f"({wkt_pts})")

    if line_strings:
        # combine all shapes for this route into one MultiLineString
        wkt_geometry = f"MULTILINESTRING ({', '.join(line_strings)})"
        results.append(
            {
                "id": route_id,
                "name": route_info[route_id]["route_long_name"],
                "color": "#" + route_info[route_id]["route_color"],
                "geometry": wkt_geometry,
            }
        )

client = datablob.DataBlobClient(
    bucket_name=AWS_BUCKET_NAME, bucket_path=AWS_BUCKET_PATH
)

client.update_dataset(
    name=DATASET_NAME,
    version=DATASET_VERSION,
    data=results,
    description="Simple Bus Routes",
)

geojson = {"type": "FeatureCollection", "features": []}

for item in results:
    geometry = item["geometry"]

    inner = geometry.replace("MULTILINESTRING ", "").strip("()")
    lines = inner.split("), (")

    multi_coords = []
    for line in lines:
        # Convert "lon lat, lon lat" into [[lon, lat], [lon, lat]]
        pts = line.split(", ")
        coords = [[float(c) for c in pt.split(" ")] for pt in pts]
        multi_coords.append(coords)

    feature = {
        "type": "Feature",
        "properties": {
            "id": item["id"],
            "name": item["name"],
            "color": item["color"],
            "stroke": item["color"],
        },
        "geometry": {"type": "MultiLineString", "coordinates": multi_coords},
    }
    geojson["features"].append(feature)

# patching datablob client, remove once geojson lines supported
key = (
    client.bucket_path
    + "/"
    + DATASET_NAME
    + "/v"
    + DATASET_VERSION
    + "/data.lines.geojson"
)
boto3.client("s3").put_object(
    Bucket=client.bucket_name, Key=key, Body=json.dumps(geojson)
)

print(f"[dataops-simple-bus-routes] updated {len(results)} rows")
