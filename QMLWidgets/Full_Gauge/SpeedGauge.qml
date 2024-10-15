import QtQuick 2.9

Item {
    id: root
    width: 300
    height: 300

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

    signal speedValueChanged(int value)

    Component.onCompleted: {
        calculateGeometry();
        updateGaugeValue(value); // Initialize the gauge display
    }

    onWidthChanged: calculateGeometry()
    onHeightChanged: calculateGeometry()

    function calculateGeometry() {
        const side = Math.min(width, height);
        gaugeRadius = (side - side * 0.20) / 2;
        tickLength = gaugeRadius * 0.1;
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

        onPaint: {
            var ctx = getContext("2d");
            var center = Qt.point(width / 2, height / 2);

            ctx.reset();
            ctx.lineCap = 'round';

            drawBackground(ctx, center);
            drawProgress(ctx, center, value);
            drawTicks(ctx, center);
            drawProgressTick(ctx, center, value);
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

            var gradient = ctx.createLinearGradient(
                center.x - gaugeRadius, center.y,
                center.x + gaugeRadius, center.y
            );

            gradient.addColorStop(0.0, "#00FF00");
            //gradient.addColorStop(0.3, primaryColor);
            gradient.addColorStop(0.4, "#FFD700");
            gradient.addColorStop(1, "#FF0000");

            ctx.beginPath();
            ctx.arc(center.x, center.y, gaugeRadius, startAngle, startAngle + (progress / (maxValue - minValue)) * fullAngle);
            ctx.strokeStyle = gradient;
            ctx.stroke();
        }

        function drawTicks(ctx, center) {
            ctx.lineWidth = tickLength / 2;
            ctx.strokeStyle = '#FFFFFF';
            ctx.beginPath();

            const tickCount = 10; // Adjust the number of ticks as needed
            
            for (let i = 0; i <= tickCount; i++) {
                const angle = startAngle + (i / tickCount) * fullAngle;
                const x1 = center.x + gaugeRadius * Math.cos(angle);
                const y1 = center.y + gaugeRadius * Math.sin(angle);
                const x2 = center.x + (gaugeRadius - tickLength) * Math.cos(angle);
                const y2 = center.y + (gaugeRadius - tickLength) * Math.sin(angle);
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
            }
            
            ctx.stroke();
        }

        function drawProgressTick(ctx, center, progress) {
            ctx.lineWidth = tickLength * 1.5;
            ctx.strokeStyle = '#FFFFFF';
            ctx.beginPath();

            const progressAngle = startAngle + (progress / (maxValue - minValue)) * fullAngle;
            const x1 = center.x + gaugeRadius * Math.cos(progressAngle);
            const y1 = center.y + gaugeRadius * Math.sin(progressAngle);
            const x2 = center.x + (gaugeRadius - tickLength * 1.5) * Math.cos(progressAngle);
            const y2 = center.y + (gaugeRadius - tickLength * 1.5) * Math.sin(progressAngle);

            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
    }

    Text {
        id: gaugeText
        anchors.centerIn: parent
        text: "0"
        font.pixelSize: 0.3 * Math.min(root.width, root.height)
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
       canvas.requestPaint(); // Request a repaint to reflect changes.
       gaugeText.text = (value).toFixed(0); // Display the current value directly.
       speedValueChanged(value); // Emit the signal with the current value.
   }

   MouseArea {
       id: dragArea
       anchors.fill: parent

       property bool isDragging: false

       onEntered: cursorShape = Qt.PointingHandCursor

       onPressed: {
           isDragging = true;
           updateDragValue(mouseX, mouseY); // Update immediately on press.
       }
       
       onReleased: isDragging = false

       onPositionChanged:
           if (isDragging) {
               updateDragValue(mouseX, mouseY); // Use formal parameters instead of injected ones.
           }

       function updateDragValue(x, y) {
           const centerX = width / 2;
           const centerY = height / 2;

           // Calculate angle from the center to the mouse position.
           const dx = x - centerX;
           const dy = centerY - y; // Note that y-axis is inverted in QML.
           const angle = Math.atan2(dy, dx);

           // Normalize angle to [startAngle .. startAngle + fullAngle]
           let normalizedAngle = angle < startAngle ? angle + Math.PI * 2 : angle;

           // Calculate the normalized value based on the angle.
           let normalizedValue = ((normalizedAngle - startAngle) / fullAngle) * (maxValue - minValue);

           // Clamp value within min and max range.
           normalizedValue = Math.max(minValue, Math.min(maxValue, normalizedValue));

           // Update the root value.
           root.value = normalizedValue;
       }
   }
}