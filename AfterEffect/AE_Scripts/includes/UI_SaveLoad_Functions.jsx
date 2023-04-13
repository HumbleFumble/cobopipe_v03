function my_UI_saveChild(uiObject,path,call_name){
    var return_list = [];
    for(var i = 0;i<uiObject.children.length;i++){
        var path = path+".children["+i+"]";
        if(uiObject.children[i].type.toLowerCase() == 'panel'||uiObject.children[i].type.toLowerCase() == 'group'||uiObject.children[i].type.toLowerCase() == 'tabbedpanel'||uiObject.children[i].type.toLowerCase() == 'tab'){
            var to_return = my_UI_saveChild(uiObject.children[i],path,call_name);
            return_list.push(to_return);
        } else if(uiObject.children[i].type.toLowerCase() == "dropdownlist"){
            if(uiObject.children[i].items.length >0){
            app.settings.saveSetting(call_name, path+".selection", uiObject.children[i].selection);
            }
        } else if(uiObject.children[i].type.toLowerCase() == "radiobutton"||uiObject.children[i].type.toLowerCase() == "checkbox"){
            app.settings.saveSetting(call_name, path+".value", uiObject.children[i].value);
            app.settings.saveSetting(call_name, path+".enabled", uiObject.children[i].enabled);
        }else if(uiObject.children[i].type.toLowerCase() == "edittext"||uiObject.children[i].type.toLowerCase() == "statictext"){
            //alert("Saving" + path+".text" + " AS: " + uiObject.children[i].text);
            app.settings.saveSetting(call_name, path+".text", uiObject.children[i].text);
            app.settings.saveSetting(call_name, path+".enabled", uiObject.children[i].enabled);
            //return_list.push(path + " " + uiObject.children[i].text + "\n");
            }
            """else{ //commented out because it doesn't add anything?
                return_list.push("NOT :" + path + " " + uiObject.children[i].type + "\n");
                }
                """
    }
    return return_list;
}

function my_UI_initChild(uiObject,path,call_name){
    var return_list = [];
    for(var i = 0;i<uiObject.children.length;i++){
        var path = path+".children["+i+"]";
        if(uiObject.children[i].type.toLowerCase() == 'panel'||uiObject.children[i].type.toLowerCase() == 'group'||uiObject.children[i].type.toLowerCase() == 'tabbedpanel'||uiObject.children[i].type.toLowerCase() == 'tab'){//if(uiObject.children[i].type == 'panel'||uiObject.children[i].type == 'group'){
            var to_return = my_UI_initChild(uiObject.children[i],path,call_name);
            return_list.push(to_return);
        } else if(uiObject.children[i].type.toLowerCase() == "dropdownlist"){
                if (app.settings.haveSetting(call_name, path+".selection")){
                    var selection = app.settings.getSetting(call_name, path+".selection");
                    var drop_down = uiObject.children[i];
                    for(var a=0;a< drop_down.items.length;a++){
                        if(drop_down.items[a].text == selection){
                            drop_down.items[a].selected = true;
                        }
                    }
                }
        } else if(uiObject.children[i].type.toLowerCase() == "radiobutton"||uiObject.children[i].type.toLowerCase() == "checkbox"){

            if (app.settings.haveSetting(call_name, path+".value")){
                uiObject.children[i].value = eval(app.settings.getSetting(call_name, path+".value"));

            }
            if (app.settings.haveSetting(call_name, path+".enabled")){
                uiObject.children[i].enabled = eval(app.settings.getSetting(call_name, path+".enabled"));
            }
        } else if(uiObject.children[i].type.toLowerCase() == "edittext"||uiObject.children[i].type.toLowerCase() == "statictext"){
            if (app.settings.haveSetting(call_name, path+".text")){
                uiObject.children[i].text = app.settings.getSetting(call_name, path+".text");
            }
            if (app.settings.haveSetting(call_name, path+".enabled")){
                uiObject.children[i].enabled = eval(app.settings.getSetting(call_name, path+".enabled"));
            }
            return_list.push(path + " " + uiObject.children[i].type + "\n");
            }
        """}else{
            return_list.push("NOT :" + path + " " + uiObject.children[i].type + "\n");
            }
            """
    }
}

function my_UI_save(winRef,current_call_name){
    var path = winRef.name;
        for(var i = 0;i<winRef.children.length;i++){
            var path = path+".children["+i+"]";
            my_UI_saveChild(winRef.children[i],path,current_call_name);
        }

}
function my_UI_init(winRef, current_call_name){
    var path = winRef.name;

        for(var i = 0;i<winRef.children.length;i++){
            var path = path+".children["+i+"]";
            my_UI_initChild(winRef.children[i],path,current_call_name);
        }

}