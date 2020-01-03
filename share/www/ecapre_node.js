#!/usr/bin/env node

/*
# Copyright (c) 2019 Rafael Sánchez
# This file is part of 'ecapre', a PC based preampiflier.
#
# 'ecapre' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'ecapre' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'ecapre'.  If not, see <https://www.gnu.org/licenses/>.
*/

// HARD WIRED GLOBALS:
const INDEX_HTML_PATH       = __dirname + '/index.html';
const NODEJS_PORT = 8080;

const ECAPRE_ADDR = 'localhost';
const ECAPRE_PORT = 9999;

const AUX_ADDR = 'localhost';
const AUX_PORT = 9998;

// importing modules (require) that we want to use
const http  = require('http');
const url   = require('url');
const fs    = require('fs');
const net   = require('net');

// Here we keep the answers from the ecapre TCP server
// when issuing any command to him.
var ecapre_ans = null;

// helper to debug received command_phrases
var last_cmd_phrase = '';

function ecapre_socket( cmd_phrase, host, port ){

    const client = net.createConnection({ port:port,
                                          host:host },() => {
        //console.log('--- connected to server :-)');
    });

    client.on('error', function(err){
        console.log(err.message);
    });

    client.write( cmd_phrase + '\r\n' );
    //console.log( '|---> : ', cmd_phrase );

    // a 'received data (aka data)' event handler for the client socket;
    client.on('data', (data) => {
        ecapre_ans = data.toString();
        //console.log( '--->| : ', ecapre_ans );
    });

    // finishing the socket connection
    client.end();

    // an informative 'end' event handler for the client socket;
    client.on('end', () => {
      //console.log('--- disconnected from server');
    });

    return ecapre_ans;
}


http.createServer(function(req, res) {

    // Debug the received requests to this server
    //console.log('--- node.js received a request: ' + req.url);

    // Render our HTML code index.html as an html:// response
    // when a browser client connects here
    if (req.url === '/' || req.url === '/index.html') {
        console.log( 'sending text/html to the client side' );
        res.writeHeader(200,  { "Content-Type": "text/html" } );
        fs.readFile(INDEX_HTML_PATH, 'utf8', (err,data) => {
            if (err) throw err;
            res.write(data);
            res.end();
        });
    }

    // Needed to serve the client side JAVASCRIPT source file that is required
    // from the index.html's head section:
    // <head>
    //      <script src="clientside.js"></script>
    //      ... ... ...
    // </head>
    else if (req.url === '/clientside.js') {
        console.log( 'sending application/javascript to the client side' );
        res.writeHead(200,{'content-Type': 'application/javascript'});
        var jsReadStream = fs.createReadStream(__dirname + '/clientside.js','utf8');
        jsReadStream.pipe(res);
    }

    // Here we try to PROCESS A CLIENT QUERY by reading the key 'command'
    // previously parsed from the query part of the raw url, for instance:
    //      http://localhost:8080/?command=level%203%20add
    // the raw url is:   '/?command=level%203%20add'
    // after parsing it, we can use the key 'command' through by 'q.command',
    // then we can pass the wanted command 'level 3 add' to the ecapre socket
    else {
        var q = url.parse(req.url, true).query;
        var cmd_phrase = q.command;

        if ( cmd_phrase ){

            // monitoring received commands, but no repeating :-)
            if (last_cmd_phrase !== cmd_phrase){
                console.log('received command=' + cmd_phrase);
                last_cmd_phrase = cmd_phrase;
            }

            // pass the command phrase to the related socket:

            // If prefix 'aux', remove prefix and send to the AUX server
            if ( cmd_phrase.split(' ')[0] == 'aux' ){
                var tmp = cmd_phrase.split(' ').slice(1)
                                                .toString()
                                                  .replace(',',' ');
                var ans = ecapre_socket( tmp, AUX_ADDR, AUX_PORT );
            }
            // else: a regular preamp command will be sent to the ECAPRE server
            else {
                var ans = ecapre_socket( cmd_phrase, ECAPRE_ADDR, ECAPRE_PORT );
            }
        }
        // And finally we pass the ecapre_control response to the http client side
        // while ending the http response.
        res.end(ans);
    }

}).listen( NODEJS_PORT );

console.log('Server running at http://localhost:' + NODEJS_PORT + '/');
