function Arrow(graphicsObj, base, angle, length){
    this.g = graphicsObj;

    this.basePoint = new Phaser.Geom.Point(base.x, base.y);
    this.line = new Phaser.Geom.Line(base.x, base.y, base.x, base.y-length);
    this.triangle = new Phaser.Geom.Triangle.BuildEquilateral(base.x, base.y+length, length/3);

    this.updateLinePoints();
    this.rotate(angle);
}


Arrow.prototype.getLength = function(){
    return Math.sqrt((this.head.x - this.base.x) * (this.head.x - this.base.x) + (this.head.y - this.base.y) * (this.head.y - this.base.y));
    //return Phaser.Geom.Line.Length(this.line);
}


Arrow.prototype.getAngle = function(){
    return Phaser.Geom.Line.Angle(this.line);
}


Arrow.prototype.updateLinePoints = function(){
    this.base = this.line.getPointA();
    this.head = this.line.getPointB();
    this.basePoint.x = this.base.x;
    this.basePoint.y = this.base.y;
}


Arrow.prototype.rotateLine = function(angle){
    Phaser.Geom.Line.RotateAroundXY(this.line, this.base.x, this.base.y, angle);
    this.updateLinePoints();
    Phaser.Geom.Triangle.CenterOn(this.triangle, this.head.x, this.head.y);
}

Arrow.prototype.moveBaseTo = function(x, y){
    Phaser.Geom.Line.Offset(this.line, x-this.base.x, y-this.base.y);
    this.updateLinePoints();
    Phaser.Geom.Triangle.CenterOn(this.triangle, this.head.x, this.head.y);
}

Arrow.prototype.offset = function(x, y){
    Phaser.Geom.Line.Offset(this.line, x, y);
    this.updateLinePoints();
    Phaser.Geom.Triangle.CenterOn(this.triangle, this.head.x, this.head.y);
}

Arrow.prototype.rotateTriangle = function(angle){
    Phaser.Geom.Triangle.RotateAroundXY(this.triangle, this.head.x, this.head.y, angle);
}


Arrow.prototype.rotate = function(angle){
    this.rotateLine(angle);
    this.rotateTriangle(angle);
}


Arrow.prototype.setAngle = function(angle){
    this.rotate(angle-Phaser.Geom.Line.Angle(this.line))
}


Arrow.prototype.setLength = function(len){
    var newHead = {
        x: this.base.x + len*Math.cos(this.getAngle()),
        y: this.base.y + len*Math.sin(this.getAngle())
    }

    this.line = new Phaser.Geom.Line(this.base.x, this.base.y, newHead.x, newHead.y)

    this.updateLinePoints();
    Phaser.Geom.Triangle.CenterOn(this.triangle, this.head.x, this.head.y);
}

Arrow.prototype.stroke = function(){
    if (this.getLength() < 1){
        this.g.fillPointShape(this.basePoint, 5)
    } else{
        this.g.strokeLineShape(this.line);   
        this.g.fillTriangleShape(this.triangle);
    }


}