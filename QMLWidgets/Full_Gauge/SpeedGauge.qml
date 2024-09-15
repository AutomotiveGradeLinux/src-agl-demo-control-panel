import QtQuick 2.9

Item {
    id: root
    width: 400
    height: 400

    property real value: 0
    property real minValue: 0
    property real maxValue: 240
    property string unit: "Km/h"

    property color primaryColor: "#16CCBA"
    property color secondaryColor: "#00000000"
    property int animationDuration: 500
    property real startAngle: Math.PI * 3 / 4
    property real fullAngle: Math.PI * 3 / 2

    property real gaugeRadius: 0
    property real tickLength: 0

    Component.onCompleted: {
        calculateGeometry();
    }

    onWidthChanged: calculateGeometry()
    onHeightChanged: calculateGeometry()

    function calculateGeometry() {
        const side = Math.min(width, height);
        gaugeRadius = (side - side * 0.20) / 2;
        tickLength = gaugeRadius * 0.05;
    }

    Rectangle {
        anchors.fill: parent
        color: "#041F2B"
        z: -1
    }

    Image {
        id: background1
        source: "./assets/Ellipse 5.svg"
        rotation: 180
        sourceSize.width: width
        sourceSize.height: width
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        scale: 1
        opacity: 0.7
        z: 0
    }

    Image {
        id: background2
        source: "./assets/Ellipse 1.svg"
        sourceSize.width: width
        sourceSize.height: width
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        scale: 1
        opacity: 0.7
        z: 1
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true
        property real degree: 0

        onDegreeChanged: requestPaint()

        onPaint: {
            var ctx = getContext("2d");
            var center = Qt.point(width / 2, height / 2);

            ctx.reset();
            ctx.lineCap = 'round';

            drawBackground(ctx, center);
            drawProgress(ctx, center, degree);
            drawTicks(ctx, center);
            drawProgressTick(ctx, center, degree);
        }

        function drawBackground(ctx, center) {
            ctx.lineWidth = gaugeRadius * 0.1;
            ctx.beginPath();
            ctx.arc(center.x, center.y, gaugeRadius, startAngle, startAngle + fullAngle);
            ctx.strokeStyle = secondaryColor;
            ctx.stroke();
        }

        function drawProgress(ctx, center, progress) {
            ctx.lineWidth = 20;
            ctx.beginPath();
            ctx.arc(center.x, center.y, gaugeRadius, startAngle, startAngle + (progress / 270) * fullAngle);
            ctx.strokeStyle = primaryColor;
            ctx.stroke();
        }

        function drawTicks(ctx, center) {
            ctx.lineWidth = tickLength * 2
            ctx.strokeStyle = '#FFFFFF'
            ctx.beginPath()
            const tickCount = 2
            for (let i = 0; i < tickCount; i++) {
                const angle = startAngle + (i / (tickCount - 1)) * fullAngle
                const x1 = center.x + gaugeRadius * Math.cos(angle)
                const y1 = center.y + gaugeRadius * Math.sin(angle)
                const x2 = center.x + (gaugeRadius - tickLength) * Math.cos(angle)
                const y2 = center.y + (gaugeRadius - tickLength) * Math.sin(angle)
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
            }
            ctx.stroke();
        }

        function drawProgressTick(ctx, center, progress) {
            
            ctx.lineWidth = tickLength * 3
            ctx.strokeStyle = '#FFFFFF'
            ctx.beginPath()
            
            const progressAngle = startAngle + (progress / 270) * fullAngle
            const x1 = center.x + gaugeRadius * Math.cos(progressAngle)
            const y1 = center.y + gaugeRadius * Math.sin(progressAngle)
            const x2 = center.x + (gaugeRadius - tickLength * 1.5) * Math.cos(progressAngle)
            const y2 = center.y + (gaugeRadius - tickLength * 1.5) * Math.sin(progressAngle)
            
            ctx.moveTo(x1, y1)
            ctx.lineTo(x2, y2)
            ctx.stroke()
        }
    }

    Text {
        id: gaugeText
        anchors.centerIn: parent
        text: "0"
        font.pixelSize: 0.2 * Math.min(root.width, root.height)
        font.bold: true
        color: "#FFFFFF"
    }

    Text {
        id: gaugeUnit
        anchors.top: gaugeText.bottom
        anchors.horizontalCenter: gaugeText.horizontalCenter
        text: unit
        font.pixelSize: 18
        font.bold: true
        color: "#FFFFFF"
    }

    Behavior on value {
        NumberAnimation { duration: animationDuration }
    }

    onValueChanged: updateGaugeValue(value)

    function updateGaugeValue(value) {
        canvas.degree = value * 270
        gaugeText.text = (value * (maxValue - minValue) + minValue).toFixed(0)
    }

    MouseArea {
        id: dragArea
        anchors.fill: parent
        hoverEnabled: true

        property bool isDragging: false
        property real initialValue: 0

        onEntered: cursorShape = Qt.PointingHandCursor
        onPressed: {
            isDragging = true
            initialValue = root.value
        }
        onReleased: isDragging = false

        onMouseXChanged: updateDragValue(mouse.x, mouse.y)
        onMouseYChanged: updateDragValue(mouse.x, mouse.y)

        function updateDragValue(x, y) {
            if (!isDragging) return

            const centerX = width / 2
            const centerY = height / 2
            const dx = x - centerX
            const dy = centerY - y // Note: y-axis is inverted
            const angle = Math.atan2(dy, dx) * (180 / Math.PI)

            // Convert angle to gauge value (0 to 1)
            let gaugeValue = (angle + 135) / 270
            gaugeValue = Math.max(0, Math.min(gaugeValue, 1)) // Clamp value

            root.value = gaugeValue
        }
    }
}
