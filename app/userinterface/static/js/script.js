'use strict';
var id_points = [];
var time_points = [];
var lat_points = [];
var long_points = [];
var temp_points = [];
var humidity_points = [];
var rssi_points = [];

var m = -50,
    d = -122

var temp_total_range = [0, 50];
var temp_good_range = [37.5, 38.5];
var humidity_total_range = [0, 100];
var humidity_good_range = [45, 55];

var gauge1 = document.getElementById('tempGauge');
var gauge2 = document.getElementById('humidityGauge');
var gpsMap = document.getElementById('gps_map')

var thirty_days_time = new Date(Date.now() - 2592000000).toISOString().slice(0, -1);

var format_latest_date = (iso_date_string) => {
    var day = iso_date_string.substring(0, 19).replace('T', ' ');
    return day;
}

var parse_api_data = (data => {
    data.data_points.forEach(el => {
        id_points.push(el.id);
        time_points.push(el.time);
        lat_points.push(el.gps_lat);
        long_points.push(el.gps_long);
        temp_points.push(el.temp);
        humidity_points.push(el.humidity);
        rssi_points.push(el.rssi);
    });
});

function getPercent(v) {
    return (100 * (m - d) * (m - d) - (m - v) * (15 * (m - d) + 62 * (m - v))) / ((m - d) * (m - d))
}

function interpretResults(horse, temp_val, humidity_val) {
    if (temp_val >= temp_good_range[0] && temp_val <= temp_good_range[1] &&
        humidity_val >= humidity_good_range[0] && humidity_val <= humidity_good_range[1]) {
        return `${horse} is doing great! Temperature and humidity are within range.`
    } else if (!(temp_val >= temp_good_range[0] && temp_val <= temp_good_range[1]) &&
        humidity_val >= humidity_good_range[0] && humidity_val <= humidity_good_range[1]) {
        return `${horse} needs attention. Temperature is out of range.`
    } else if (temp_val >= temp_good_range[0] && temp_val <= temp_good_range[1] &&
        !(humidity_val >= humidity_good_range[0] && humidity_val <= humidity_good_range[1])) {
        return `${horse} needs attention. Humidity is out of range.`
    } else return `${horse} needs attention. Temperature and humidity are out of range.`
}

function create_gauge(div, chart_data, data_range, cold_range, good_range, hot_range, title) {
    var latest_val = chart_data[chart_data.length - 1];
    var config = { responsive: true }
    var data = [{
        domain: { x: [0, 1], y: [0, 1] },
        value: latest_val,
        title: { text: title },
        type: "indicator",
        mode: "gauge+number",
        gauge: {
            axis: {
                range: data_range,
                automargin: true
            },
            steps: [
                { range: cold_range, color: "lavender" },
                { range: good_range, color: "lightgreen" },
                { range: hot_range, color: "tomato" }
            ]
        }
    }];
    var layout = {
        autosize: true
    };
    Plotly.newPlot(div, data, layout, config);
};

function create_time_series(div, x_data, y_data, chart_title) {
    Plotly.newPlot(div, [{ x: x_data, y: y_data }], { title: chart_title })
}

var result = fetch(`datapoints?start_time=${'2021-01-01'}`)
    .then(response => response.json())
    .then(json_data => parse_api_data(json_data))
    .then(() => document.getElementById("last_time").innerHTML = `Latest (${(format_latest_date(time_points[time_points.length -1]))})`)
    .then(() => document.getElementById("signalStrength").innerHTML = `Signal Strength: ${Math.round(getPercent(rssi_points[rssi_points.length - 1]))}%`)
    .then(() => document.getElementById("statusMessage").innerHTML = interpretResults('Lucas', temp_points[temp_points.length - 1], humidity_points[humidity_points.length - 1]))
    .then(() => create_gauge(gauge1, temp_points, temp_total_range, [temp_total_range[0], temp_good_range[0]], [temp_good_range[0], temp_good_range[1]], [temp_good_range[1], temp_total_range[1]], 'Temperature (°C)'))
    .then(() => create_gauge(gauge2, humidity_points, humidity_total_range, [humidity_total_range[0], humidity_good_range[0]], [humidity_good_range[0], humidity_good_range[1]], [humidity_good_range[1], humidity_total_range[1]], 'Humidity (%)'))
    .then(() => gpsMap.src = `https://maps.google.com/maps?q=${lat_points[lat_points.length - 1]},${long_points[long_points.length - 1]}&z=16&output=embed`)
    .then(() => create_time_series(tempTimeSeries, time_points, temp_points, "Temperature"))
    .then(() => create_time_series(humidityTimeSeries, time_points, humidity_points, "Humidity"));