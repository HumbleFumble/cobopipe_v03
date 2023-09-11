// Define a function for aligning nodes to the left-most node
void alignNodesToLeft()
{
  // Get a list of all the selected nodes
  QList<QGraphicsItem *> selectedNodes = scene->selectedItems();

  // Find the left-most node
  QGraphicsItem *leftMostNode;
  int leftMostX = INT_MAX; // Initialize to maximum possible value
  for (auto node : selectedNodes)
  {
    if (node->x() < leftMostX)
    {
      leftMostNode = node;
      leftMostX = node->x();
    }
  }

  // Move each selected node to the x-coordinate of the left-most node
  for (auto node : selectedNodes)
  {
    node->setX(leftMostNode->x());
  }
}