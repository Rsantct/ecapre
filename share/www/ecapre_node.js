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

const INDEX_HTML_PATH       = __dirname + '/index.html';
const NODEJS_LISTENING_PORT = 8080;

const ECAPRE_LISTENING_ADDR = 'localhost';
const ECAPRE_LISTENING_PORT = 9999;

function ecapre_socket( cmd_phrase ){

    const client = net.createConnection({ port:ECAPRE_LISTENING_PORT,
                                          host:ECAPRE_LISTENING_ADDR },() => {

        //console.log('--- connected to server port:9999 :-)');
    });

    client.on('error', function(err){
        console.log(err.message);
    });

    client.write( cmd_phrase + '\r\n' );
    //console.log( '---> 9999 : ', cmd_phrase );

    // a 'received data (aka data)' event handler for the client socket;
    client.on('data', (data) => {
        ecapre_ans = data.toString();
        //console.log( '9999 ---> : ', ecapre_ans );
    });

    // finishing the socket connection
    client.end();

    // an informative 'end' event handler for the client socket;
    client.on('end', () => {
      //console.log('--- disconnected from server port:9999');
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
    //      <script src="js/functions.js"></script>
    //      ... ... ...
    // </head>
    else if (req.url === '/js/functions.js') {
        console.log( 'sending application/javascript to the client side' );
        res.writeHead(200,{'content-Type': 'application/javascript'});
        var jsReadStream = fs.createReadStream(__dirname + '/js/functions.js','utf8');
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

            // monitoring received commands
            if (last_cmd_phrase !== cmd_phrase){
                console.log('received command=' + cmd_phrase);
                last_cmd_phrase = cmd_phrase;
            }
            // pass the command phrase to the ecapre_control socket
            var ecapre_ans = ecapre_socket( cmd_phrase );
        }
        // And finally we pass the ecapre_control response to the http client side
        // while ending the http response.
        res.end(ecapre_ans);
    }

}).listen( NODEJS_LISTENING_PORT );

console.log('Server running at http://localhost:' + NODEJS_LISTENING_PORT + '/');
