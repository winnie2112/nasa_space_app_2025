import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

// Make the button at center
Item {
    signal startClicked()

    Button {
        anchors.left: parent.left
        anchors.leftMargin: 350
        anchors.top: parent.top
        anchors.topMargin: 230
        width: 150
        height: 120

        contentItem: Text {
            anchors.left: parent.left
            anchors.leftMargin: 45
            anchors.top: parent.top
            anchors.topMargin: 65

            text: qsTr("Let's Go!")
            font.family: "../resources/m5x7.ttf"
            font.bold: true
            font.pixelSize: 15
            color: "#8daefc"
        }
        
        onClicked: {
            startClicked()
            weather_components.update_current_status()
        }

        background: Image {
            anchors.fill: parent
            anchors.centerIn: parent
            source: "../resources/refresh_button.png"
            fillMode: Image.PreserveAspectFit
        }
    }
}