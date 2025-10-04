import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import "qrc:/qml"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 950
    height: 700

    Image {
        anchors.fill: parent
        source: "../resources/pixelate_cloud.png"
        fillMode: Image.PreserveAspectCrop
    }

    StackLayout {
        id: stackLayout
        Layout.preferredWidth: mainWindow.width
        Layout.preferredHeight: mainWindow.height
        currentIndex: 0

        Item {
            LoadingPage {
                onStartClicked: stackLayout.currentIndex = 1
            }
        }
        
        Item {
            WeatherPage {
                onBackClicked: stackLayout.currentIndex = 0
            }
        }
    }
}
