#include 'json2.js'

function getPipePath(){
    var path = $.getenv("BOM_PIPE_PATH")
    if(!path){
        path = "C:/Users/cg/PycharmProjects/cobopipe-v02-001"
        }

    return path
}

function GetProject(){
	var project_name = $.getenv("BOM_PROJECT_NAME");
	if(project_name){
		log(project_name);
	}else{
		project_name = "Hoj"
	}
	return project_name
}

function loadConfigJson(){
    var project_name = GetProject()
    var pipe_path = getPipePath()//"C:/Users/cg/PycharmProjects/cobopipe-v02-001" //System.getenv("BOM_PIPE_PATH")
    var config_file = pipe_path + "/Configs/Config_" + project_name + ".json";
    var myFile = new File(config_file);
    myFile.open('r');
    var jsonFileContent = myFile.read();
    myFile.close();
    var project_config = JSON.parse(jsonFileContent);
    return project_config;
}

function log(msg){
$.writeln(msg)
}

function reg_replace(path){
    //log("replace" + path);
    var t = new RegExp('\<(.*?)\>','g')
    var m = path.match(t,path)
    if(!m){
        return []
        }
    return m
}

function clean_key_func(key){
     key = key.replace("<","")
     key = key.replace(">","")
    return key
    }

function dict_replace(dict,path){
    var no_keys = [];
    var key_list = reg_replace(path)
    for(i=0;i<key_list.length;i++){
         var c_key = key_list[i]
         var clean_key = clean_key_func(c_key)
         if(clean_key in dict){
             path = path.replace(c_key,dict[clean_key])
             }
         else{
             no_keys.push(c_key)
             }
         }
     var more_keys = reg_replace(path);
     if(more_keys.length!=no_keys.length){
         path = dict_replace(dict,path)
     }
     return path
    }

function getPreviewDict(cfgp,f_dict){
    var preview_obj = new Object()
    for(k in f_dict){
        preview_obj[k] = []
        for(var i=0; i<f_dict[k].length;i++){
            var tpath = dict_replace(cfgp,cfgp[f_dict[k][i]])
            preview_obj[k].push(tpath)
            }
        }
    return preview_obj
}

cfg = loadConfigJson()
cfgp = cfg.project_paths

f_dict = cfg.preview_dict
//log(f_dict.reflect.properties)

//var t = getPreviewDict(cfgp,f_dict)
var l = []
for(s in f_dict){
    l.push(s)
    //log(s)
    //log(t[s])
}
log(l)


var shot_dict = new Object()
shot_dict.episode_name = "S104"
shot_dict.seq_name = "SQ010"
shot_dict.shot_name = "SH050"


/*
log(cfgp["shot_path"])
my_path = dict_replace(cfgp,cfgp["shot_path"])
log(my_path)
*/