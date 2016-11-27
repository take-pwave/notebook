var width = 500, height = 500;
var takaokaBoundingBox = {geometry: {coordinates: [[[136.904778, 36.822525], [137.072662, 36.822525], [137.072662, 36.658552], [136.904778, 36.658552], [136.904778, 36.822525]]], type: "Polygon"}, id: 999999, properties:{}, type: "Feature"};

d3.select("#ex4").select("svg").append("g").attr("id", "tiles");
d3.select("#ex4").select("svg").append("g").attr("id", "vectors");

var tile = d3.geo.tile()
    .size([width, height]);

var projection = d3.geo.mercator()
    .scale((1 << 19) / 2 / Math.PI)
    .translate([width / 2, height / 2]);

var center = projection([137.025970, 36.754062]);

var path = d3.geo.path()
    .projection(projection);
var zoom = d3.behavior.zoom()
    .scale(projection.scale() * 2 * Math.PI)
    .translate([width - center[0], height - center[1]])
    .on("zoom", redraw);
d3.select("#ex4").select("svg").call(zoom);
projection
    .scale(1 / 2 / Math.PI)
    .translate([0, 0]);

var geoPath = d3.geo.path().projection(projection);

d3.json('data/A27-10_16-g_SchoolDistrict.json', function (schoolDistnct) {
    // console.log(schoolDistnct);

    var data = schoolDistnct.features.filter(function(d) { 
           return  d.properties.A27_006=="高岡市立"; 
        });

    d3.select("#ex4").select("#vectors").selectAll("path.countries").data(data)
        .enter()
        .append("path")
        .attr("d", geoPath)
        .attr("class", "countries")
        .style("fill", "red")
        .style("stroke-width", 3)
        .style("stroke", "black")
        .style("fill-opacity", .25)   
    
});        

redraw();

function redraw() {
   var tiles = tile
        .scale(zoom.scale())
        .translate(zoom.translate())();
    
    var image = d3.select("#ex4").select("#tiles")
        .attr("transform",
        "scale(" + tiles.scale + ") translate(" + tiles.translate + ")")
        .selectAll("image")
        .data(tiles, function(d) { return d; });
    
    image.exit()
       .remove();

    image.enter().append("image")
        .attr("xlink:href",
         function(d) { return "http://" 
             + ["a", "b", "c"][Math.random() * 3 | 0] 
             + ".tile.openstreetmap.org/" + d[2] + "/" + d[0] + "/" + d[1] 
             + ".png"; })        
        .attr("width", 1)
        .attr("height", 1)
        .attr("x", function(d) { return d[0]; })
        .attr("y", function(d) { return d[1]; });
    
        projection
            .scale(zoom.scale() / 2 / Math.PI)
            .translate(zoom.translate());

        d3.select("#ex4").selectAll("path")
            .attr("d", geoPath);
}