// Prevent users from pressing F5
document.onkeydown = disableF5;   
function disableF5(e) { if ((e.keyCode) == 116) e.preventDefault(); };

function pageRedirect(){
    document.getElementById('send').click();
}

function delaySubmitButton(){
    setTimeout(function() {
        document.getElementById("send").disabled=false;
    }, 3000);
}

function record(){
    var recognition = new webkitSpeechRecognition();
    recognition.lang  = "en-US";

    recognition.start();

    recognition.onstart = function(){
    document.getElementById('id-mic').style.backgroundColor = '#F8C400';
    document.getElementById('id-mic').disabled = true;
    document.getElementById("repeater").disabled=true;
    document.getElementById("send").disabled=true;
    }

    recognition.onend = function(){
    document.getElementById('id-mic').style.backgroundColor = '#781B1B';
    document.getElementById('id-mic').disabled = false;
    document.getElementById("repeater").disabled=false;
    document.getElementById("send").disabled=false;
    }
    
    recognition.onresult = function(event){
    text = event.results[0][0].transcript;
    text_slice = text.slice(1)
    final_text = text.charAt(0).toUpperCase() + text_slice;
    
    document.getElementById('message').value += final_text + " ";
    }  
}

function checkSeconds(seconds) {
    if (seconds < 10) 
        return String(seconds).padStart(2, '0');
    else
        return seconds
    }

function startRepeater() { 
    document.getElementById("repeater").disabled=true; 
    document.getElementById("id-mic").disabled=true;
}

function endRepeater(){ 
    document.getElementById("repeater").disabled=false;
    document.getElementById("id-mic").disabled=false;
}