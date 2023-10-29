(function(lr) {
    var status_dialog = document.createElement('div');
    status_dialog.style.background='rgba(0, 0, 0, 0.5)';
    status_dialog.style.position='absolute';
    status_dialog.style.left='0px';
    status_dialog.style.top='0px';
    status_dialog.style.width='100%';
    status_dialog.style.height='100%';
    status_dialog.style.display='none';
    document.body.appendChild(status_dialog);
    var ready = true;

    function status(msg) {
        status_dialog.style.display='block';
        status_dialog.innerHTML="<div style='position:absolute;top:50%;color:white;width:100%'><h1 style='text-align:center'>"+msg+"</h1></div>"
    }

    function hide_status() {
        status_dialog.display='none';
    }

    var ws = new WebSocket(lr.url);
    ws.onopen = function() {
        ws.send("Register");
    };
    ws.onmessage = function (evt) {
        var msg = JSON.parse(evt.data);
        console.log(msg)
        switch(msg.command) {
            case 'status':
                console.log("status", msg.status)
                if (msg.status == 'starting') {
                    ready = false;
                    status("Server is starting...");
                } else if (msg.status == 'dead') {
                    ready = false;
                    status("Server died...");
                } else if (msg.status == 'ready') {
                    ready = true;
                    hide_status();
                    ws.send("Unregister");
                    ws.close();
                    window.location.reload(true);
                }
                break;
            case 'reload':
                if (ready) {
                    ws.send('Unregister');
                    ws.close()
                    console.log("Reloading due to change in ", msg.path);
                    window.location.reload(true);
                }
                break;
        }

    };
})(window.livereload)

