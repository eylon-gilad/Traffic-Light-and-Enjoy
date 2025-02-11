/**************************************
 *  roads.js
 *  Defines the roads array and traffic lights
 **************************************/

// We'll define a 1600×1000 canvas in HTML
const canvasWidth  = 1600;
const canvasHeight = 1000;

// For demonstration, define four horizontal roads:

// For "east" roads, we'll pick two parallel centerY’s:
const east1_Y = canvasHeight / 2 - 150;  // higher
const east2_Y = canvasHeight / 2 -  30;  // slightly lower

// For "west" roads, we'll pick two parallel centerY’s:
const west1_Y = canvasHeight / 2 +  30;  // slightly above bottom
const west2_Y = canvasHeight / 2 + 150;  // lower

const roads = [];

// East1 road: left->right
roads.push(
  new Road(
    'east1',
    { x: -50, y: east1_Y },
    { x: canvasWidth + 50, y: east1_Y }
  )
);

// East2 road: left->right
roads.push(
  new Road(
    'east2',
    { x: -50, y: east2_Y },
    { x: canvasWidth + 50, y: east2_Y }
  )
);

// West1 road: right->left
roads.push(
  new Road(
    'west1',
    { x: canvasWidth + 50, y: west1_Y },
    { x: -50, y: west1_Y }
  )
);

// West2 road: right->left
roads.push(
  new Road(
    'west2',
    { x: canvasWidth + 50, y: west2_Y },
    { x: -50, y: west2_Y }
  )
);

// Two traffic lights controlling these roads:
// lightA controls east1 & west1
// lightB controls east2 & west2
// We'll start them both green, but we'll toggle them in opposite states.
const lightA = new TrafficLight(['east1','west1'], false);
const lightB = new TrafficLight(['east2','west2'], true);

// Expose them
window.roads  = roads;
window.lightA = lightA;
window.lightB = lightB;