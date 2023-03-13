function getParentWidget(){
	var topWidgets = QApplication.topLevelWidgets();
	for( var i in topWidgets ){
		if( topWidgets[i] instanceof QMainWindow && !topWidgets[i].parentWidget() ){
			return topWidgets[i];
		}
	}
	return "";
}


// function redoSelection(){
// 	var selected_nodes = selection.selectedNodes();
// 	var selected_waypoints = selection.selectedWaypoints();
// 	var selected_columns = [];
// 	for(var i = 0; i < selection.numberOfColumnsSelected(); ++i){
// 		var selected_column = selection.selectedColumn(i);
// 		selected_columns.push(selected_column)
// 	}

// 	selection.clearSelection()
// 	for(i in selected_nodes){selection.addNodeToSelection(selected_nodes[i])}
// 	for(i in selected_waypoints){selection.addWaypointToSelection(selected_waypoints[i])}
// 	for(i in selected_columns){selection.addColumnToSelection(selected_columns[i])}
// }




QuickSlider.prototype = new QDialog();
function QuickSlider(min,max){
    QDialog.call(this)
    this.objectName = "QuickSlider";
    this.min = min
    this.max = max
    this.slider_list = [];
    this.setWindowFlags(Qt.WindowStaysOnTopHint);
	this.parent = getParentWidget();
	this.base_lay = new QVBoxLayout();
	this.top_lay = new QHBoxLayout();
	this.slider_lay = new QVBoxLayout();
	this.base_lay.addLayout(this.top_lay,0)
	this.base_lay.addLayout(this.slider_lay,1)
	this.setLayout(this.base_lay);
	this.zero_check = new QCheckBox("Camera Based");
	this.zero_check.checked = 1
    this.intVal = new QIntValidator(this.min,this.max)
    this.min_label = new QLabel("Min:")
    this.max_label = new QLabel("Max:")

    this.edit_min_value = new QLineEdit();
    this.edit_min_value.setValidator(this.intVal);
    this.edit_min_value.setFixedWidth(40);

    this.edit_max_value = new QLineEdit();
    this.edit_max_value.setValidator(this.intVal);
    this.edit_max_value.setFixedWidth(40);

    this.init_bttn = new QPushButton("Load Selection");
    this.init_bttn.objectName = "loadBttn";
    this.select_bttn = new QPushButton("Select All");
    this.loadState = new QPushButton("Load State");
    this.saveState = new QPushButton("Save State");


    this.top_lay.addWidget(this.min_label,0,1);
    this.top_lay.addWidget(this.edit_min_value,0,1);
    this.top_lay.addWidget(this.max_label,0,1);
    this.top_lay.addWidget(this.edit_max_value,0,1);

    this.top_lay.addWidget(this.init_bttn,1,1);
    this.top_lay.addWidget(this.select_bttn,1,1);
    this.top_lay.addWidget(this.loadState,1,1);
    this.top_lay.addWidget(this.saveState,1,1);
    this.top_lay.addWidget(this.zero_check,0,1);
    this.edit_max_value.text = this.max;
    this.edit_min_value.text = this.min;
    this.init_bttn.clicked.connect(this, this.init_func);
    this.select_bttn.clicked.connect(this, this.select_call);
    this.loadState.clicked.connect(this, this.load_ui_state);
    this.saveState.clicked.connect(this, this.save_ui_state);

    this.update_minmax_func = function(){
        this.min = this.edit_min_value.text
        this.max = this.edit_max_value.text
        for(var k=0;k<this.slider_list.length;k++){
            var cur_slider = this.slider_list[k];
            cur_slider.slider.setRange(this.min, this.max)
//            cur_slider.slider.intVal.setRange(this.min,this.max)
        }
    }
    this.clear_func = function(){
        for(var x=this.slider_list.length-1;x>=0;x--){
            var my_w_w = this.slider_list[x];
            my_w_w.deleteLater();
            this.slider_lay.removeWidget(my_w_w)
        }
    }
    this.select_func = function(){
        selection.clearSelection();
        for(var x=this.slider_list.length-1;x>=0;x--){
            var my_w_w = this.slider_list[x];
            selection.addNodeToSelection(my_w_w.name);
        }
    }

    this.build_func = function(selected_nodes){
        this.clear_func();
        this.slider_list = [];
        // var selected_nodes = selection.selectedNodes()
        if(selected_nodes == null){
            selected_nodes = selection.selectedNodes()
        }
        var fg_nodes = [];
        var mg_nodes = [];
        var bg_nodes = [];
        var to_remove = [];

        for(i in selected_nodes){
            var node_name = selected_nodes[i].split('/')[selected_nodes[i].split('/').length-1]
            if(node_name.slice(0, 2) == 'FG'){
                fg_nodes.push(selected_nodes[i]);
                to_remove.push(selected_nodes[i]);
            }
            if(node_name.slice(0, 2) == 'MG'){
                mg_nodes.push(selected_nodes[i]);
                to_remove.push(selected_nodes[i]);
            }
            if(node_name.slice(0, 2) == 'BG'){
                bg_nodes.push(selected_nodes[i]);
                to_remove.push(selected_nodes[i]);
            }
        }

        MessageLog.trace(selected_nodes)
        for(i in to_remove){
            MessageLog.trace("remove: " + to_remove[i])
            selected_nodes.splice(selected_nodes.indexOf(to_remove[i]),1);
            MessageLog.trace("Left: " + String(selected_nodes))
        }


        var sorted_list = fg_nodes.sort();
        sorted_list = sorted_list.concat(mg_nodes.sort());
        sorted_list = sorted_list.concat(bg_nodes.sort());
        sorted_list = sorted_list.concat(selected_nodes.sort());
        MessageLog.trace(sorted_list)

        // MessageLog.trace(sorted_list);
        var scene_nodes = node.getNodes(["PEG"]);

        for(i in sorted_list){
            if(scene_nodes.indexOf(sorted_list[i]) > -1){
                var cur_name = sorted_list[i];
                var slider = new createSlider(this,cur_name,this.min,this.max);
                this.slider_lay.addWidget(slider,1,1)
                this.slider_list.push(slider);
            }
        }
    }

    this.load_ui_state = function(){
        var file_path = "C:\\Temp\\TB\\_SaveState\\depth_slider_ui.json";
        var json_file = new PermanentFile(file_path);
        json_file.open(1);
        var json_content = json_file.read();
        json_file.close();

        var sliders = JSON.parse(json_content);
        this.build_func(sliders)
    }

    this.save_ui_state = function(){
        var state = [];
        for(i in this.slider_list){
            state.push(this.slider_list[i].name)
        }

        var folder_path = "C:\\Temp\\TB\\_SaveState"
        var dir = new Dir(folder_path)
        if(!dir.exists){
            dir.mkdirs();
        }

        var file_path = folder_path + "\\" + "depth_slider_ui.json";
        var json_file = new PermanentFile(file_path);
        json_file.open(2);
        json_file.write(JSON.stringify(state));
        json_file.close();
    }

    this.edit_min_value.editingFinished.connect(this,this.update_minmax_func);
    this.edit_max_value.editingFinished.connect(this,this.update_minmax_func);
//    this.build_func();

    function getSliderPosition(peg){
        var node_matrix = node.getMatrix(peg,  frame.current());
        var node_position = node_matrix.extractPosition();
        var value = scene.fromOGLZ(node_position.z).toFixed(0);
        return Math.abs(parseInt(value))
    }

    function updatePeg(my_peg,my_value,cam){

        var z_units = scene.numberOfUnitsZ();
        //var cam = false; //this.cam_check.checked
        //MessageLog.trace(cam)
    //
        if(cam){
            var camera_matrix = scene.getCameraMatrix(frame.current());
            var camera_position = camera_matrix.extractPosition();
        }else{
            var camera_position = new Point3d(0.0,0.0,scene.toOGLZ(z_units));
        }

//        MessageLog.trace(camera_position)
        var node_matrix = node.getMatrix(my_peg,  frame.current());
    //    MessageLog.trace(node_matrix)
        var node_position = node_matrix.extractPosition();
        var node_scale = node_matrix.extractScale();

        // var scale_attribute = node.getAttr(my_peg, frame.current(), "SCALE");
        // var scale_sub_attributes = scale_attribute.getSubAttributes();
        // var scale_X = scale_sub_attributes[3].doubleValue();
        // var scale_Y = scale_sub_attributes[4].doubleValue();


        var z_depth = scene.fromOGLZ(node_position.z - camera_position.z)

        var base_scale_X = node_scale.x / (z_depth / z_units)
        var base_scale_Y = node_scale.y / (z_depth / z_units)

        var new_z = -my_value.toFixed(2);

        var vector = Vector3d(node_position.x - camera_position.x, node_position.y - camera_position.y, node_position.z - camera_position.z)
        
        var new_x = (scene.fromOGLX(vector.x) * ((new_z - scene.fromOGLZ(camera_position.z)) / z_depth)) + scene.fromOGLX(camera_position.x)
        var new_y = (scene.fromOGLY(vector.y) * ((new_z - scene.fromOGLZ(camera_position.z)) / z_depth)) + scene.fromOGLY(camera_position.y)

        var new_scale_X = ((new_z - scene.fromOGLZ(camera_position.z)) / z_units) * base_scale_X
        var new_scale_Y = ((new_z - scene.fromOGLZ(camera_position.z)) / z_units) * base_scale_Y
//        scene.beginUndoRedoAccum("Set Position");
//        var position_attribute = node.getAttr(my_peg, frame.current(), "POSITION");
    //	position_attribute.setValue(Point3d(new_x, new_y, new_z));

//        node.setTextAttr(my_peg,"POSITION.x",frame.current(),"-50.0");
//        node.setTextAttr(my_peg,"POSITION.y",frame.current(),"-50.0");


//        var orig_3d_point = position_attribute.pos3dValue()
    //    MessageLog.trace(orig_3d_point.x)
//        position_attribute.setValue(Point3d(orig_3d_point.x , orig_3d_point.y, new_z));
    //	position_attribute.setValue(Point3d(scene.fromOGLX(vector.x) , scene.fromOGLY(vector.y), new_z));
        if(cam){
        node.setTextAttr(my_peg,"POSITION.x",frame.current(),String(new_x));
        node.setTextAttr(my_peg,"POSITION.y",frame.current(),String(new_y));
        }
        node.setTextAttr(my_peg,"POSITION.z",frame.current(),String(new_z));
        node.setTextAttr(my_peg,"SCALE.x",frame.current(),String(new_scale_X));
        node.setTextAttr(my_peg,"SCALE.y",frame.current(),String(new_scale_Y));
//        scale_sub_attributes[3].setValue(new_scale_X);
//        scale_sub_attributes[4].setValue(new_scale_Y);
//    	scene.endUndoRedoAccum();
        }
    function reset_peg_function(my_peg){
        node.setTextAttr(my_peg,"POSITION.x",frame.current(),String(0));
        node.setTextAttr(my_peg,"POSITION.y",frame.current(),String(0));
        node.setTextAttr(my_peg,"POSITION.z",frame.current(),String(0));
        node.setTextAttr(my_peg,"SCALE.x",frame.current(),String(0));
        node.setTextAttr(my_peg,"SCALE.y",frame.current(),String(0));

    }

    createSlider.prototype = new QWidget;
    function createSlider(parent,name, min,max){
        QWidget.call(this);
        this.parent = parent;
        this.name = name;
        this.pretty_name = name.split("Top/")[1]
        //MessageLog.trace(this.pretty_name)
        this.min = min;
        this.max = max;
        this.f_layout = new QHBoxLayout();
        this.setLayout(this.f_layout);
//        this.objectName = "pegSlider";

        this.label = new QLabel(this.pretty_name)
        var l = 150;
        this.label.minimumWidth = l;
        this.slider = new QSlider();
        this.slider.objectName = "pegSlider";
        this.slider.setOrientation(Qt.Horizontal)
        this.slider.minimumWidth = 200;
        this.slider.setRange(this.min,this.max)

        this.number_value = new QLineEdit();
        this.intVal = new QIntValidator(this.min,this.max)
        this.number_value.setValidator(this.intVal)
        this.number_value.setFixedWidth(40)


        this.bttn = new QPushButton("Select");
        this.reset_bttn = new QPushButton("Reset")
    //    frame.setLayout(QHBoxLayout())
        this.f_layout.addWidget(this.label,1,1);
        this.f_layout.addWidget(this.slider,0,1);
        this.f_layout.addWidget(this.number_value,0,1);
        this.f_layout.addSpacing(20);
        this.f_layout.addWidget(this.bttn,0,1);
        this.f_layout.addWidget(this.reset_bttn,0,1);

    //    this..resize(400,50);

        var start_value = getSliderPosition(this.name)
        this.slider.value = start_value
        this.number_value.text = parseInt(start_value);

//        this.slider.sliderPressed.connect(this,this.startUndo);
//        this.slider.sliderReleased.connect(this,this.endUndo);

        this.slider.valueChanged.connect(this,this.slider_func);

        this.number_value.editingFinished.connect(this,this.number_func)
        this.bttn.clicked.connect(this,this.bttn_func)

        return this
    }

    createSlider.prototype.bttn_func = function(){
//        scene.beginUndoRedoAccum("slider text move")
//        updatePeg(this.name, this.slider.value)
//        scene.endUndoRedoAccum()
        selection.clearSelection();
        selection.addNodeToSelection(this.name);
    }
    createSlider.prototype.reset_bttn_func = function(){
        MessageLog.trace(this.name)
        reset_peg_function(this.name)
    }

    createSlider.prototype.startUndo = function(){
        //MessageLog.trace("pressed")
        scene.beginUndoRedoAccum("slider move");
    }
    createSlider.prototype.endUndo = function(){
        //MessageLog.trace("release")
        scene.endUndoRedoAccum();
    }

    createSlider.prototype.slider_func = function(v){
        scene.beginUndoRedoAccum("slider move");
        this.number_value.text = v;
        updatePeg(this.name, this.slider.value,this.parent.zero_check.checked)
        scene.endUndoRedoAccum();
    }
    createSlider.prototype.number_func = function(){
        v = this.number_value.text;
        this.slider.value = parseInt(v);
    }
    this.build_func();
	return this

}

QuickSlider.prototype.init_func = function(){
    this.build_func(null)
}
QuickSlider.prototype.select_call = function(){
    this.select_func()
}
QuickSlider.prototype.load_ui_state = function(){
    this.load_ui_state()
}
QuickSlider.prototype.save_ui_state = function(){
    this.save_ui_state()
}


function runQuickSlider(){
    q = new QuickSlider(0,720)
    q.show()

//    t = new QDialog();
//   s = new createSlider(t,"gotta",0,100);
//   t.show()

}