import subprocess
import os
import sys

from Log.CoboLoggers import getLogger
logger = getLogger()

def CreatePrecomp(base_file, passes_folder,comp_folder, precomp_name):
    precomp_script = "%sAutoCreatePrecomp.jsx" % passes_folder
    script_content = """
    #target.aftereffects
    #include T:/_Pipeline/cobopipe_v02-001/AfterEffect/AE_Scripts/NDS_SetDurationOfSubComps.jsx
    
    function ImportFootage(render_folder, footage_folder){
        precomp_folder = new Folder(render_folder);
        var my_footage_list = precomp_folder.getFiles('*001.*');
        var _duration = 0.08;
        //footage_folder = 
        for(i=0; i <my_footage_list.length;i++){
                file_path = render_folder + "/" + my_footage_list[i].name;
                my_footage = new File(file_path);
                import_options = new ImportOptions(my_footage);
                import_options.sequence = true;
                project_item = app.project.importFile(import_options);
                project_item.mainSource.conformFrameRate = 25.00;
                cur_duration = project_item.duration;
                if(cur_duration > _duration){
                    _duration = cur_duration;
                    }
                project_item.parentFolder = footage_folder;
        }
        return _duration;
    }

    function SavePrecompFile(comp_folder,precomp_name){
        var comp_folder = new Folder(comp_folder);
        var comp_file = new File(comp_folder.toString() +"/"+ precomp_name);
        var my_confirm = true;
        /*if(comp_file.exists){
            my_confirm = confirm ("A file already   exists, do you want save\nThis file as "+ shot + "_Comp_V001 ?", true, "OverWrite Comp?");
            }
        if(my_confirm){*/	
        if(!comp_folder.exists){comp_folder.create();
            }
        app.project.bitsPerChannel = 16;
        app.project.save(comp_file);
    }
     function FindItem(item_name, item_type){
        var project_content = app.project.items;
        for(var p =project_content.length;p>=1;p--){
            var cur_content = project_content[p];
            if(cur_content instanceof item_type){
                if(cur_content.name == item_name){
                    return cur_content
                    }
                }
            }
        return null
        }
    function Run(base_file, passes_folder, comp_folder, precomp_name){
        //var cur_proj = app.newProject();
        app.open(new File(base_file));
        var footage_folder = app.project.items.addFolder("Footage");
        var duration = ImportFootage(passes_folder,footage_folder);
        //var duration = frame_duration *(1/25);
        render_item = FindItem(".RENDER",CompItem);
        if(!render_item){
            render_item = app.project.items.addComp(".RENDER", 1920, 1080, 1, duration, 25);
            }
        work_item = FindItem(".WORK",CompItem);
        if(!work_item){
            work_item = app.project.items.addComp(".WORK", 1920, 1080, 1, duration, 25);
            render_item.layers.add(work_item);
        }        
        RunSetDuration(render_item,duration,0.04);
        SavePrecompFile(comp_folder, precomp_name);	
        }

    Run("%s", "%s","%s", "%s");
    """ % (base_file, passes_folder, comp_folder, precomp_name)

    script_file = open(precomp_script, "w")
    script_file.write(script_content)
    script_file.close()

    ae_create_precomp = 'afterfx -noui -r %s' % (precomp_script)
    subprocess.run(ae_create_precomp, shell=True,universal_newlines=True)
    # os.remove(precomp_script)
    print("Create %s " % precomp_name)
    return True


def CreateAEShot(template_file, anim_folder, shot_file,animatic):
    shot_script = "%sAutoCreateAnimScene.jsx" % anim_folder
    script_content = """
    #target.aftereffects
    
    function SaveFile(shot_file){
        //var comp_folder = new Folder(anim_folder);
        //var comp_file = new File(anim_folder.toString() +"/"+ shot_name + "_V001");
        //if(!comp_folder.exists){comp_folder.create();}
        var comp_file = new File(shot_file);
        app.project.bitsPerChannel = 8;
        app.project.save(comp_file);
    }
    
    function ImportFootage(animatic){
        var _duration = 0.08;
        my_footage = new File(animatic);
        import_options = new ImportOptions(my_footage);
        import_options.sequence = false;
        project_item = app.project.importFile(import_options);
        project_item.mainSource.conformFrameRate = 25.00;
        cur_duration = project_item.duration;
        if(cur_duration > _duration){
            _duration = cur_duration;
            }
        return [project_item,_duration];
    }
    
    function Run(base_file, shot_file,animatic){
        //var cur_proj = app.newProject();
        app.open(new File(base_file));
        animatic_import = ImportFootage(animatic);
        duration = animatic_import[1];
        //var duration = frame_duration *(1/25);
        render_item = app.project.items.addComp(".RENDER", 1920, 1080, 1, duration, 25);
        work_item = app.project.items.addComp(".WORK", 1920, 1080, 1, duration, 25);
        render_item.layers.add(work_item);
        work_item.layers.add(animatic_import[0]);
        SaveFile(shot_file);	
        }

    Run("%s","%s","%s");
    """ % (template_file,shot_file,animatic)

    script_file = open(shot_script, "w")
    script_file.write(script_content)
    script_file.close()

    ae_create_shot = 'afterfx -noui -r %s' % (shot_script)
    subprocess.run(ae_create_shot, shell=True, universal_newlines=True)
    os.remove(shot_script)
    print("Create %s " % shot_file)
    return True

#TODO Make applyCompToFocus look for Old_Footage and if Footage folder and old_footage folder exists, move footage from one to the other
def ApplyCompToFocus(dst_comp, src_comp, passes_folder,file_type,src_shot,dest_shot):
    script_path = "%s/ApplyComp.jsx" % passes_folder
    # print("Dest: %s Src: %s Pass: %s" % (dst_comp,src_comp,passes_folder))
    script_content = """
    #target.aftereffects
    
    function Run(dst_comp, src_comp,passes_folder,file_type,old_shot,new_shot){
        //Setting paths and variables
        var dst_file = new File(dst_comp);
        var project_folder = new Folder(dst_file.path);
        if(!project_folder.exists){project_folder.create();}

        
        //Running functions. Opening src comp, finding footing in src comp, 
        //check footage in src up against footage in passes folder, if footage in both places then replace it, otherwise just import it.
        //Rename footage_folder to OLD and place footage from passes folder in a new "Footage" folder.
        //Then set duration, based on the longest footage found, and save project.
        
        ImportProject(src_comp, dst_comp);
        var footage_folder = FindFootageFolder();
        var src_footage = ProjectFootage("." + file_type);
        var _duration = FindAndReplaceFootage(src_footage, passes_folder, footage_folder,file_type,old_shot,new_shot);
        SetRenderCompDuration(_duration);
        app.project.bitsPerChannel = 16;
        app.project.save(new File(dst_comp));
        }
    
    function ImportProject(src_comp, dst_comp){
        //var imp_prj = "C:/Temp/Sprinter_Project_Structure/Film/E010/sq010/sh010/Comp/E010_sq010_sh010_Comp_V001.aep";
        //var dest_prj = "C:/Temp/Sprinter_Project_Structure/Film/E010/sq010/sh020/Comp/E010_sq010_sh020_Comp_V001.aep";
        app.open(new File(src_comp));
        //app.project.save(new File(dst_comp));
        }
    //ADDED new FindFootageFolder functionality
    function FindFootageFolder(){
        var project_content = app.project.items;
        var my_folder = "";
        var old_folder_list = [];
        var old_folder = "";
        for(var p =project_content.length;p>=1;p--){
            var cur_content = project_content[p];
            if(cur_content instanceof FolderItem){
                var _name = cur_content.name;
                if(_name == "Footage"){
                    my_folder = cur_content;  
                }
                if(_name == "Old_Footage"){
                    old_folder_list.push(cur_content);
                }
            }
        }
        if (my_folder != ""){
            my_folder.name = "Old_Footage";
            old_folder_list.push(my_folder);
            }
        if(old_folder_list.length>0){
            old_folder = old_folder_list[0];
            for(var i=old_folder_list.length-1;i>=1;i--){
                var old_footage = old_folder_list[i].items;
               for(var x=old_footage.length;x>=1;x--){
                    old_footage[x].parentFolder = old_folder;
                    }
                old_folder_list[i].remove();
                }
        }
        return project_content.addFolder("Footage");
    }
    function ReplaceSceneFootage(source,dest){
        
        }
    function FindAndReplaceFootage(project_footage, base_path, parent_folder,file_type,old_shot,new_shot){	
        my_proj = app.project;
        var _duration = 0.05;
        //base_path = "C:/Temp/Sprinter_Project_Structure/Film/E010/sq010/sh020/Passes/";
        precomp_folder = new Folder(base_path);
        var my_footage_list = precomp_folder.getFiles('*001.'+ file_type);
        for(i=0; i <my_footage_list.length;i++){
            var old_footage = false;
            var scene_ref = false;
            if(my_footage_list[i].name.indexOf(new_shot)>-1){
                scene_ref = true;
                }
            for(x=0;x<project_footage.length;x++){
                if(project_footage[x].mainSource.file.name == my_footage_list[i].name){
                    old_footage = project_footage[x];
                    }
                if(project_footage[x].mainSource.file.name.indexOf(old_shot)>-1 && scene_ref){
                    old_footage = project_footage[x];
                    }
                }
            if(old_footage){
                var changed_footage = old_footage.replaceWithSequence(new File(my_footage_list[i]),false);
                var cur_duration = old_footage.duration;
                if(cur_duration > _duration){
                    _duration = cur_duration;
                    }
                old_footage.parentFolder = parent_folder;
                //cur_content.replaceWithSequence(new File(new_footage),false);
                }else{
                    file_path = base_path + "/" + my_footage_list[i].name;
                    my_footage = new File(file_path);
                    import_options = new ImportOptions(my_footage);
                    import_options.sequence = true;
                    project_item = my_proj.importFile(import_options);
                    project_item.mainSource.conformFrameRate = 25.00;
                    cur_duration = project_item.duration;
                    if(cur_duration > _duration){
                        _duration = cur_duration;
                        }
                    project_item.parentFolder = parent_folder;
                    }
            }
        return _duration;
    
    }
    
    function SetRenderCompDuration(cur_length){
        var render_comp_list = [];
        var project_content = app.project.items;
        for(var p =project_content.length;p>=1;p--){
            var cur_content = project_content[p];
            if(cur_content instanceof CompItem){
                var _name = cur_content.name;
                if(_name == ".RENDER"){
                    SetDuration(cur_content, cur_length);
                }
            }
        }
    }
    
    
    
    //ImportProject()
    function ProjectFootage(extension){//Find the footage items in the current project that has a source that ends with 'extension'
        var project_footage_list = [];
        var project_content = app.project.items;
        for(var p =project_content.length;p>=1;p--){
            var cur_content = project_content[p];
            if(cur_content instanceof FootageItem){
                if(cur_content.mainSource instanceof FileSource){
                    var cur_name = cur_content.mainSource.file.name;
                    if( cur_name.search(extension)>=0 ){
                        var old_footage = cur_content.mainSource.file.name;
                        var old_name = cur_content.name;
                        project_footage_list.push(cur_content);
                        }
                    }
            }
        }
        return project_footage_list
    }
    
    
    function SetDuration(cur_comp, cur_length){
            if(cur_comp==null){
                var cur_comp = app.project.selection[0];
                if(cur_comp==undefined){
                    return;
                }
                var cur_length = cur_comp.duration;
            }
            else{
                cur_comp.duration = cur_length;
                }
            var comp_layers =  cur_comp.layers;
            for(var c = 1; c<=comp_layers.length; c++){
                var cur_layer = comp_layers[c];
                if(cur_layer.source instanceof CompItem){
                    SetDuration(cur_layer.source,cur_length);
                    }
                }
            SetOutPoint(cur_comp, cur_length)
        }
    
    function SetOutPoint(my_comp, my_length){
        my_layers = my_comp.layers;
        for(var l=my_layers.length;l>=1;l--){
            set_lock = false;
            if(my_layers[l].locked == true){
                my_layers[l].locked=false;
                set_lock = true;
                }
            my_layers[l].outPoint = my_length;
            if(set_lock){
                my_layers[l].locked=true;
            }
        }
    }
    Run("%s","%s","%s","%s","%s","%s")
    """ % (dst_comp, src_comp,passes_folder,file_type,src_shot,dest_shot)

    script_file = open(script_path, "w")
    script_file.write(script_content)
    script_file.close()

    ae_apply = 'afterfx -noui -r %s' % (script_path)
    logger.info("RUNNING :: " + ae_apply)
    subprocess.run(ae_apply, shell=True,universal_newlines=True)
    # os.remove(script_path) // Deletes before subprocess finishes
    # print("Create %s " % script_path)
    return True

def RenderShot(scene_path, output_folder, output_name, watchfolder_path):
    comp_name = ".RENDER"
    output_settings = "Best Settings"
    output_module = "TIF_Render"
    file_name = "%s_[####]" % output_name

    output_path = "%s%s" % (output_folder,file_name)
    if not(os.path.exists(output_folder)):
        os.makedirs(output_folder)


    if(watchfolder_path==""):
        # ORIGINAL: string_command = 'aerender -project %s -comp ".RENDER" -RStemplate "%s" -OMtemplate "%s" -output %s' % (scene_path, render_settings, render_module, output_path)
        string_command = 'aerender -project %s -comp ".RENDER" -v "ERRORS" -RStemplate "%s" -OMtemplate "%s" -output %s' % (scene_path, output_settings, output_module, output_path)
        # print(string_command)
        subprocess.run(string_command, shell=True, universal_newlines=True)
    else:
        script_content = """
        function WatchFolderRender(scene_path, output_folder, output_name, watchfolder_path,comp_name, output_module, output_settings){
            app.open(new File(scene_path));
            
            //var comp_name = ".RENDER";
            //var output_module = "TIF_Render";
            //split filename to find episode and shot number
        
            var project_name = output_name  + "_Comp";
            var file_name = output_name  + "_[####]";
        
            var render_comp = FindOutputComp(comp_name);
            if(render_comp){
                output_path = output_folder + output_name;
                setup =SimpleRenderQueue(render_comp, output_path, output_settings, output_module);
                if(setup==true){
                    CreateWatchfolderProject(project_name, watchfolder_path);
                    }
            }
        }
        
        function CreateWatchfolderProject(project_name, watchfolder_path){
            //var cur_project = new File(app.project.file);
            //app.project.save(cur_project);
            var text_string = 'After Effects 13.2v1 Render Control File\\nmax_machines=10\\nnum_machines=0\\ninit=0\\nhtml_init=0\\nhtml_name=""';
            var folder_path = watchfolder_path + project_name + "/";
            var text_name = project_name + "_RCF.txt";
        
            var project_folder = new Folder(folder_path);
            if(!project_folder.exists){project_folder.create();}
        
            var text_path = new File(folder_path + text_name);
            text_path.open("w");
            text_path.write(text_string);
            text_path.close();
        
            project_file = new File(folder_path + project_name + ".aep");
            app.project.save(project_file);
        }
        
        
        function SimpleRenderQueue(render_comp, output_path, out_settings, out_module){
            var renderSetting = out_settings;
            var outputModule = out_module;
        
            while(app.project.renderQueue.numItems >= 1) {
                    app.project.renderQueue.item(1).remove();
                }
        
            var render_item = app.project.renderQueue.items.add(render_comp);
            
            var outputMO = render_item.outputModules[1];
            var out_found = false;
            for (var i=0; i<outputMO.templates.length; i++){
                if (outputMO.templates[i].indexOf(outputModule)==0){
                    out_found = true
                    }
                }
            if(out_found){
                outputMO.applyTemplate(outputModule); 
                render_item.applyTemplate(renderSetting);
                outputMO.file = new File(output_path);
                return true
                }else{
                    app.project.renderQueue.item(1).remove();
                    return false
                    }
        }
        //Find Render Comp
        function FindOutputComp(comp_name){
            var to_return = false;
            var project_content = app.project.items;
            for(var p =project_content.length;p>=1;p--){
                var cur_content = project_content[p];
                if(cur_content instanceof CompItem){
                    if(cur_content.name == comp_name){
                        to_return = cur_content;
                        }
                    }
                }
            return to_return;
            }
        WatchFolderRender('%s', '%s', '%s', '%s','%s', '%s', '%s');
        """ % (scene_path,output_folder,output_name,watchfolder_path, comp_name, output_module, output_settings)
        script_path = scene_path + "_WatchScript.jsx"
        script_file = open(script_path, "w")
        script_file.write(script_content)
        script_file.close()
        ae_apply = 'afterfx -noui -r %s' % (script_path)
        result = subprocess.run(ae_apply, shell=True, universal_newlines=True)
        print("Added shot to watchfolder")
        os.remove(script_path)




# shot_folder = "P:/_WFH_Projekter/930448_MSP_academy/Film/E010/sq050/sh140/"
# passes_folder = shot_folder + "Passes/";
# comp_folder = shot_folder + "Comp/";
# precomp_name = "E010_sq050_sh140_Precomp";
# CreatePrecomp(passes_folder,comp_folder,precomp_name)
# cur_src = "P:/930462_HOJ_Project/Production/Film/S104/S104_SQ050/S104_SQ050_SH180/Comp/S104_SQ050_SH180_Precomp.aep"
# cur_dst = "P:/930462_HOJ_Project/Production/Film/S104/S104_SQ050/S104_SQ050_SH200/Comp/S104_SQ050_SH200_Precomp.aep"
# cur_pass = "P:/930462_HOJ_Project/Production/Film/S104/S104_SQ050/S104_SQ050_SH200/Passes"
# file_type = "TGA"
# ApplyCompToFocus(cur_dst,cur_src,cur_pass,file_type)
# RenderShot('P:/930444_SprinterGalore_Animated_S01/Production/Film/E010/sq010/sh010//Comp//E010_sq010_sh010_Precomp.aep','P:/930444_SprinterGalore_Animated_S01/Production/Film/E010/sq010//TIF/E010_sq010_sh010/','E010_sq010_sh010','')