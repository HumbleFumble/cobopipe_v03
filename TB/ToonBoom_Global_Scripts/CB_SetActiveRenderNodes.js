

function SetActiveRenderNodes(){
	MessageLog.trace("Listing Render Nodes: ");
	active_nodes = selection.selectedNodes();
	GroupTravel("Top", "WRITE", active_nodes);
}

function GroupTravel(groupName,my_type, active_nodes ) 
  {
    var nNodes = node.numberOfSubNodes(groupName);

    for( var i = 0; i < nNodes; i++)
    {
      var nodeName =  node.subNode( groupName, i );
      var type = node.type( nodeName );

       if (type == my_type ){
	SetEnable(nodeName, active_nodes);
	}

      if ( type == "GROUP" ){
       GroupTravel( nodeName, my_type, active_nodes );
      }
    }
  }

function SetEnable(cur_write){
	if (active_nodes == ""){
		MessageLog.trace("Enable " + cur_write);
		node.setEnable(cur_write, true);
		}else{
	if (active_nodes.indexOf(cur_write)>=0){
		MessageLog.trace(cur_write);
		node.setEnable(cur_write, true);
	}
	else{
		MessageLog.trace("Not selected: " +  cur_write);
		node.setEnable(cur_write, false);
	}
	}

}
