const socket = io();
var input = document.getElementById("input_link");
var result = document.getElementById("result");
var output_js = document.getElementById("output_js_lib");
var output_section = document.getElementById("output-section");
var error = document.getElementById("error");
var loading_bar = document.getElementsByClassName("modal-wrapper")[0];
var bar1 = new ldBar("#loadbar");

var domains_btn = document.getElementById("domaines");
var lib_btn = document.getElementById("librairies");
var wp_btn = document.getElementById("wp-plugins");

input.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        document.getElementById("button").click();
    }
});

var pending = false;
var format = /^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$/;

function beautyname(des,name){
    var clean_name = name.toLowerCase().replaceAll(" js","").replaceAll(" css","").replaceAll("-"," ")
    var clean_des = des.toLowerCase();

    count =0;
    start = 0;
    for(var i = 0; count<clean_name.length && i<des.length;i++){
        if (clean_des[i] == clean_name[count] && start ==0){
            count+=1;
            start = i-1;
        }else{
            if (clean_des[i] == clean_name[count]){
                count+=1;
            }
            else{      
               if(clean_des[i] == " "){if (start ==0){start = i+1}}
            else{
            count = 0;
            start = 0;}}}
        if (count == clean_name.length){return des.substring(start,i+1)}
        }
    
    return name.replace("Wordpress","").replaceAll("-"," ").replaceAll(" js","");       
}


function send_link(){
    if (pending == false){
    inputval = input.value
    if (inputval.indexOf(".") != -1 && inputval.match(format)){
    error.innerHTML = ''
    socket.emit("send link", inputval);
    pending = true;
    document.getElementsByClassName("searchbar")[0].style.display = "none"
    loading_bar.style.display = "" 
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


function show_domains(){
    for(let i=0;i<output_list.length;i++){
        if(i<parseInt(map[0]) + parseInt(map[1])){
            output_list[i].style.display = "";
        }
        else{
            output_list[i].style.display = "none";          
        }
    }
}
function show_lib(){
    for(let i=0;i<output_list.length;i++){
        if(i< output_list.length - parseInt(map[4]) && i >= parseInt(map[0]) + parseInt(map[1])){
            output_list[i].style.display = "";
        }
        else{
            output_list[i].style.display = "none";          
        }
    }
}
function show_wp(){
    for(let i=0;i<output_list.length;i++){
        if(i >= output_list.length - parseInt(map[4])){
            output_list[i].style.display = "";
        }
        else{
            output_list[i].style.display = "none";          
        }
    }
}

socket.on("receive data", (data)=>{
    pending = false;
    console.log(data);
    map = data[0]["map"].split(" ");
    console.log(map)
    if (data[0]["Server"]== 'cloudflare' && data[0]["map"] == "0 0 0 0 0"){error.innerHTML = "[Erreur] Ce site est protégé par Cloudflare et ne peut donc pas être scanné."}
    else{
        if(data[0]["map"] == "0 0 0 0 0"){error.innerHTML = "[Erreur] Aucune technologie trouvée sur ce site."}
    else{
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
        if (i>parseInt(map[0])+parseInt(map[1])){
        title.textContent = beautyname(data[i]["description"],data[i]["name"]);}
        else{
            title.textContent = beautyname(data[i]["description"],data[i]["name"].split(".")[0]);
        }
        var logo = document.createElement('div');
        logo.classList.add("output-category__entry__firstline__logo");


        firstline.appendChild(logo);
        //
        firstline.appendChild(title);
        //
        if(data[i]["version"]){
            var version = document.createElement('div');
            version.textContent = data[i]["version"];
            version.classList.add("output-category__entry__firstline__version");
            firstline.appendChild(version);
        }
        
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
    if(map[4]=='0'){wp_btn.style.display = "none"}else{wp_btn.style.display = ""}
    if(map[0]=='0' && map[1]=='0'){domains_btn.style.display = "none"}else{domains_btn.style.display = ""}
    if(map[2]=='0' && map[3]=='0'){lib_btn.style.display = "none"}else{lib_btn.style.display = ""}

    output_list = document.getElementsByClassName("output-category__entry");
    show_domains();
    document.querySelectorAll("html")[0].classList.remove("html-scroller");
    output_section.style.display = ""; 
    document.getElementsByClassName("searchbar")[0].style.display = ""
    loading_bar.style.display = "none"
    window.scrollTo(0,document.body.scrollHeight);}
}});

socket.on("error", (data)=>{
    error.innerHTML = "[Erreur] " + data;
    pending = false;
});




socket.on("loading", (percent)=>{
    bar1.set(parseInt(percent));
});
