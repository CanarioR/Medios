import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QDialog
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QTimer

class CameraWindow(QDialog):
    """Ventana de la cámara que se abre en una ventana aparte."""
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app  # Referencia a la ventana principal
        self.setWindowTitle("Cámara")
        self.setGeometry(200, 200, 640, 480)

        # Layout
        self.layout = QVBoxLayout()
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        # Botón para tomar foto
        self.capture_button = QPushButton("Tomar Foto")
        self.capture_button.clicked.connect(self.capture_image)
        self.layout.addWidget(self.capture_button)

        self.setLayout(self.layout)

        # Variables de la cámara
        self.cap = cv2.VideoCapture(0)  # Abrir cámara
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Actualizar cada 30ms

    def update_frame(self):
        """Actualiza la vista previa de la cámara en la ventana."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_img))

    def capture_image(self):
        """Captura la imagen y la envía a la ventana principal."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # Mostrar la imagen en la ventana principal
            self.main_app.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(150,100))

            # Guardar la imagen
            #cv2.imwrite("foto.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            #print("Foto guardada como foto.jpg")

        # Cerrar la cámara
        self.close_camera()

    def close_camera(self):
        """Cierra la cámara y la ventana."""
        self.timer.stop()
        self.cap.release()
        self.close()

    def closeEvent(self, event):
        """Cerrar correctamente la cámara si se cierra la ventana."""
        self.close_camera()
        event.accept()


class MainApp(QWidget):
    """Ventana principal donde se muestra la foto."""
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Cámara con Ventana Separada")
        self.showMaximized()

        # Layout principal
        self.layout = QVBoxLayout()

        # Label para mostrar la imagen capturada
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        # Botón para abrir la cámara en otra ventana
        self.open_camera_button = QPushButton("Abrir Cámara")
        self.open_camera_button.clicked.connect(self.open_camera)
        self.layout.addWidget(self.open_camera_button)

        self.setLayout(self.layout)

    def open_camera(self):
        """Abre la cámara en una ventana separada."""
        self.camera_window = CameraWindow(self)
        self.camera_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
