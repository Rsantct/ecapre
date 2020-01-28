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
const AUTO_UPDATE_INTERVAL = 1000;      // Auto-update interval millisec
var advanced_controls = false;          // Defaults hide advanced controls
var state = {};                         // The system status

// Talks to the ecapre node.js HTTP SERVER
function control_cmd( cmd ) {

    // avoids http socket lossing some symbols
    cmd = http_prepare(cmd);

    var myREQ = new XMLHttpRequest();

    // a handler that waits for HttpRequest has completed.
    myREQ.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            return;
        }
    };

    myREQ.open(method="GET", url="/?command="+cmd, async=false);
    myREQ.send();
    //console.log('TX: ' + cmd);

    ans = myREQ.responseText;
    //console.log('RX: ' + ans);

    return ans;
}

// Page INITIATE
function page_initiate(){
    // Geeting the current system status
    state = JSON.parse( control_cmd('get_state') );
    // Macros buttons (!) place this first because
    // aux server is supposed to be always alive
    fill_in_macro_buttons();
    // Initiate fixed page elements
    fill_in_page_statics();
    // Schedules the page_update (only runtime variable items):
    // Notice: the function call inside setInterval uses NO brackets)
    setInterval( page_update, AUTO_UPDATE_INTERVAL );
}

// Page STATIC ITEMS (HEADER and SELECTORS)
function fill_in_page_statics(){
    function fill_in_inputs_selector() {
        try{
            var inputs = JSON.parse( control_cmd( 'get_inputs' ) );
        }catch{
            return;
        }
        // Filling the options in a selector
        // https://www.w3schools.com/jsref/dom_obj_select.asp
        select_clear_options(ElementId="inputsSelector");
        const mySel = document.getElementById("inputsSelector");
        for ( i in inputs) {
            var option = document.createElement("option");
            option.text = inputs[i];
            mySel.add(option);
        }
        // And adds the input 'none' as expected in server_process that will disconnet all inputs
        var option = document.createElement("option");
        option.text = 'none';
        mySel.add(option);
    }
    function display_drc_info() {
        if ( state.drc_set && state.drc_set != 'none'){
            document.getElementById("drc").style.color = "white";
            document.getElementById("drc").innerHTML = "DRC: " + state.drc_set;
        }
        else {
            document.getElementById("drc").style.color = "grey";
            document.getElementById("drc").innerHTML = "(no drc)";
        }
    }
    // Fills in the web header
    document.getElementById("main_cside").innerText = ':: '+
                            JSON.parse(control_cmd('aux system_name')) +' :: ';
    // Fills in the INPUTS selector
    fill_in_inputs_selector();
    // Display DRC info
    display_drc_info();
}

// Queries the system status and updates the page (only runtime variable items):
function page_update() {

    // Amplifier switching:
    update_ampli_switch();

    // Querying the current status. Cancel updating if no answer
    try{
        state = JSON.parse( control_cmd('get_state') );
    }catch{
        document.getElementById("main_lside").innerText = ':: not connected :: ';
        document.getElementById("levelInfo").innerHTML  = '--';
        return;
    }

    // Updates level, balance, tone info
    document.getElementById("levelInfo").innerHTML  = state.level.toFixed(1);
    document.getElementById("balInfo").innerHTML    = 'BAL: '  + state.balance;
    document.getElementById("bassInfo").innerText   = 'BASS: ' + state.bass;
    document.getElementById("trebleInfo").innerText = 'TREB: ' + state.treble;

    // Updates loudness reference and loudness monitor
    document.getElementById("loud_slider_container").innerText =
                    'Loud. Ref: ' + state.loudness_ref;
    document.getElementById("loud_slider").value    =
                    parseInt(state.loudness_ref);

    // Updates current INPUT
    document.getElementById("inputsSelector").value = state.input;

    // Highlights activated buttons and related indicators accordingly
    buttonMuteHighlight()
    buttonMonoHighlight()
    buttonLoudHighlight()

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

//////// AUX SERVER FUNCTIONS ////////
// Switch the amplifier
function ampli(mode) {
    control_cmd( 'aux amp_switch ' + mode );
}
// Queries the remote amplifier switch state
function update_ampli_switch() {
    try{
        const amp_state = JSON.parse( control_cmd( 'aux amp_switch state' )
                                      .replace('\n','') );
        document.getElementById("onoffSelector").value = amp_state;
    }catch{
    document.getElementById("onoffSelector").value = '--';
    }
}
// Filling in the user's macro buttons
function fill_in_macro_buttons() {
    try{
        var macros = JSON.parse( control_cmd( 'aux get_macros' ).split(',') );
    }catch{
    // If no macros list, do nothing
        return
    }
    var macro = ''
    for (i in macros) {
        macro = macros[i];
        // Macro files are named this way: 'N_macro_name', so N will serve as button position
        macro_name = macro.slice(2, );
        macro_pos = macro.split('_')[0];
        document.getElementById( "macro_button_" + macro_pos ).innerText = macro_name;
    }
}
// Executes user defined macros
function user_macro(prefix, name) {
    control_cmd( 'aux run_macro ' + prefix + '_' + name );
}


///////////////  MISCEL INTERNAL ////////////
// Hightlight the MUTE, MONO and LOUDNESS BUTTONS:
function buttonMuteHighlight(){
    if ( state.muted == true ) {
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
}
function buttonMonoHighlight(){
    if ( state.midside == 'mid' ) {
        document.getElementById("buttonMono").style.background = "rgb(100, 0, 0)";
        document.getElementById("buttonMono").style.color = "rgb(255, 200, 200)";
        document.getElementById("buttonMono").innerText = 'MO';
    } else if ( state.midside == 'side' ) {
        document.getElementById("buttonMono").style.background = "rgb(100, 0, 0)";
        document.getElementById("buttonMono").style.color = "rgb(255, 200, 200)";
        document.getElementById("buttonMono").innerText = 'L-R';
    } else {
        document.getElementById("buttonMono").style.background = "rgb(0, 90, 0)";
        document.getElementById("buttonMono").style.color = "white";
        document.getElementById("buttonMono").innerText = 'ST';
    }
}
function buttonLoudHighlight(){
    if ( state.loudness_track == true ) {
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
}
// Send preamp changes and display new values w/o waiting for the autoupdate
function audio_change(param, value) {
    if ( param == 'level') {
        document.getElementById('levelInfo').innerHTML =
                                    (state[param] + value).toFixed(1);
    }else if( param == 'bass'){
        document.getElementById('bassInfo').innerHTML =
                         'BASS: ' + (state[param] + value).toFixed(0);
    }else if( param == 'treble'){
        document.getElementById('trebleInfo').innerHTML =
                         'TREB: ' + (state[param] + value).toFixed(0);
    }else if( param == 'balance'){
        document.getElementById('balInfo').innerHTML =
                         'BAL: ' + (state[param] + value).toFixed(0);
    }else{
        return;
    }
    control_cmd( param + ' ' + value + ' add' );
}
function mute_toggle() {
    state.muted = ! state.muted;
    buttonMuteHighlight();
    control_cmd( 'mute toggle' );
}
function loudness_toggle() {
    state.loudness_track = ! state.loudness_track;
    buttonLoudHighlight();
    control_cmd( 'loudness_track toggle' );
}
function mono_toggle() {
    if (state.midside == "mid" || state.midside == "side"){
        state.midside = "off";
    }else{
        state.midside = "mid";
    }
    buttonMonoHighlight();
    control_cmd( 'mono toggle' );
}
// Aux to clearing selector elements to avoid repeating
// when audio processes have changed
function select_clear_options(ElementId){
    // https://www.w3schools.com/jsref/dom_obj_select.asp
    const mySel = document.getElementById(ElementId);
    for (opt in mySel.options){
        mySel.remove(opt);
    }
}
// Toggle advanced controls
function advanced_toggle() {
    if ( advanced_controls !== true ) {
        advanced_controls = true;
    }
    else {
        advanced_controls = false;
    }
    page_update();
}
// Avoid http socket lossing some symbols
function http_prepare(x) {
    //x = x.replace(' ', '%20');  // leaving spaces as they are
    x = x.replace('!', '%21');
    x = x.replace('"', '%22');
    x = x.replace('#', '%23');
    x = x.replace('$', '%24');
    x = x.replace('%', '%25');
    x = x.replace('&', '%26');
    x = x.replace("'", '%27');
    x = x.replace('(', '%28');
    x = x.replace(')', '%29');
    x = x.replace('*', '%2A');
    x = x.replace('+', '%2B');
    x = x.replace(',', '%2C');
    x = x.replace('-', '%2D');
    x = x.replace('.', '%2E');
    x = x.replace('/', '%2F');
    return x;
}
// Test buttons
function TESTING1(){
    //do something
}
function TESTING2(){
    //do something
}
