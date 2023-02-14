function getParentWidget(){
	var topWidgets = QApplication.topLevelWidgets();
	for( var i in topWidgets ){
		if( topWidgets[i] instanceof QMainWindow && !topWidgets[i].parentWidget() ){
			return topWidgets[i];
		}
	}
	return "";
}

//TODO Check for sound both in toonboom and outside

createPreviewUI.prototype = new QDialog();
function createPreviewUI(){
    QDialog.call(this)

    this.CreatePreview = CreatePreview

    this.objectName = "CreatePreviewUI";
    this.setWindowFlags(Qt.WindowStaysOnTopHint);
	this.parent = getParentWidget();

	this.base_lay = new QVBoxLayout();
	this.top_lay = new QHBoxLayout();
	this.quality_lay = new QHBoxLayout()
	this.slate_lay = new QHBoxLayout()
	this.network_lay = new QHBoxLayout()
	this.level_lay = new QHBoxLayout()

	this.base_lay.addLayout(this.top_lay,0)
	this.base_lay.addLayout(this.quality_lay,0)
	this.base_lay.addLayout(this.slate_lay,0)
	this.base_lay.addLayout(this.network_lay,0)
	this.base_lay.addLayout(this.level_lay,0)
	this.setLayout(this.base_lay);

    this.create_bttn = new QPushButton("Create Preview");
    this.top_lay.addWidget(this.create_bttn,0,1);

    this.quality_label = new QLabel("Quality: ")
    this.quality_label.minimum = 150;
    this.quality_group = new QButtonGroup()
    this.quality_on_bttn = new QRadioButton("OpenGL",this.quality_group)
    this.quality_off_bttn = new QRadioButton("Render",this.quality_group)
    this.quality_group.addButton(this.quality_on_bttn,1)
    this.quality_group.addButton(this.quality_off_bttn,0)
    this.quality_on_bttn.checked = true;
    this.quality_lay.addWidget(this.quality_label,0,1)
    this.quality_lay.addWidget(this.quality_on_bttn,0,1)
    this.quality_lay.addWidget(this.quality_off_bttn,0,1)


    this.slate_label = new QLabel("Slate: ")
    this.slate_label.minimum = 150;
    this.slate_group = new QButtonGroup()
    this.slate_on_bttn = new QRadioButton("ON",this.slate_group)
    this.slate_off_bttn = new QRadioButton("OFF",this.slate_group)
    this.slate_on_bttn.checked = true;
    this.slate_group.addButton(this.slate_on_bttn,1)
    this.slate_group.addButton(this.slate_off_bttn,0)

    this.slate_lay.addWidget(this.slate_label,0,1);
    this.slate_lay.addWidget(this.slate_on_bttn,0,1);
    this.slate_lay.addWidget(this.slate_off_bttn,0,1);


    this.network_label = new QLabel("Working: ")
    this.network_label.minimum = 150;
    this.network_group = new QButtonGroup()
    this.network_on_bttn = new QRadioButton("Server",this.network_group)
    this.network_off_bttn = new QRadioButton("Local",this.network_group)
    this.network_group.addButton(this.network_on_bttn,1)
    this.network_group.addButton(this.network_off_bttn,0)
//    this.network_group.setId(this.network_on_bttn,0)
    this.network_on_bttn.checked = true;
    this.network_lay.addWidget(this.network_label,0,1);
    this.network_lay.addWidget(this.network_on_bttn,0,1);
    this.network_lay.addWidget(this.network_off_bttn,0,1);


    this.level_label = new QLabel("Level: ")
    this.level_label.minimum = 150;
    this.level_group = new QButtonGroup()
    this.level_on_bttn = new QRadioButton("Blocking",this.level_group)
    this.level_off_bttn = new QRadioButton("Anim",this.level_group)
    this.level_group.addButton(this.level_on_bttn,1)
    this.level_group.addButton(this.level_off_bttn,0)
    this.level_on_bttn.checked = true;
    this.level_lay.addWidget(this.level_label,0,1);
    this.level_lay.addWidget(this.level_on_bttn,0,1);
    this.level_lay.addWidget(this.level_off_bttn,0,1);

    this.check_list = [this.quality_off_bttn,this.slate_off_bttn,this.network_off_bttn,this.level_off_bttn]

    this.create_bttn.clicked.connect(this,this.run_preview);



    this.load_ui_state = function(){
        var file_path = "C:\\Temp\\TB\\_SaveState\\CreatePreview.json";
        var json_file = new PermanentFile(file_path);
        if(json_file.exists()){
            json_file.open(1);
            var json_content = json_file.read();
            json_file.close();
            var check_state = JSON.parse(json_content);
            for(i in check_state){
                this.check_list[i].setChecked(check_state[i]);
            }
        }
    }

    this.save_ui_state = function(){
        var state = [];
        for(i in this.check_list){
            var bttn = this.check_list[i];
            state.push(bttn.checked);
        }

        var folder_path = "C:\\Temp\\TB\\_SaveState"
        var dir = new Dir(folder_path)
        if(!dir.exists){
            dir.mkdirs();
        }

        var file_path = folder_path + "\\" + "CreatePreview.json";
        var json_file = new PermanentFile(file_path);
        json_file.open(2);
        json_file.write(JSON.stringify(state));
        json_file.close();
    }
    this.load_ui_state()
    this.setGeometry(300,300,300,150)

}

createPreviewUI.prototype.run_preview = function(){
//    this.create_preview("Move")
    this.save_ui_state()
    this.CreatePreview(this.quality_group.checkedId(), this.network_group.checkedId(),this.slate_group.checkedId(),this.level_group.checkedId());
//    this.create_func()
//    CreatePreview(this.quality_group.checkedId(), this.network_group.checkedId(),this.slate_group.checkedId(),this.level_group.checkedId());
}

const CreatePreview = function(opengl,network,with_slate,blocking){
    const GetProjectSettings = require("CB_GetInfo.js").GetProjectSettings;
    const loadConfigJson = require("CB_GetInfo.js").loadConfigJson;
    const GetUser = require("CB_GetInfo.js").GetUser;

    MessageLog.trace("quality: "+ opengl +" - network:" +network+ "- slate: " +with_slate+ " -blocking:" +blocking)
    this.python_path = "T:/_Executables/python/Python310/python.exe"

    var python_exe = new File(this.python_path);
    if(!python_exe.exists){
        this.python_path = "python.exe"
        }

    this.MakeSlate_withServerPython = function(shot_name,temp_path,preview_path, project_name, crop, width, height,soundPath,user){
    MessageLog.trace('MakeSlate with server python - inhouse');
//        var pythonPath = "T:/_Executables/python/Python310/python.exe";
    var pipeline_path = loadConfigJson();

    var scriptPath = System.getenv("BOM_PIPE_PATH") + "/Preview/harmony/slate.py";

    MessageLog.trace(this.python_path + ' ' + scriptPath + ' ' + project_name + ' ' + shot_name + ' ' + temp_path +' ' +preview_path + ' ' + crop + ' ' + width + ' ' + height + ' ' + soundPath + ' ' + "Christian")
    p1 = new Process2(this.python_path, scriptPath, project_name, shot_name, temp_path, preview_path, crop, width, height,soundPath,1,user)
    p1.launchAndDetach();
    }
    this.crop_withServerPython = function(shot,temp_path,final_path,project_name,width,height){
        MessageLog.trace('Crop with server python - inhouse');
//        var pythonPath = "T:/_Executables/python/Python310/python.exe";
        var scriptPath = System.getenv("BOM_PIPE_PATH") + "/Preview/harmony/cropIn.py";
        MessageLog.trace(this.python_path + " \"" + scriptPath + "\" " + project_name + " " + shot +" \""+ temp_path +"\" "+" \""+ final_path +"\" "+ width +" "+ height);
        p1 = new Process2(this.python_path, scriptPath, project_name, shot, temp_path,final_path, width, height)
        p1.launchAndDetach();
    }

    var cur_scene = scene.currentVersionName();
	var cur_full_path = scene.currentProjectPath();
	if(cur_scene.indexOf("_V")!= -1){
		shot = cur_scene.split("_V")[0];
	}else{
		shot = cur_scene;
	}
	var seq_path = cur_full_path.split("/" + shot + "/")[0];
	var preview_name = shot;
	var preview_dir = seq_path + "/_Preview/";
	var preview_path = seq_path +"/_Preview/" + preview_name + ".mov";

	if (blocking){
	    preview_name = shot + "_Blocking"
	    preview_dir = seq_path + "/_Preview/Blocking/";
	    preview_path = preview_dir + preview_name + ".mov";
	    }
    var dir = new Dir(preview_dir);
    if(!dir.exists){
        dir.mkdirs();
        }

	var temp_path = "C:/Temp/temp_previews/" + preview_name + "_Temp.mov";
	var crop = false;

	var width = 1280;
	var height = 720;

	var soundPath = seq_path + "/" + shot + "/" + shot + "_Sound.wav";
	var sound_test = new File(soundPath);
	if(!new File(soundPath).exists){
	    soundPath = false;
	    MessageLog.trace("NO SOUND FILE FOUND -> WILL FAIL")
	}
	var project_settings = false;
	var user = null;
    if (network){
	    project_settings = GetProjectSettings();
        if (project_settings){
            var size_multiplier = project_settings.tb_size_multi;
            //ask for user here.
            //var cur_user = preferences.getString("CreatePreview_ProjectUser","")
            //if(cur_user){
            user = GetUser();
            if(user){
                MessageLog.trace("User:" + user)
                preferences.setString("CreatePreview_ProjectUser",user)
                }
               //}
            //And remember the user for next time.
        }
    }else{
	    var size_multiplier = 1.1;
        var cur_user = preferences.getString("CreatePreview_User","")
	    var user_input = Input.getText( "User:" , cur_user , "Write User:" );
        if(user_input){
            user = user_input
	        preferences.setString("CreatePreview_User",user_input)
	    }

    }
	var crop = false;
	if(size_multiplier > 1.0){
		crop = true
		var floatWidth = parseFloat(width).toFixed(2) * size_multiplier;
		var floatHeight = parseFloat(height).toFixed(2) * size_multiplier;
		var renderWidth = parseInt(floatWidth)
		var renderHeight = parseInt(floatHeight)
		var renderWidthString = renderWidth + "";
		var renderHeightString = renderHeight + "";
        var x_cord = (floatWidth - parseFloat(width).toFixed(2)) / 2.00;
        var y_cord = (floatHeight - parseFloat(height).toFixed(2)) / 2.00;
		MessageLog.trace("Export Settings: W: " + renderWidthString + " - H: " + renderHeightString +" Crop: True");
	}else{
	  	var renderWidthString = width + "";
		var renderHeightString = height + "";
		var x_cord = (parseFloat(width).toFixed(2)) / 2.00;
        var y_cord = (parseFloat(height).toFixed(2)) / 2.00;
	}

    if(opengl){
        if(with_slate||crop){
            exporter.exportOGLToQuicktime(preview_name + "_Temp","C:/Temp/temp_previews/","-1","-1",renderWidthString,renderHeightString);
        }else{
            exporter.exportOGLToQuicktime(preview_name,preview_dir,"-1","-1",renderWidthString,renderHeightString);
            return;
        }

    }else{
        if(with_slate||crop){
            exporter.exportToQuicktime("", "-1","-1", true, renderWidthString, renderHeightString, temp_path, "", false, "1");
        }else{
            MessageLog.trace(preview_path)
            exporter.exportToQuicktime("", "-1","-1", true, renderWidthString, renderHeightString, preview_path, "", false, "1");
            var quickTime = "C:\\Program Files (x86)\\QuickTime\\QuickTimePlayer.exe";
            p2 = new Process2(quickTime, preview_path.replace("/", "\\"));
            p2.launchAndDetach();
            return;
        }
    }
    if(network){
        if(with_slate){
               //this doesnt work
            this.MakeSlate_withServerPython(shot, temp_path,preview_path, project_name, crop, width, height,soundPath,user);
        }else{
            this.crop_withServerPython(shot, temp_path,preview_path, project_name, width, height);
        }
    }else{
        if(with_slate){
            MakeSlate_NoServerPython(temp_path,soundPath,preview_path,shot,crop,width,height,x_cord,y_cord);
        }else{
            Crop_NoServerPython(temp_path,preview_path,width,height,x_cord,y_cord);
        }
    }





    function MakeSlate_NoServerPython(input_path, soundPath,output_path, shot_name, crop, width, height,x_cord,y_cord){
        var date = new Date();
        var timestamp = String(date.getFullYear()) + "-" + String(date.getMonth()+1) + "-" + String(date.getDate()) + "_" + String(date.getHours()) + "\\\\:" + String(date.getMinutes());
        MessageLog.trace("ffmpeg -i "+soundPath + " -i " + input_path + " -filter_complex [0:a]asetpts=expr=PTS-STARTPTS[s0];[1:v]crop=h=" + height + ":w=" + width + ":x=" + x_cord.toFixed(1) + ":y=" + y_cord.toFixed(1) + "[s1];[s1]drawtext=fontcolor=white:fontfile=/Windows/Fonts/Arial.ttf:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text="+ shot_name +":x=w-(text_w+20):y=20[s2];[s2]drawtext=fontcolor=white:fontfile=/Windows/Fonts/Arial.ttf:fontsize=24:shadowcolor=black:shadowx=1.5:shadowy=1.5:start_number=1:text=%{eif\\\\:n\\\\:d\\\\:5}:x=w-(text_w+20):y=50[s3];[s3]drawtext=fontcolor=white:fontfile=/Windows/Fonts/Arial.ttf:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=" +timestamp +":x=w-(text_w+20):y=h-(text_h+20)[s4] -map [s0] -map [s4] -acodec pcm_s16le -pix_fmt yuv420p " + output_path +" -y");
        proc_string = "ffmpeg -i "+soundPath + " -i " + input_path + " -filter_complex [0:a]asetpts=expr=PTS-STARTPTS[s0];[1:v]crop=h=" + height + ":w=" + width + ":x=" + x_cord.toFixed(1) + ":y=" + y_cord.toFixed(1) + "[s1];[s1]drawtext=fontcolor=white:fontfile=/Windows/Fonts/Arial.ttf:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text="+ shot_name +":x=w-(text_w+20):y=20[s2];[s2]drawtext=fontcolor=white:fontfile=/Windows/Fonts/Arial.ttf:fontsize=24:shadowcolor=black:shadowx=1.5:shadowy=1.5:start_number=1:text=%{eif\\\\:n\\\\:d\\\\:5}:x=w-(text_w+20):y=50[s3];[s3]drawtext=fontcolor=white:fontfile=/Windows/Fonts/Arial.ttf:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=" +timestamp +":x=w-(text_w+20):y=h-(text_h+20)[s4] -map [s0] -map [s4] -acodec pcm_s16le -pix_fmt yuv420p " + output_path +" -y";
        launchProcess_ForNoServerPython(proc_string,input_path,output_path);
    }

    function Crop_NoServerPython(input_path,output_path,width,height,x_cord,y_cord){
        MessageLog.trace("ffmpeg -i " + input_path + " -filter_complex [0:a]asetpts=expr=PTS-STARTPTS[s0];[0:v]crop=h=" + height + ":w=" + width + ":x=" + x_cord.toFixed(1) + ":y=" + y_cord.toFixed(1) + "[s1] -map [s0] -map [s1] -acodec pcm_s16le -pix_fmt yuv420p " + output_path + " -y");
        proc_string = "ffmpeg -i "  + input_path + " -filter_complex [0:a]asetpts=expr=PTS-STARTPTS[s0];[0:v]crop=h=" + height + ":w=" + width + ":x=" + x_cord.toFixed(1) + ":y=" + y_cord.toFixed(1) + "[s1] -map [s0] -map [s1] -acodec pcm_s16le -pix_fmt yuv420p " + output_path + " -y";
        launchProcess_ForNoServerPython(proc_string,input_path,output_path);
    }

    function copyAndOpenPreview(input_path,output_path){
        old_file = new PermanentFile(input_path);
        new_file = new PermanentFile(output_path);
        old_file.copy(new_file);
        var quickTime = "C:\\Program Files (x86)\\QuickTime\\QuickTimePlayer.exe";
        p1 = new Process2(quickTime, output_path.replace("/", "\\"));
        p1.launchAndDetach();
    }

    function launchProcess_ForNoServerPython(preview_proc_string,input_path,output_path){
        preview_proc = new Process2(preview_proc_string)
        preview_proc.launch();
        old_file = new PermanentFile(input_path);
        new_file = new PermanentFile(output_path);
        if(preview_proc.isAlive()){
            preview_proc.terminate();
        }

        killQuicktime = new Process2("taskkill", "/im", "QuickTimePlayer.exe");
        killQuicktime.launch();
        killVLC = new Process2("C:\\Windows\\System32\\taskkill.exe", "/im", "vlc.exe");
        killVLC.launch();

    //	if(new_file.exists()==true){
    //		var i = 0;
    //		while(old_file.exists()==true && i<500){
    //			old_file.remove();
    //			i = i +1;
    //		}
    //	}
        var quickTime = "C:\\Program Files (x86)\\QuickTime\\QuickTimePlayer.exe";
        p2 = new Process2(quickTime, output_path.replace("/", "\\"));
        p2.launchAndDetach();
    }
}

function createPreviewDialog(){
//    exporter.exportToQuicktime("", "-1","-1", true, 1280, 720, "C:/Temp/temp_previews/S229_SQ010_SH030.mov", "", false, "1");
//    exporter.exportOGLToQuicktime("Test_Temp","C:/Temp/temp_previews/","-1","-1",1280,720);
    var ui = new createPreviewUI()

    ui.show()
}


