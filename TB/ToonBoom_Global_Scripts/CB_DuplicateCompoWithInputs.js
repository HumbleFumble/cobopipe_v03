function DupWithInputs(){
	var my_node = selection.selectedNodes()[0];
	var cur_name = "Temp_Composite";
	var pos_x = node.coordX(my_node) + 10;
	var pos_y = node.coordY(my_node);
	cur_parent = node.parentNode(my_node);
	var new_composite = node.add(cur_parent,cur_name, "COMPOSITE", pos_x,pos_y, 0);

	var input_number = node.numberOfInputPorts(my_node);
	for(i=0;i<input_number; i++){
		temp_input = node.srcNode(my_node,i);
		MessageLog.trace(temp_input +" "+ i);
		node.link(temp_input,0, new_composite, i);
		
	}
}
