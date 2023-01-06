include("CB_ToonBoom_Include_SetRenderNode.js");
include("CB_GetInfo.js")
function submitSceneToRoyalRender(){
//Set render info on nodes

project_settings = GetProjectSettings();
var project_name = GetProject();
var user_name = GetUser();
var output_format = project_settings.tb_output_format;
var leading_zeros = project_settings.tb_number_padding;
PrepareForRender(output_format,leading_zeros);
//Get scene path
var cur_full_path = scene.currentProjectPath();
var cur_scene = scene.currentVersionName()+ ".xstage";
var final_path = cur_full_path + "/" + cur_scene;
MessageLog.trace("Submitting: " + final_path);
scene.saveAll();

p1 = new Process2("python", System.getenv("BOM_PIPE_PATH")+"\\ToonBoom\\ToonBoom_RR_Submit_Call.py", final_path,"False",project_name,user_name);

p1.launchAndDetach();
MessageBox.information("Submitted " + final_path + " to RoyalRender");
}
