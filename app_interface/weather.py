"""Module for initializing the application."""

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

import app_interface.weather_rc  # pylint: disable= [unused-import]
from backend import weather_bridge

CURRENT_DIRECTORY = Path(__file__).resolve().parent

class WeatherApplication(QGuiApplication):
    """Weather app entry point."""

    def __init__(self) -> None:
        """Initialize weather application."""
        super().__init__()
        self._engine = QQmlApplicationEngine()
        self.setApplicationDisplayName("Will It Rain On My Parade")

    @property
    def engine(self) -> QQmlApplicationEngine:
        """Get the QML application engine."""
        return self._engine
    
    def set_components(self) -> None:
        """Set up the main application components."""
        self.weather_bridge = weather_bridge.WeatherBridge()

    def set_up_image_format(self) -> None:
        """Set up the image format for the application."""

    def set_up_qml_contexts(self) -> None:
        """Set up the QML context properties."""
        self.engine.rootContext().setContextProperty(
            "weather_components", self.weather_bridge
        )

    def set_window_icon(self) -> None:
        """Set the window icon for the application."""
        self.setWindowIcon(QIcon(str(CURRENT_DIRECTORY.parent / "resources" / "dreamy_cloud.ico")))

    def set_up_signals(self) -> None:
        """Set up the application signals."""
        self.aboutToQuit.connect(self._on_quit)

    def _on_quit(self) -> None:
        """Clean up resources before quitting."""
        del self._engine

    def start_engine(self) -> None:
        """Start the QML engine."""
        self.engine.load(QUrl.fromLocalFile(str(CURRENT_DIRECTORY / "weather.qml")))

    def verify(self) -> None:
        """Verify the application state."""
        if not self._engine.rootObjects():
            sys.exit(-1)

    def start_application(self) -> int:
        """Start the main application."""
        self.set_components()
        self.set_up_image_format()
        self.set_up_qml_contexts()
        self.set_up_signals()
        self.set_window_icon()
        self.start_engine()
        return sys.exit(self.exec())


def main() -> None:
    """Start the main entry point for the application."""
    app = WeatherApplication()
    app.start_application()


if __name__ == "__main__":
    main()