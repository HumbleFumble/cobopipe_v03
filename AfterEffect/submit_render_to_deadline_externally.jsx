#target.aftereffects;
#include "AE_Scripts/submit_render_to_deadline.jsx"

function Main(file_path){
	app.open(new File(file_path));
	Run();
}