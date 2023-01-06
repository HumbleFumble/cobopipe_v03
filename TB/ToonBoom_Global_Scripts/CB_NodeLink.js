function NodeLink(){

var cur_nodes = selection.selectedNodes();
if(cur_nodes.length > 1){ 
	var in_node = cur_nodes[0];
	var out_node = cur_nodes[1];
	var myDialog = new Dialog();
	myDialog.title = "Pick OutGoing Node Dialog";
	var my_text = new Label();
	my_text.text = "Pick the 'FROM' node :"
	myDialog.add( my_text ); 
	var mycheck = new CheckBox();
	mycheck.text = "Reverse";
	myDialog.add(mycheck);
	myDialog.okButtonText = "From: " + in_node;
	myDialog.cancelButtonText = "Cancel";

	if(myDialog.exec()){
		
		if (mycheck.checked){
			node.link(out_node, 0, in_node,0);
			
		}else{
			node.link(in_node, 0, out_node,0);
		}
	}
}
}
