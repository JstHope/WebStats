const socket = io();
var input = document.getElementById("input_link");
var result = document.getElementById("result");
var output_js = document.getElementById("output_js_lib");
var urlname = document.getElementById("urlname");

var pending = false
var format = /^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$/;

function send_link(){
    if (pending == false){
    inputval = input.value
    if (inputval.indexOf(".") != -1 && inputval.match(format)){
    socket.emit("send link", inputval);
    pending = true;
    }
    else{
    console.log("invalid link")
    }
}
    else{
    console.log("demande requete deja en cours...")}
    }

socket.on("receive data", (data)=>{
    console.log(data);
    urlname.textContent = data[0]["url"]
    for(let i = 1; i<data.length;i++){
        // cree un entry objet 
        var entry = document.createElement('div');
        entry.classList.add("output-category__entry");
        // 
        var firstline = document.createElement('div');
        firstline.classList.add("output-category__entry__firstline");
        entry.appendChild(firstline);
        //
        var title = document.createElement('h4');
        title.classList.add("output-category__entry__firstline__title");
        title.textContent = data[i]["name"];
        firstline.appendChild(title);
        //
        var logo = document.createElement('div');
        logo.classList.add("output-category__entry__firstline__logo");
        firstline.appendChild(logo);
        //
        var image = document.createElement('img');
        image.classList.add("output-category__entry__firstline__logo__image");
        image.alt = "Logo de la librairie"
        image.src = data[i]["logo"]
        logo.appendChild(image);
        //
        var desc = document.createElement('p');
        desc.classList.add("output-category__entry__infos");
        desc.textContent = data[i]["description"]
        entry.appendChild(desc);
        //////////////////////

        output_js.appendChild(entry)
    }
    pending = false;
});

socket.on("invalid link", ()=>{
    console.log("invalid link");
    pending = false;
});

socket.on("timeout", ()=>{
    console.log("timeout");
    pending = false;
});
