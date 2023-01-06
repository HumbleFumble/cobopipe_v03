/* 

ToonBoom Harmony script by Liza Desya

Script that aligns nodes horizontally. 
This is useful when organizing the node view whilst rigging.
The script will always align with the oldest node within the selection (ToonBoom sorts it's nodes by order of creation, not by type or order of selection)

Find more ToonBoom scripts at https://gumroad.com/lizadesya
Contact me through LizaDesya.com
To see more of my work, follow @LizaDesya on Instagram and Twitter

*/

function LIZA_alignNodesHorizontally(){

	var exeDialog = new private_exeDialog();

	scene.beginUndoRedoAccum("LIZA_alignNodesHorizontally");

	exeDialog.main();
	  
	scene.endUndoRedoAccum("LIZA_alignNodesHorizontally");
	
  }

function private_exeDialog(){
 
	this.main = function(){
        if(selection.numberOfNodesSelected() > 0)
        {
       var  selectionNodes = selection.selectedNodes(0);
       var firstNodeY = node.coordY(selectionNodes[selectionNodes.length - 1])
      
       for (i=0;i < selectionNodes.length; i++)
            {
            nodeX = node.coordX(selectionNodes[i]);
            node.setCoord(selectionNodes[i], nodeX, firstNodeY);
            }
        }
    }
}
   



	







