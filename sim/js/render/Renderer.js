// js/render/Renderer.js
import { roundRect } from "../utils/utils.js";
import { SAFE_DISTANCE_PIXELS } from "../utils/config.js";

/**
 * The Renderer handles all drawing via Phaser (and sprite pooling).
 * It now also draws labels for each lane.
 */
export default class Renderer {
  /**
   * @param {Phaser.Scene} scene - The current Phaser scene.
   * @param {Array} roads - The roads to render.
   */
  constructor(scene, roads) {
    this.scene = scene;
    this.roads = roads;
    this.carSpriteContainer = scene.add.container(0, 0);
    // Set the car sprite container depth high so cars are always above text.
    this.carSpriteContainer.setDepth(100);
    this.spritePool = [];
  }

  render() {
    const graphics = this.scene.graphics;
    graphics.clear();

    this.drawBackground(graphics);
    this.drawRoads(graphics);
    this.drawTrafficLights(graphics);
    this.updateCarSprites();
    this.drawLabels();
  }

  drawBackground(graphics) {
    graphics.fillStyle(0xecf0f1, 1);
    graphics.fillRect(0, 0, this.scene.cameras.main.width, this.scene.cameras.main.height);
  }

  drawRoads(graphics) {
    this.roads.forEach((road) => {
      if (road.isVertical()) {
        graphics.fillStyle(0x7f8c8d, 1);
        const xCenter = road.cachedCenterX;
        graphics.fillRect(xCenter - road.roadWidth / 2, 0, road.roadWidth, this.scene.cameras.main.height);
        graphics.lineStyle(4, 0xffffff, 0.7);  // thicker lane markings for larger roads
        for (let i = 1; i < road.laneCount; i++) {
          const xOffset = -road.roadWidth / 2 + i * (road.roadWidth / road.laneCount);
          const startX = xCenter + xOffset;
          const startY = 0;
          const endX = startX;
          const endY = this.scene.cameras.main.height;
          this.drawDashedLine(graphics, startX, startY, endX, endY);
        }
      } else {
        graphics.fillStyle(0x7f8c8d, 1);
        const yCenter = road.cachedCenterY;
        graphics.fillRect(0, yCenter - road.roadWidth / 2, this.scene.cameras.main.width, road.roadWidth);
        graphics.lineStyle(4, 0xffffff, 0.7);
        for (let i = 1; i < road.laneCount; i++) {
          const yOffset = -road.roadWidth / 2 + i * (road.roadWidth / road.laneCount);
          const startX = 0;
          const startY = yCenter + yOffset;
          const endX = this.scene.cameras.main.width;
          const endY = startY;
          this.drawDashedLine(graphics, startX, startY, endX, endY);
        }
      }
    });

    // Draw enlarged intersection (using a rounded rectangle).
    const centerX = this.scene.centerX;
    const centerY = this.scene.centerY;
    const roadWidth = this.roads[0].roadWidth;
    const roadWidthWithBuffer = roadWidth * 1.075;
    const intersecX = centerX - roadWidthWithBuffer;
    const intersecY = centerY - roadWidthWithBuffer;
    const intersectionWidth = roadWidthWithBuffer * 2;
    const intersectionHeight = roadWidthWithBuffer * 2;
    graphics.fillStyle(0x555555, 1);
    roundRect(graphics, intersecX, intersecY, intersectionWidth, intersectionHeight, 20);
  }

  drawDashedLine(graphics, x1, y1, x2, y2, dashLength = 20, gapLength = 10) {
    const line = new Phaser.Geom.Line(x1, y1, x2, y2);
    const length = Phaser.Geom.Line.Length(line);
    let currentLength = 0;
    while (currentLength < length) {
      const startPoint = Phaser.Geom.Line.GetPoint(line, currentLength / length);
      currentLength += dashLength;
      if (currentLength > length) currentLength = length;
      const endPoint = Phaser.Geom.Line.GetPoint(line, currentLength / length);
      graphics.strokeLineShape(new Phaser.Geom.Line(startPoint.x, startPoint.y, endPoint.x, endPoint.y));
      currentLength += gapLength;
    }
  }

  drawTrafficLights(graphics) {
    // For each road, draw a traffic light for each lane.
    this.roads.forEach((road) => {
      const trafficState = road.nsTrafficLight ? road.nsTrafficLight : road.ewTrafficLight;
      road.lanes.forEach((lane) => {
        const baseX = road.start.x + (road.end.x - road.start.x) * road.stopProgress;
        const baseY = road.start.y + (road.end.y - road.start.y) * road.stopProgress;
        const laneX = baseX + road.perp.x * lane.offset;
        const laneY = baseY + road.perp.y * lane.offset;
        const lightX = laneX - road.dir.x * 50;
        const lightY = laneY - road.dir.y * 50;
        graphics.save();
        const color = trafficState.isGreen() ? 0x2ecc71 : 0xe74c3c;
        graphics.fillStyle(color, 1);
        graphics.fillCircle(lightX, lightY, 20);
        graphics.restore();
      });
    });
  }

  updateCarSprites() {
    this.roads.forEach((road) => {
      road.lanes.forEach((lane) => {
        lane.cars.forEach((car) => {
          const pX = road.start.x + (road.end.x - road.start.x) * car.positionProgress;
          const pY = road.start.y + (road.end.y - road.start.y) * car.positionProgress;
          const cx = pX + road.perp.x * car.currentLaneOffset;
          const cy = pY + road.perp.y * car.currentLaneOffset;
          let sprite = car.__sprite;
          if (!sprite) {
            sprite = this.getSpriteFromPool();
            const spriteIndex = Math.floor(Math.random() * 7) + 1;
            sprite.setTexture(`carSprite${spriteIndex}`);
            sprite.setDisplaySize(96, 72);
            car.__sprite = sprite;
            this.carSpriteContainer.add(sprite);
          }
          sprite.setPosition(cx, cy);
          if (Math.abs(road.angle) > Math.PI / 2) {
            sprite.setFlipX(true);
            sprite.setRotation(0);
          } else {
            sprite.setFlipX(false);
            sprite.setRotation(road.angle);
          }
          sprite.setActive(true);
          sprite.setVisible(true);
        });
      });
    });
  }

  drawLabels() {
    // For each lane, draw its label below the cars.
    // We ensure that lane labels have a lower depth so that cars are drawn above them.
    this.roads.forEach((road) => {
      road.lanes.forEach((lane) => {
        // Base position: near the stop line, then offset downward.
        const t = road.stopProgress - 0.2;  // Slightly before the stop line.
        const baseX = road.start.x + (road.end.x - road.start.x) * t;
        const baseY = road.start.y + (road.end.y - road.start.y) * t;
        let labelX = baseX + road.perp.x * lane.offset;
        let labelY = baseY + road.perp.y * lane.offset;
        // Offset the label so that it appears behind (i.e. lower depth than) the cars.
        if (road.isVertical()) {
          if (!lane.label) {
            lane.label = this.scene.add.text(labelX, labelY, lane.id, {
              font: "20px Arial",
              fill: "#fff",
              align: "center"
            });
            lane.label.setOrigin(0.5);
            // Rotate text so that it appears vertical.
            lane.label.setAngle(90);
            lane.label.setDepth(0); // lower than car sprites
          } else {
            lane.label.setPosition(labelX, labelY);
          }
        } else {
          if (!lane.label) {
            lane.label = this.scene.add.text(labelX, labelY, lane.id, {
              font: "20px Arial",
              fill: "#fff",
              align: "center"
            });
            lane.label.setOrigin(0.5);
            lane.label.setDepth(0); // lower than car sprites
          } else {
            lane.label.setPosition(labelX, labelY);
          }
        }
      });
    });
  }

  /**
   * Retrieves a sprite from the pool or creates a new one.
   * @returns {Phaser.GameObjects.Sprite}
   */
  getSpriteFromPool() {
    if (this.spritePool.length > 0) {
      return this.spritePool.pop();
    } else {
      return this.scene.add.sprite(0, 0, "carSprite");
    }
  }
}
