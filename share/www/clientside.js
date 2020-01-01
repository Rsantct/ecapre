/*
    Copyright (c) 2019 Rafael Sánchez
    This file is part of 'ecapre', a PC based preamplifier.

    'ecapre' is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'ecapre' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 'ecapre'.  If not, see <https://www.gnu.org/licenses/>.
*/

/*
   debug trick: console.log(something);
   NOTICE: remember do not leaving any console.log actives
*/

/* TO REVIEW:
    At some http request we use async=false, this is not recommended
    but this way we get the answer.
    Maybe it is better to use onreadystatechange as per in refresh_system_status()
*/

/////////////   GLOBALS //////////////
var auto_update_interval = 1000;            // Auto-update interval millisec
var advanced_controls = false;              // Default for displaying advanced controls

// Talks to the ecapre TCP server
function control_cmd( cmd ) {

    // avoids http socket lossing some symbols
    cmd = http_prepare(cmd);

    // https://www.w3schools.com/js/js_ajax_http.asp
    var myREQ = new XMLHttpRequest();
    // waiting for HttpRequest has completed.
    myREQ.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            return;
        }
    };

    // the http request:
    myREQ.open(method="GET", url="/?command="+cmd, async=false);
    myREQ.send();
    ans = myREQ.responseText;
    // debug
    //console.log('ans', ans);
    return ans;
}

function page_initiate(){

    // Web header
    document.getElementById("main_lside").innerText = ':: ecapre ::';

    // Queries the system status and updates the page
    page_update();

    // Waits 1 sec, then schedules the auto-update itself:
    // Notice: the function call inside setInterval uses NO brackets)
    setTimeout( setInterval( page_update, auto_update_interval ), 1000);
}


// Dumps system status into the web page
function page_update() {

    var status = control_cmd('dummy');

    // Level, balance, tone info
    document.getElementById("levelInfo").innerHTML  =            status_decode(status, 'level');
    document.getElementById("balInfo").innerHTML    = 'BAL: '  + status_decode(status, 'balance');
    document.getElementById("bassInfo").innerText   = 'BASS: ' + status_decode(status, 'bass');
    document.getElementById("trebleInfo").innerText = 'TREB: ' + status_decode(status, 'treble');

    // the loudness reference to the slider and the loudness monitor to the meter
    document.getElementById("loud_slider_container").innerText =
                                                     'Loud. Ref: '
                                                      + status_decode(status, 'loudness_ref');
    document.getElementById("loud_slider").value    = parseInt(status_decode(status, 'loudness_ref'));
    //loud_measure = get_file('loudness_monitor').trim();
    //document.getElementById("loud_meter").value    =  loud_measure;

    // The selected item on INPUTS, XO, DRC and PEQ
    document.getElementById("targetSelector").value =            status_decode(status, 'target');
    document.getElementById("inputsSelector").value =            status_decode(status, 'input');
    document.getElementById("xoSelector").value     =            status_decode(status, 'xo_set');
    document.getElementById("drcSelector").value    =            status_decode(status, 'drc_set');

    // MONO, LOUDNESS buttons text lower case if deactivated ( not used but leaving this code here)
    //document.getElementById("buttonMono").innerHTML = UpLow( 'mono', status_decode(status, 'mono') );
    //document.getElementById("buttonLoud").innerHTML = UpLow( 'loud', status_decode(status, 'loudness_track') );

    // Highlights activated buttons and related indicators
    if ( status_decode(status, 'muted') == true ) {
        document.getElementById("buttonMute").style.background = "rgb(185, 185, 185)";
        document.getElementById("buttonMute").style.color = "white";
        document.getElementById("buttonMute").style.fontWeight = "bolder";
        document.getElementById("levelInfo").style.color = "rgb(150, 90, 90)";
    } else {
        document.getElementById("buttonMute").style.background = "rgb(100, 100, 100)";
        document.getElementById("buttonMute").style.color = "lightgray";
        document.getElementById("buttonMute").style.fontWeight = "normal";
        document.getElementById("levelInfo").style.color = "white";
    }
    if ( status_decode(status, 'mono') == true ) {
        document.getElementById("buttonMono").style.background = "rgb(100, 0, 0)";
        document.getElementById("buttonMono").style.color = "rgb(255, 200, 200)";
        document.getElementById("buttonMono").innerText = 'MO';
    } else {
        document.getElementById("buttonMono").style.background = "rgb(0, 90, 0)";
        document.getElementById("buttonMono").style.color = "white";
        document.getElementById("buttonMono").innerText = 'ST';
    }
    if ( status_decode(status, 'loudness_track') == true ) {
        document.getElementById("buttonLoud").style.background = "rgb(0, 90, 0)";
        document.getElementById("buttonLoud").style.color = "white";
        document.getElementById("buttonLoud").innerText = 'LD';
        document.getElementById( "loudness_metering_and_slider").style.display = "block";
    } else {
        document.getElementById("buttonLoud").style.background = "rgb(100, 100, 100)";
        document.getElementById("buttonLoud").style.color = "rgb(150, 150, 150)";
        document.getElementById("buttonLoud").innerText = 'LD';
        // Hides loudness_metering_and_slider if loudness_track=False
        document.getElementById( "loudness_metering_and_slider").style.display = "none";
    }

    // Header
    document.getElementById("main_lside").innerText = ':: ecapre ::';

    // Updates the amplifier switch
    //update_ampli_switch()

    // Updates metadata player info
    //update_player_info()

    // Highlights player controls when activated
    //update_player_controls()

    // Displays the [url] button if input == 'iradio' or 'istreams'
    //if (status_decode(status, 'input') == "iradio" ||
    //    status_decode(status, 'input') == "istreams") {
    //    document.getElementById( "url_button").style.display = "inline";
    //}
    //else {
    //    document.getElementById( "url_button").style.display = "none";
    //}

    // Displays the track selector if input == 'cd'
    //if (status_decode(status, 'input') == "cd") {
    //    document.getElementById( "track_selector").style.display = "inline";
    //}
    //else {
    //    document.getElementById( "track_selector").style.display = "none";
    //}


    // Displays or hides the advanced controls section
    if ( advanced_controls == true ) {
        document.getElementById( "advanced_controls").style.display = "block";
        document.getElementById( "level_buttons13").style.display = "table-cell";
    }
    else {
        document.getElementById( "advanced_controls").style.display = "none";
        document.getElementById( "level_buttons13").style.display = "none";
    }

}

//////// TOGGLES ADVANCED CONTROLS ////////
function advanced_toggle() {
    if ( advanced_controls !== true ) {
        advanced_controls = true;
    }
    else {
        advanced_controls = false;
    }
    page_update(status);
}

// Processing the LOUDNESS_REF slider
function loudness_ref_change(slider_value) {
    loudness_ref = parseInt(slider_value);
    control_cmd('loudness_ref ' + loudness_ref, update=false);
}

// Decodes the value from a system parameter inside the system status stream
function status_decode(state, prop) {
    state = JSON.parse(state);
    return state[prop];
}

// Auxiliary function to avoid http socket lossing some symbols
function http_prepare(x) {
    //x = x.replace(' ', '%20')  # leaving spaces as they are
    x = x.replace('!', '%21')
    x = x.replace('"', '%22')
    x = x.replace('#', '%23')
    x = x.replace('$', '%24')
    x = x.replace('%', '%25')
    x = x.replace('&', '%26')
    x = x.replace("'", '%27')
    x = x.replace('(', '%28')
    x = x.replace(')', '%29')
    x = x.replace('*', '%2A')
    x = x.replace('+', '%2B')
    x = x.replace(',', '%2C')
    x = x.replace('-', '%2D')
    x = x.replace('.', '%2E')
    x = x.replace('/', '%2F')
    return x;
}
