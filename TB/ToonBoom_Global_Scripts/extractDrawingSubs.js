//untested from openAI
//from this prompt>
// write a script for toonboom harmony that copies a list of drawing substitutions from one drawing node to a new drawing node, and then removes the same list of drawing substitutions from the original drawing node


//Set up the variables
var drawingNode1 = Scene.get('DrawingNode1');
var drawingNode2 = Scene.get('DrawingNode2');

var drawingSubs1 = drawingNode1.getDrawingSubstitutions();

//Copy drawing substitutions from drawingNode1 to drawingNode2
for(var i=0; i<drawingSubs1.length; i++)
{
	var drawingSub = drawingSubs1[i];
	drawingNode2.addDrawingSubstitution(drawingSub);
}

//Remove drawing substitutions from drawingNode1
for(var i=0; i<drawingSubs1.length; i++)
{
	var drawingSub = drawingSubs1[i];
	drawingNode1.removeDrawingSubstitution(drawingSub);
}