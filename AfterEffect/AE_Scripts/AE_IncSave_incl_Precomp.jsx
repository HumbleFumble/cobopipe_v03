#target.aftereffects
//saves a project in the same folder, with a added version number.
//the name should be in in the format of "Name_V01_User.aep"

function AE_Incremental_Save(){
	if(app.project.file){

		//app.project.save();
		//var target = new File("C:/Users/Alan/Desktop/Noel Kealahan/copy.aep")

		var project_folder = new File (app.project.file.path);
		//var project_folder = String(project_filepath).lastIndexOf('/');
		var filename = String(app.project.file.name);
		
		//var folder_path = String(project_filepath).split(filename)[0];
		//alert(folder_path);
		if(filename.search("_Precomp") >=0){
			var ask_user_for_overwrite = "";
			new_filename = filename.split("_Precomp")[0] + "_Comp_V001.aep";
			}else{
				name_parts = filename.split("_v");
				if(name_parts.length <2){
					name_parts = filename.split("_V");
					}
				version = name_parts[1].split(".")[0];
				version = parseInt(version, 10) + 1;		

				new_filename = name_parts[0] + "_V" + Pad(version,3) +".aep";
			}
		new_file_path = String(project_folder) +"/" + new_filename;
		new_file = new File(new_file_path);
			
		if (new_file.exists){
			var my_confirm = confirm(new_filename +" exists, do you want overwrite file?", true, "OverWrite Comp?");
			if(my_confirm){
				app.project.save(new_file);
				}
			}else{
				app.project.save(new_file);
				}
	}else{
		alert("Save project one place first!");
		}
}

function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

AE_Incremental_Save();
