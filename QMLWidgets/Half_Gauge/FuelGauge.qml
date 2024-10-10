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
    property int animationDuration: 500
    property real startAngle: 0

    property var exposedFunction: updateGaugeUnit

    Rectangle {
        anchors.fill: parent
        color: "#041F2B"
        z: -1
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true
        property real degree: 0

        onDegreeChanged: requestPaint()

        onPaint: {
            var ctx = getContext("2d")
            var center = Qt.point(width / 2, height / 2)
            var side = Math.min(width, height)
            var radius = (side - side * 0.25) / 2
            var startAngle = Math.PI * 5 / 4
            var fullAngle = Math.PI * 1 / 2 
            var progressAngle = startAngle + (degree / 270) * fullAngle

            ctx.reset()
            ctx.lineCap = 'round'

            // background arc
            ctx.lineWidth = 25
            ctx.beginPath()
            ctx.arc(center.x, center.y, radius, startAngle, startAngle + fullAngle)
            ctx.strokeStyle = '#000000'
            ctx.stroke()

            // fill arc
            ctx.lineWidth = 15
            ctx.beginPath()
            ctx.arc(center.x, center.y, radius, startAngle, progressAngle)
            ctx.strokeStyle = primaryColor
            ctx.stroke()

            // draw tick marks
            ctx.lineWidth = 5
            ctx.strokeStyle = '#FFFFFF'
            ctx.beginPath()
            var tickCount = 2; // Number of tick marks
            for (var i = 0; i < tickCount; i++) {
                var angle = startAngle + (i / (tickCount - 1)) * (progressAngle - startAngle)
                var x1 = center.x + radius * Math.cos(angle)
                var y1 = center.y + radius * Math.sin(angle)
                var x2 = center.x + (radius - 10) * Math.cos(angle)
                var y2 = center.y + (radius - 10) * Math.sin(angle)
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
            }
            ctx.stroke()
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
        // anchor this to the right of the gaugeText such that their baseline is aligned
        
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
        // antialiasing: true
        antialiasing: true
    }

    Behavior on value {
        NumberAnimation { duration: animationDuration }
    }
    
    onValueChanged: updateGaugeValue(value)

    function updateGaugeValue(value) {
        canvas.degree = value * 270
        gaugeText.text = (value * (maxValue - minValue) + minValue).toFixed(0)
    }

    function updateGaugeUnit() {
        gaugeUnit.text = unit
    }

    MouseArea {
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

            var centerX = width / 2
            var centerY = height / 2
            var dx = x - centerX
            var dy = centerY - y // Note: y-axis is inverted
            var angle = Math.atan2(dy, dx) * (180 / Math.PI)

            // Convert angle to gauge value (0 to 1)
            var gaugeValue = (angle + 135) / 270; // Adjust based on your gauge's start angle
            gaugeValue = Math.max(0, Math.min(gaugeValue, 1)); // Clamp value

            root.value = gaugeValue;
        }
    }
}
