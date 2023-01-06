//TESTING
function GetInfo(){
var project_name = System.getenv("BOM_PROJECT_NAME");
var user = System.getenv("BOM_USER");
if(project_name){
	MessageLog.trace(project_name);
	
//	PickProject();
	}else{
	PickProject();
	}
if(user){
	MessageLog.trace(user);
	}else{
	PickUser();
	}

};


function PickProject(){
var myDialog = new Dialog();
myDialog.title = "Pick Project";
myDialog.width = 300;
var userInput = new ComboBox();
userInput.minWidth = 300;
userInput.label = "Pick Current Project";
userInput.editable = true;
userInput.itemList = ["Boerste_Season2", "MiasMagic2"];
myDialog.add( userInput );
if ( myDialog.exec() ){
  MessageLog.trace(userInput.currentItem)}
else{
	MessageLog.trace("Cancelled");
	};
}

function PickUser(){
var myDialog = new Dialog();
myDialog.title = "Pick User";
myDialog.width = 300;
var userInput = new ComboBox();
userInput.minWidth = 300;
userInput.label = "Pick Current User";
userInput.editable = true;
userInput.itemList = ["Christian", "Amalie"];
myDialog.add( userInput );
if ( myDialog.exec() ){
  MessageLog.trace(userInput.currentItem)}
else{
	MessageLog.trace("Cancelled");
	};
}