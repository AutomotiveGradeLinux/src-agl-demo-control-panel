import QtQuick 2.9

Item {
    id: root
    width: 200
    height: 200

    property real value: 0
    property real minValue: 0
    property real maxValue: 100
    property string unit: "%"
    property string iconSource: "qrc:/Images/Images/fuel-icon.png"

    property color primaryColor: "#16CCBA"
    property color secondaryColor: "#00000000"
    property int animationDuration: 1000
    property real startAngle: Math.PI * 5 / 4
    property real fullAngle: Math.PI * 1 / 2 

    signal fuelLevelValueChanged(int value)

    Rectangle {
        anchors.fill: parent
        color: "#041F2B"
        z: -1
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true

        onPaint: {
            var ctx = getContext("2d");
            var center = Qt.point(width / 2, height / 2);
            var side = Math.min(width, height);
            var radius = (side - side * 0.25) / 2;
            var progressAngle = startAngle + (value / (maxValue - minValue)) * fullAngle;

            ctx.reset();
            ctx.lineCap = 'round';

            // Background arc
            ctx.lineWidth = 25;
            ctx.beginPath();
            ctx.arc(center.x, center.y, radius, startAngle, startAngle + fullAngle);
            ctx.strokeStyle = '#000000';
            ctx.stroke();

            // Fill arc
            ctx.lineWidth = 15;
            ctx.beginPath();
            ctx.arc(center.x, center.y, radius, startAngle, progressAngle);
            ctx.strokeStyle = primaryColor;
            ctx.stroke();

            // Draw tick marks
            ctx.lineWidth = 5;
            ctx.strokeStyle = '#FFFFFF';
            ctx.beginPath();
            const tickCount = 2; // Adjust the number of ticks as needed
            
            for (let i = 0; i <= tickCount; i++) {
                const angle = startAngle + (i / tickCount) * fullAngle;
                const x1 = center.x + radius * Math.cos(angle);
                const y1 = center.y + radius * Math.sin(angle);
                const x2 = center.x + (radius - 10) * Math.cos(angle);
                const y2 = center.y + (radius - 10) * Math.sin(angle);
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
            }
            
            ctx.stroke();

            // Draw progress tick mark
            drawProgressTick(ctx, center, progressAngle, radius);
        }

        function drawProgressTick(ctx, center, angle, radius) {
            ctx.lineWidth = 8; // Thickness of the progress tick mark
            ctx.strokeStyle = '#FFFFFF'; // Color of the progress tick mark
            ctx.beginPath();

            const x1 = center.x + radius * Math.cos(angle);
            const y1 = center.y + radius * Math.sin(angle);
            const x2 = center.x + (radius - 15) * Math.cos(angle); // Adjust length as needed
            const y2 = center.y + (radius - 15) * Math.sin(angle);

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
        id: gaugePercentage
        anchors.verticalCenter: gaugeText.verticalCenter
        anchors.left: gaugeText.right
        text: unit
        font.pixelSize: 0.15 * Math.min(root.width, root.height)
        font.bold: true
        color: "#FFFFFF"
    }

    Image {
        source: iconSource
        anchors.top: gaugeText.bottom
        anchors.horizontalCenter: gaugeText.horizontalCenter
        width: 0.15 * Math.min(root.width, root.height)
        fillMode: Image.PreserveAspectFit
        antialiasing: true
    }

    Behavior on value {
        NumberAnimation { duration: animationDuration }
    }

    onValueChanged: updateGaugeValue(value)

    function updateGaugeValue(value) {
        canvas.requestPaint(); // Request a repaint to reflect changes.
        gaugeText.text = value.toFixed(0); // Display the current value directly.
        fuelLevelValueChanged(value); // Emit the signal with the current value.
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