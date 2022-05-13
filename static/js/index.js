const socket = io();
var input = document.getElementById("input_link");
var result = document.getElementById("result");
var output_js = document.getElementById("output_js_lib");
var urlname = document.getElementById("urlname");
var output_section = document.getElementById("output-section");
var error = document.getElementById("error");

var pending = false;
var format = /^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$/;

function beautyname(des,name){
    var clean_name = name.toLowerCase().replaceAll(" js","")
    var clean_des = des.toLowerCase()

    for(let k=0;k<2;k++){
    if(clean_des.replaceAll(" ","").indexOf(clean_name) != -1){
            let count = 0;
            for(let i = 0;i<des.substring(clean_des.indexOf(clean_name),clean_name.length).length;i++){
                if (des[i] == " "){count+=1}
            }
            return des.substring(clean_des.indexOf(clean_name),clean_des.indexOf(clean_name) + clean_name.length)
        }
        
        else{clean_name = clean_name.split(".")[0]}
    }
    return name}


function send_link(){
    if (pending == false){
    inputval = input.value
    if (inputval.indexOf(".") != -1 && inputval.match(format)){
    error.innerHTML = ''
    socket.emit("send link", inputval);
    pending = true;
    output_js.replaceChildren();
    output_section.style.display = "none"
    }
    else{
        error.innerHTML = "[Erreur] Lien invalide (Charset)"
    }
}
    else{
        error.innerHTML = "[Erreur] Vous avez déjà une recherche en cours"}
    }

socket.on("receive data", (data)=>{
    pending = false;
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
        title.textContent = beautyname(data[i]["description"],data[i]["name"]);
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
        output_js.appendChild(document.createElement("hr"))

    }
    output_section.style.display = "";
    window.scrollTo(0,document.body.scrollHeight);
});

socket.on("error", (error)=>{
    error.innerHTML = "[Erreur] " + error;
    pending = false;
});


socket.on("loading", (load)=>{
    console.log(load);
});
