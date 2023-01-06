//SCRIPT START
function Find_And_Replace()
{
d = new Dialog;
d.title = "Find and Replace";
         
var group = new GroupBox;
   
var findLE = new LineEdit;
var replaceLE = new LineEdit;
findLE.label = "Find:";
replaceLE.label = "Replace:";

group.add(findLE );
d.addSpace(1);
group.add( replaceLE);
d.add(group);

var rc = d.exec();

if (!rc)
{
   return;
}
   
var _find = findLE.text;
var _replace = replaceLE.text;
      
var n = selection.numberOfNodesSelected();

for (i = 0; i < n; ++i)
{
   var selNode = selection.selectedNode(i);
   var nodeNamePath= selNode.split("/");
   var nodeName = nodeNamePath[nodeNamePath.length - 1];
   
   var newNodeName = nodeName.replace(_find, _replace);
   var columnId = node.linkedColumn(selNode,"DRAWING.ELEMENT");
   var elementKey = column.getElementIdOfDrawing(columnId);
   var newColumnName = newNodeName;
   
   node.rename(selNode, newNodeName);
   column.rename(columnId, newNodeName);
   element.renameById( elementKey, newNodeName);
   
   //System.println(newNodeName );
}      
}
//SCRIPT END