document.addEventListener("DOMContentLoaded", (event) => {
    var socket = io();

    let room = 'Public';
    joinRoom('Public');

    socket.on('message', function(data) {  
        var p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br');
        
        if(username === data.username)
            p.classList.add('messages','box-current-user', 'basic-drop-shadow');
        else
            p.classList.add('messages','box', 'basic-drop-shadow');

        if(data.username){
            span_username.innerHTML = data.username;
            span_timestamp.innerHTML = data.time_stamp;

            var msg = span_username.textContent + ": " +span_timestamp.textContent; 
            msg = msg.bold();
            data.msg = data.msg.replace(/((?:\S+\s+){5}\S+)/g, '$1<br />');
            p.innerHTML = msg + br.outerHTML + data.msg;
            
            var parent = document.querySelector('#display-message-section');
            parent.append(p);
            parent.scrollTop = parent.scrollHeight;
        }else{
            printSysMsg(data.msg);
        }
    });

    document.querySelector('#send_message').onclick = () => {
        socket.send({'username': username,
                    'msg': document.querySelector('#user_message').value,
                    'room': room
                });
        document.querySelector('#user_message').value = '';
    }

    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            let newRoom = p.innerHTML;
            if(newRoom == room){
                msg = `You are already in ${room}.`
                printSysMsg(msg);
            }else {
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        }
    });

    function leaveRoom(room){
        socket.emit('leave', {'username':username, 'room':room});
    }

    function joinRoom(room){
        socket.emit('join', {'username':username, 'room':room});

        document.querySelectorAll('.messages').forEach(p => {
            p.remove();
        });

        document.querySelector('#user_message').focus();
        document.querySelector('#room-header').innerHTML = room;
        document.title = room + " - Aditya Chat App";
    }

    function printSysMsg(msg){
        var p = document.createElement('p');
        p.classList.add('messages','box-joining', 'basic-drop-shadow');
        p.innerHTML = msg.bold();

        var parent = document.querySelector('#display-message-section');
        parent.append(p);
    }
});
