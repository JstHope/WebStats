function beautyname(des,name){
    var clean_name = name.toLowerCase().replaceAll(" js","")
    var clean_des = des.toLowerCase()
    var count = 0
    for(let k=0;k<2;k++){
    if(clean_des.replaceAll(" ","").indexOf(clean_name) != -1){
            let count = 0;
            for(let i = 0;i<des.substring(clean_des.indexOf(clean_name),clean_name.length).length;i++){
                if (des[i] == " "){start+=1}
            }
            return des.substring(clean_des.replaceAll(" ","").indexOf(clean_name) + count,clean_des.indexOf(clean_name) + clean_name.length)
        }
        
        else{clean_name = clean_name.split(".")[0]}
    }
    return name}

des = ["Promote your business online with TrafficJunky. Reach audiences across PC, mobile, and tablet","The Google APIs Explorer is is a tool that helps you explore various Google APIs interactively."]
name = ["trafficjunky.com","googleapis.com"]

console.log(beautyname(des[0],name[0]))
console.log(beautyname(des[1],name[1]))