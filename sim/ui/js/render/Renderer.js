// js/render/Renderer.js
import { roundRect } from "../utils/utils.js";
import { SAFE_DISTANCE_PIXELS } from "../utils/config.js";

/**
 * The Renderer handles all drawing via Phaser (and sprite pooling).
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
    this.spritePool = [];
  }

  render() {
    const graphics = this.scene.graphics;
    graphics.clear();

    this.drawBackground(graphics);
    this.drawRoads(graphics);
    this.drawTrafficLights(graphics);
    this.updateCarSprites();
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
    this.roads.forEach((road) => {
      const light = (road.id === "north" || road.id === "south")
        ? road.nsTrafficLight
        : road.ewTrafficLight;
      if (!light) return;
      const progress = road.stopProgress;
      let x = road.start.x + (road.end.x - road.start.x) * progress;
      let y = road.start.y + (road.end.y - road.start.y) * progress;
      x -= road.dir.x * SAFE_DISTANCE_PIXELS;
      y -= road.dir.y * SAFE_DISTANCE_PIXELS;
      graphics.save();
      const color = light.isGreen() ? 0x2ecc71 : 0xe74c3c;
      graphics.fillStyle(color, 1);
      graphics.fillCircle(x, y, 20);
      graphics.restore();
    });
  }

  updateCarSprites() {
    // Instead of iterating over container children and hiding unused sprites,
    // we update or create a sprite for every car.
    this.roads.forEach((road) => {
      road.lanes.forEach((lane) => {
        lane.cars.forEach((car) => {
          const pX = road.start.x + (road.end.x - road.start.x) * car.positionProgress;
          const pY = road.start.y + (road.end.y - road.start.y) * car.positionProgress;
          // Offset for lane placement.
          const cx = pX + road.perp.x * car.currentLaneOffset;
          const cy = pY + road.perp.y * car.currentLaneOffset;
          let sprite = car.__sprite;
          if (!sprite) {
            sprite = this.getSpriteFromPool();
            // Choose one of the car sprites randomly.
            const spriteIndex = Math.floor(Math.random() * 8) + 1;
            sprite.setTexture(`carSprite${spriteIndex}`);
            // Enlarge the car sprite.
            sprite.setDisplaySize(96, 72);
            car.__sprite = sprite;
            this.carSpriteContainer.add(sprite);
          }
          sprite.setPosition(cx, cy);
          // Instead of rotating 180°, we determine whether to flip horizontally.
          if (Math.abs(road.angle) > Math.PI / 2) {
            sprite.setFlipX(true);
            sprite.setRotation(0);
          } else {
            sprite.setFlipX(false);
            sprite.setRotation(road.angle);
          }
          // Always mark the sprite as active and visible.
          sprite.setActive(true);
          sprite.setVisible(true);
        });
      });
    });
    // Do not hide any sprite in the container—this ensures all car sprites remain visible.
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
