function test(){

var selectedNodeCount = selection.numberOfNodesSelected();
if(selectedNodeCount != 1)
  return;
var newSelection = new Object;
newSelection.node = selection.selectedNode(0);
newSelection.subobjects = selection.subSelectionForNode(newSelection.node);
MessageLog.trace(JSON.stringify(newSelection));
for(i in newSelection){
	MessageLog.trace(newSelection[i]);
	}
}

function simple_test(){
var selectedNode = selection.selectedNode(0);
if(selectedNode == "")
  return;
// Remove the selected attribute from the node
var subSelection = selection.subSelectionForNode(selectedNode);
for(var i=0; i<subSelection.length; ++i)
{
  var attribute = selection.attributeFromSubSelectionId(selectedNode, subSelection[i]);
  MessageLog.trace(JSON.stringify(attribute));

    }
}

function select(){
    var selectedNode = selection.selectedNode(0);
    if(selectedNode == "")
      return;
     MessageLog.trace(selectedNode);
    // Remove the selected attribute from the node
    var subSelection = selection.subSelectionForNode(selectedNode);
    MessageLog.trace(subSelection);
    //selection.addNodeToSelection(selectedNode);
    selection.addSubSelectionForNode(selectedNode, [4]);
}