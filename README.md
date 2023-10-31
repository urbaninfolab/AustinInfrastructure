# Austin Fuel Stations

## Leaflet with .csv Files
Leaflet only natively supports loading .geojson files, despite that a lot of data files are stored in plain-text .csv format. A general workaround involves converting the data to json format. We decided to employ the [Omnivore Leaflet Plugin](https://github.com/mapbox/leaflet-omnivore) to simplify the process.
### API
|Factory|Description|
|-|-|
|<code>omnivore.csv(\<String\> *url*, \<JSON\> *parser_options?*, \<JSON\> *customLayer?*)</code>|Instantiates a GeoJSON object from the given url to a .csv file|
|<code>omnivore.csv.parse(\<String\> *csvString*, \<JSON\> *parser_options?*)</code>|Instantiates a GeoJSON object from the string read from a .csv file|
### Usage Example
```javascript
let customLayer = new L.geoJson(null, {
	filter: (feature, layer) => {
		return feature.properties[col1] == '...'
	}
	ponitToLayer: (feature, latlng) => {
		return new L.circleMarker(latlng, {
			radius: 10,
			fillColor: 'red',
			color: 'gray'
		}).bindPopup(`
			<div class="basic-info">
				<span>${feature.properties[col2]}</span><br>
				<span>${feature.properties[col3]}</span>
			</div>
		`)
	}
})
omnivore.csv('./data/.csv', null, customLayer)
```
Note that `parser_options` are sent to the parser library, rather than the layer, and are thus left as `null`. Custom layer options must be passed through `customLayer` as shown above.