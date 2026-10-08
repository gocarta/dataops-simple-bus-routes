# dataops-simple-bus-routes
> Simple Dataset of Routes for all [CARTA](https://www.gocarta.org/) Buses and Shuttles

<img width="806" height="401" alt="image" src="https://github.com/user-attachments/assets/4e5cd35e-fd16-4ebb-8319-8b3d2f2efb10" />


## background
Data access is important to us at CARTA and we built this pipeline to make it easier to access data about the various routes of our buses and shuttles.  GTFS is great, but sometimes you just want a simple geojson to display on a web map.  This data pipeline basically pulls official [GTFS](https://gtfs.org/) data hosted by CARTA and then converts it into user-friendly formats.  We'll continue to add more formats, but let us know if you have one you'd like to see.

## frequency
The pipeline automatically runs once a day to make sure we are in sync, but the underlying data only changes every several months.

## columns
| column | example | description |
| :--- | :--- | :--- |
| **id** | `10G` | The unique identifier of the route. |
| **name** | `Glenwood` | The name of the route. |
| **color** | `#c0c0c0` | The route color assigned in the GTFS file, but it's not an official color. |
| **stroke** | `#c0c0c0` | This is the same as color.  We added it for compatability with geojson.io and other Web GIS |

## download links
- [metadata](https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/meta.json)
- [csv](https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/data.csv)
- [geojson (lines)](https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/data.lines.geojson)
- [geoparquet](https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/data.parquet)
- [json](https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/data.json)
- [json lines](https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/data.jsonl)

## preview links
- You can view the dataset on a map using [geojson.io](https://geojson.io/#data=data:text/x-url,https://gocarta.s3.us-east-2.amazonaws.com/public/data/simple_bus_routes/v1/data.lines.geojson).
- You can query the data with SQL using [duckdb](https://shell.duckdb.org/#queries=v0,CREATE-TABLE-dataset-AS-SELECT-*-FROM-'s3://gocarta/public/data/simple_bus_routes/v1/data.csv'~,Describe-dataset~).

## support
Post an issue [here](https://github.com/gocarta/dataops-simple-bus-routes/issues) or email the package author at DanielDufour@gocarta.org.
