#target.aftereffects;
#include "AE_Scripts/includes/deadline_submit.jsx"

function Main(file_path){
	app.open(new File(file_path));
	Run();
}