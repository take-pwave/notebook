d3.json("js/world.geojson", createMap);

var width = 350;
var height = 350;
var aProjection = d3.geo.mollweide()
    .scale(120)
    .rotate([-136, 0])
    .center([0, 38])
    .translate([width / 2, height / 2]);

function createMap(countries) {
    var geoPath = d3.geo.path().projection(aProjection);
    var featureSize = d3.extent(countries.features,
                   function(d) {return geoPath.area(d);});        
    var countryColor = d3.scale.quantize()
                    .domain(featureSize).range(colorbrewer.Reds[7]);
    
    d3.select('#ex2').select("svg").selectAll("path").data(countries.features)
        .enter()
        .append("path")
        .attr("d", geoPath)
        .attr("class", "countries")
        .style("fill", function(d) {
                        return countryColor(geoPath.area(d))
        });
}

d3.csv("data/cities.csv",function(error,data) {createCities(data)});

function createCities(cities) {
    d3.select('#ex2').select("svg").selectAll("circle").data(cities)
        .enter()
        .append("circle")
        .attr("class", "cities")
        .attr("r", 3)
        .attr("cx",  function(d) { return aProjection([d.y, d.x])[0]})
        .attr("cy",  function(d) { return aProjection([d.y, d.x])[1]});
    
}