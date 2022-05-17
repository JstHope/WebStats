/// fichier de test pour les fonctions js
function beautyname(des,name){
    var clean_name = name.toLowerCase().replaceAll(" js","")
    var clean_des = des.toLowerCase();

    for (let k =0; k<2;k++){
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
        clean_name = name.split(".")[0]
    }
    return name;       
}

des = ["oTrafficJunky. Reach audiences across PC, mobile, and tablet","The Google APIs Explorer is is a tool that helps you explore various Google APIs interactively."]
name = ["trafficjunky.com","googleapis"]

console.log(beautyname(des[0],name[0]))
console.log(beautyname(des[1],name[1]))