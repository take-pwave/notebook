d3.json("js/world.geojson", createMap);

function createMap(countries) {
    var width = 350;
    var height = 350;
    var aProjection = d3.geo.mercator()
        .scale(80)
        .translate([width / 2, height / 2]);
    var geoPath = d3.geo.path().projection(aProjection);
    d3.select('#ex1').select("svg").selectAll("path").data(countries.features)
        .enter()
        .append("path")
        .attr("d", geoPath)
        .attr("class", "countries")
}