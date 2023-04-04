var URL = 'http://127.0.0.1:8000'
/* Global Vars */
var mainState;
var activeHorse;
var horses = [];
var user_name;
var csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
var loginElements = document.querySelectorAll(".login-page")
var mainElements = document.querySelectorAll(".main-page")
var dataElements = document.querySelectorAll(".data-page")
var id_points = [];
var time_points = [];
var lat_points = [];
var long_points = [];
var temp_points = [];
var batt_points = [];
var hr_points = [];
var hr_int_points = [];
var data_points = [];


const buttonGroup = document.getElementById("button-group");
const backButton = document.getElementById("back-button");

/* Helper Functions */
var apiPostRequest = (endpoint, ...body) =>{
    // define headers object
    var headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.cookie.split('=')[1],
    };

    // set conditional headers
    if (mainState !== "loginState") {
        headers['Authorization'] = 'token ' + sessionStorage.getItem('token');
    }
    // make fetch request with headers object and return the promise
    return fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify( ...body )
    })
    .then(el => el.json());
}

var apiPatchRequest = (endpoint, ...body) =>{
    // define headers object
    var headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.cookie.split('=')[1],
        'Authorization': 'token ' + sessionStorage.getItem('token')
    };

    // make fetch request with headers object and return the promise
    return fetch(endpoint, {
        method: 'PATCH',
        headers: headers,
        body: JSON.stringify( ...body )
    })
    .then(el => el.json());
}

var apiGetRequest = (endpoint) =>{
    // define headers object
    var headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.cookie.split('=')[1],
        'Authorization': 'token ' + sessionStorage.getItem('token')
    };

    // make fetch request with headers object and return the promise
    return fetch(endpoint, {
        method: 'GET',
        headers: headers,
    })
    .then(el => el.json());
}

var getUsername = () =>{
    return apiGetRequest('/api/user/me/')
            .then(res => {
                sessionStorage.setItem('user_name', res.name);
            })
}

var getHorses = () => {
    horses = [];
    sessionStorage.removeItem('horses');
    return apiGetRequest('/api/horse/horses/')
    .then(res => res.forEach(el =>{
        horses.push(el);
    }))
    .then(res => sessionStorage.setItem('horses', JSON.stringify(horses)));
}

/* Main States
 * States: loginState, mainState, dataState
 * Horse states: api_key, undefined
*/



const refreshView = () =>{
    if(mainState == "loginState"){
        loginElements.forEach(el => el.style.display='block');
        mainElements.forEach(el => el.style.display='none');
        dataElements.forEach(el => el.style.display='none');
    }
    else if(mainState == "dataState"){
        loginElements.forEach(el => el.style.display='none');
        mainElements.forEach(el => el.style.display='none');
        dataElements.forEach(el => el.style.display='block');
        renderDataPage()  
    }
    else {
        loginElements.forEach(el => el.style.display='none');
        mainElements.forEach(el => el.style.display='block');
        dataElements.forEach(el => el.style.display='none');
        renderMainPage()
    } 
}

const refreshMainState = () =>{
    if (sessionStorage.getItem('token') == null){
        mainState = "loginState";
    }
    else if (sessionStorage.getItem('activeHorse') == null){
        getHorses()
        .then(mainState = "mainState")
        .then(refreshView);
    } else {
        mainState = "dataState";
    }
    refreshView();
    return mainState;
}


/* Event Listeners */

const activateHorse = e => { 
    const isButton = e.target.nodeName === 'BUTTON' 
    const isHorseSelector = e.target.id.split("-")[0]=="horse";
    const isEdit = e.target.id.split("-")[0]=="edit"
    if(isButton && isHorseSelector) {
        activeHorse = e.target.id.split("-")[2]
        sessionStorage.setItem('activeHorse', activeHorse);
        refreshMainState();
        refreshView();
    }
    else if(isButton && isEdit){
        var api_key = e.target.id.split("-")[1]
        var horse_id = horses.filter(el => el.api_key == api_key)[0].id
        if (e.target.innerHTML == 'Edit'){
            e.target.innerHTML = 'Submit'
            document.getElementById(`horse-id-${api_key}`).style.display="none"
            document.getElementById(`rename-${api_key}`).style.display="block"
        } else {
            new_name = document.getElementById(`${api_key}-new`).value
            apiPatchRequest(`/api/horse/horses/${horse_id}/`, {name: new_name})
            .then(() =>{
                e.target.innerHTML = 'Edit'
                document.getElementById(`horse-id-${api_key}`).style.display="block"
                document.getElementById(`horse-id-${api_key}`).innerHTML = new_name;
                horses.filter(el => el.id == horse_id)[0].name = new_name;
                sessionStorage.setItem('horses', JSON.stringify(horses))
                document.getElementById(`rename-${api_key}`).style.display="none"
            })
            .then(refreshMainState())
            .then(refreshView())
            .then(renderMainPage())
        }       
    }
    return
}

const deactivateHorse = () => {
    sessionStorage.removeItem('activeHorse')
    refreshMainState();
    refreshView();
}
const renderMainPage = () =>{
    var html_string = `<div>`
    document.getElementById("welcome").innerHTML=`Welcome ${sessionStorage.getItem('user_name')}`
    horses.forEach(el => {
        html_string +=  `<div style="display:flex; flex-direction:row; margin:5px 10px;">`
        html_string += `<button class="select-horse" id="horse-id-${el.api_key}" style="flex: 0 0 80%;">${el.name}</button>`
        html_string += `<div class="rename-horse" name="${el.name}" id="rename-${el.api_key}" style="flex: 0 0 80%; width: 100%; height: 100%; display:none;"><form><input type="text" id="${el.api_key}-new" value="${el.name}"/></form></div>`
        html_string +=`<button class="select-horse" id="edit-${el.api_key}" style="flex: 0 0 20%">Edit</button>`
        html_string +=`</div>`
    })
    html_string += `</div>`
    buttonGroup.innerHTML = html_string;
}

const renderDataPage = () =>{
    var horses = JSON.parse(sessionStorage.getItem('horses'))
    activeHorse = sessionStorage.getItem('activeHorse')
    var horse = horses.filter(el => el.api_key == activeHorse)[0]
    document.getElementById("data-header").innerHTML = `<h2>Data for ${horse.name}</h2>`
    var datapoints = apiGetRequest(`/api/horse/datapoints/?horse__api_key=${activeHorse}`)
                    .then(json_data => {
                        parse_api_data(json_data);
                        return json_data;
                    })
                    .then(() => document.getElementById("last_time").innerHTML = `Latest (${(format_latest_date(time_points[0]))})`)
                    .then(() => document.getElementById("batt").innerHTML = `Battery: ${Math.round(batt_points[0])}%`)
                    .then(() => document.getElementById("statusMessage").innerHTML = interpretResults(`${horse.name}`, temp_points[0], hr_points[0]))
                    .then(() => create_gauge(gauge1, temp_points, temp_total_range, [temp_total_range[0], temp_good_range[0]], [temp_good_range[0], temp_good_range[1]], [temp_good_range[1], temp_total_range[1]], 'Temperature (°C)'))
                    .then(() => create_gauge(gauge2, hr_points, hr_total_range, [hr_total_range[0], hr_good_range[0]], [hr_good_range[0], hr_good_range[1]], [hr_good_range[1], hr_total_range[1]], 'Heart Rate (BPM)'))
                    .then(() => gpsMap.src = `https://maps.google.com/maps?q=${lat_points[0]},${long_points[0]}&z=16&output=embed`)
                    .then(() => create_time_series(tempTimeSeries, time_points, temp_points, "Temperature"))
                    .then(() => create_time_series(hrTimeSeries, time_points, hr_points, "Heart Rate"));
}
buttonGroup.addEventListener("click", activateHorse);
backButton.addEventListener("click", deactivateHorse);

const loginButton = document.getElementById("login-form");
loginButton.onsubmit = (e) => {
    e.preventDefault()
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    let result = apiPostRequest('/api/user/token/',
            {email: email, password: password})
            .then((el) => sessionStorage.setItem('token', el.token.toString()))
            .then((el) => getUsername())
            .then((el) => renderMainPage(sessionStorage.getItem('user_name')))
            .then((el) => refreshMainState())
            .then((el) => refreshView())
            .then((el) => {return false})
};


// 'use strict';
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
var temp_good_range = [36.5, 39.5];
var hr_total_range = [0, 100];
var hr_good_range = [20, 40];

var gauge1 = document.getElementById('tempGauge');
var gauge2 = document.getElementById('hrGauge');
var gpsMap = document.getElementById('gps_map')

var thirty_days_time = new Date(Date.now() - 2592000000).toISOString().slice(0, -1);

var format_latest_date = (iso_date_string) => {
    var day = iso_date_string.substring(0, 19).replace('T', ' ');
    return day;
}

var parse_api_data = (data => {
    id_points = [];
    time_points = [];
    lat_points = [];
    long_points = [];
    temp_points = [];
    batt_points = [];
    hr_points = [];
    hr_int_points = [];
    data.forEach(el => {
        id_points.push(el.id);
        time_points.push(el.date_created);
        lat_points.push(el.gps_lat);
        long_points.push(el.gps_long);
        temp_points.push(el.temp);
        batt_points.push(el.batt);
        hr_points.push(el.hr);
        hr_int_points.push(el.hr_interval);
    });
});

function getPercent(v) {
    return (100 * (m - d) * (m - d) - (m - v) * (15 * (m - d) + 62 * (m - v))) / ((m - d) * (m - d))
}

function interpretResults(horse, temp_val, hr_val) {
    if (temp_val >= temp_good_range[0] && temp_val <= temp_good_range[1] &&
        hr_val >= hr_good_range[0] && hr_val <= hr_good_range[1]) {
        return `${horse} is doing great! Temperature and heart rate are within range.`
    } else if (!(temp_val >= temp_good_range[0] && temp_val <= temp_good_range[1]) &&
        hr_val >= hr_good_range[0] && hr_val <= hr_good_range[1]) {
        return `${horse} needs attention. Temperature is out of range.`
    } else if (temp_val >= temp_good_range[0] && temp_val <= temp_good_range[1] &&
        !(hr_val >= hr_good_range[0] && hr_val <= hr_good_range[1])) {
        return `${horse} needs attention. Heart rate is out of range.`
    } else return `${horse} needs attention. Temperature and heart rate are out of range.`
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


var logout = () => {
    sessionStorage.clear();
    refreshMainState();
}



