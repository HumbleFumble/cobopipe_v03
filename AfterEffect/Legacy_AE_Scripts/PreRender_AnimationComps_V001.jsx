#target.aftereffects
function RQClear(){
    // clear renderQueue
    while(app.project.renderQueue.numItems >= 1) {
        app.project.renderQueue.item(1).remove();
    }   
}

function createPrerenders(){
    //This script was made for pre-rendering animation precomps in AE, to avoid having to do compositing with all the rigging and keys in the same file.
    //Pick the layers in the
    try{
        RQClear();
        var rendermax = 70;
        var rendercount = 0;
        var output_folder = app.project.file;
        $.writeln(output_folder.path);
        if(output_folder.path.search("%20folder")>-1){
            output_folder = output_folder.parent
            $.writeln(output_folder)
            }
        var output_folder = output_folder.path + "/Passes/";
        $.writeln(output_folder);
        output_folder_check = new Folder(output_folder);
        if (!output_folder_check.exists){
            output_folder_check.create();
            }
        
        var module_name = "PNG_Render";
        var cur_comp = app.project.activeItem;
        var cur_layers = null;
        if(cur_comp!=null){
            layersRef = cur_comp.selectedLayers;
            }
        if(layersRef){
            $.writeln("found layers: " + toString(layersRef));
            for (var i = 0;i < layersRef.length ;i++){
                    if(layersRef[i].inPoint>cur_comp.duration||layersRef[i].outPoint<0){
                        }else{
                            cur_layer = layersRef[i]
                            $.writeln(cur_layer.source);  
                            if (cur_layer.source instanceof CompItem){
                                comp_item = cur_layer.source;
                                var cur_name = comp_item.name;
                                cur_name = cur_name.replace(/ /g,"_");
                                
                                $.writeln(output_folder + cur_name);
                                
                                var renderItem = app.project.renderQueue.items.add(comp_item);
                                renderItem.timeSpanStart = 1;
                                renderItem.timeSpanDuration = comp_item.duration;
                                var outputMO = renderItem.outputModules[1];
                                outputMO.applyTemplate(module_name);
                                var render_path  = new File(output_folder + cur_name + '_[####].png');
                                outputMO.file = render_path;
                            }
                        }
                    
                    app.project.renderQueue.render();
                    $.writeln("finished rendering");
                    
                    import_options = new ImportOptions(new File(output_folder + cur_name + "_0001.png"));
                    import_options.sequence = true;
                    prerender_item = app.project.importFile(import_options);
                    prerender_item.mainSource.conformFrameRate = 25.00;
                    cur_layer.replaceSource(prerender_item,false);
                    //prerender_item

                    
            }
        }

    } catch(e){
        alert(e.line+":"+e.message);
    }
    //compRef.openInViewer() //Opens back up the old comp flow
//app.project.renderQueue.queueInAME(false); //Submit til media encoder queue items. Uses the last used preset/format by encoder.
}

function FindFootageFolder(){
    var project_content = app.project.items;
    var my_folder = "";
    var old_folder_list = [];
    var old_folder = "";
    for(var p =project_content.length;p>=1;p--){
        var cur_content = project_content[p];
        if(cur_content instanceof FolderItem){
            var _name = cur_content.name;
            if(_name == "PreRenders"){
                my_folder = cur_content;  
            }
        }
    }
    if(my_folder == ""){
        my_folder = project_content.addFolder("PreRenders");
        }

    return my_folder
}

function createPrerenders_in_comp(){
    //This script was made for pre-rendering animation precomps in AE, to avoid having to do compositing with all the rigging and keys in the same file.
    //Pick the layers in the
    try{
        RQClear();
        var rendermax = 70;
        var rendercount = 0;
        var output_folder = app.project.file;
        $.writeln(output_folder.path);
        if(output_folder.path.search("%20folder")>-1){
            output_folder = output_folder.parent
            }
        var output_folder = output_folder.path + "/Passes/";
        output_folder_check = new Folder(output_folder);
        if (!output_folder_check.exists){
            output_folder_check.create();
            }
        
        var module_name ="TIF_Render";//"DPX_Render"; //"TIF_Render"//"PNG_Render";
        var ext = "tif";//"dpx";//"png";
        var cur_comp = app.project.activeItem;
        var cur_layers = null;
        if(cur_comp!=null){
            layersRef = cur_comp.selectedLayers;
            }
        var my_folder = FindFootageFolder();
        if(layersRef){
            for (var i = 0;i < layersRef.length ;i++){
                    if(layersRef[i].inPoint>cur_comp.duration||layersRef[i].outPoint<0){
                        }else{
                            cur_layer = layersRef[i]
                            if (cur_layer.source instanceof CompItem){
                                comp_item = cur_layer.source;
                                var cur_name = comp_item.name;
                                cur_name = cur_name.replace(/ /g,"_");
                                var enable_state = turnOffandGetState(cur_comp,layersRef[i]);
                                var renderItem = app.project.renderQueue.items.add(cur_comp);
                                renderItem.timeSpanStart = cur_comp.displayStartFrame;
                                renderItem.timeSpanDuration = cur_comp.duration;
                                var outputMO = renderItem.outputModules[1];
                                outputMO.applyTemplate(module_name);
                                var render_path  = new File(output_folder + cur_name + '_[####].' + ext);
                                outputMO.file = render_path;
                               
                                 app.project.renderQueue.render();
                                $.writeln("finished rendering");
                                
                                import_options = new ImportOptions(new File(output_folder + cur_name + "_0001." + ext));
                                import_options.sequence = true;
                                prerender_item = app.project.importFile(import_options);
                                prerender_item.mainSource.conformFrameRate = 25.00;
                                prerender_item.parentFolder = my_folder;
                                turnBackOn(cur_comp,enable_state);
                            }
                        }
                    }
                }

    } catch(e){
        alert(e.line+":"+e.message);
    }
    //compRef.openInViewer() //Opens back up the old comp flow
//app.project.renderQueue.queueInAME(false); //Submit til media encoder queue items. Uses the last used preset/format by encoder.
}

function turnBackOn(cur_comp,enable_obj){
    for(var y=1;y<=cur_comp.numLayers; y++){
        var fix_layer = cur_comp.layer(y);
        $.writeln(fix_layer.name + " setting to " + enable_obj[fix_layer]);
        fix_layer.enabled = enable_obj[fix_layer.name];
        }
    }

function turnOffandGetState(cur_comp,selected_layer){
    var enable_obj = {}
    for(var i=1;i<=cur_comp.numLayers; i++){
        var cur_layer = cur_comp.layer(i);
        $.writeln(cur_layer.name + " is " + cur_layer.enabled);
        enable_obj[cur_layer.name] = cur_layer.enabled;
        if (cur_layer == selected_layer){
            cur_layer.enabled = true;
            }else{
                cur_layer.enabled = false;
                }
        }
    return enable_obj;
    }
"p:/930496_KenderDuHende/Production_Lis/Film/E01/E01_SQ020/E01_SQ020_SH021/Passes/"
"""
var cur_comp = app.project.activeItem;
    var cur_layers = null;
    if(cur_comp!=null){
        layersRef = cur_comp.selectedLayers;
        }
    if(layersRef){
        $.writeln("found layers: " + toString(layersRef));
        for (var i = 0;i < layersRef.length ;i++){
                if(layersRef[i].inPoint>cur_comp.duration||layersRef[i].outPoint<0){
                    }else{
                        var offset = layersRef[i].startTime *25;
                        $.writeln(offset);                        
                        cur_layer = layersRef[i]
                        $.writeln(cur_layer.source);  
                        if (cur_layer.source instanceof CompItem){
                            comp_item = cur_layer.source;
                            var cur_name = comp_item.name;
                            $.writeln(cur_name);
                            }
                        }
                    }
                }
"""
//createPrerenders()
createPrerenders_in_comp()

