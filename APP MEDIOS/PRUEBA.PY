from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTextEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QWheelEvent, QKeyEvent, QImage, QIcon, QPainter, QPdfWriter
from PyQt6.QtCore import Qt, QTimer
import numpy as np


class ImageViewer(QGraphicsView):
    def __init__(self, image_path):
        super().__init__()

        # Crear la escena
        self.scene = QGraphicsScene(self)

        # Cargar la imagen de fondo
        self.image_item = QGraphicsPixmapItem(QPixmap(image_path))
        self.scene.addItem(self.image_item)

        # Configurar la vista
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints().Antialiasing)

        # Configuración de zoom inicial
        self.scale_factor = 0.5  # Zoom inicial más pequeño
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.scale(self.scale_factor, self.scale_factor)  # Aplicar el zoom inicial

        # Ajustar la vista para que empiece un poco más abajo
        self.centerOn(self.image_item)
        self.verticalScrollBar().setValue(self.verticalScrollBar().minimum() + 100)

        # Crear campos de texto fijos (inicialmente ocultos)
        self.create_fixed_text()

        # Conectar el evento de scroll para ajustar la posición de los campos de texto
        self.verticalScrollBar().valueChanged.connect(self.adjust_text_position)

        # Botón para guardar como PDF
        self.save_pdf_button = QPushButton(self)
        self.save_pdf_button.setGeometry(600, 750, 50, 50)  # Ajusta la posición
        self.save_pdf_button.setIcon(QIcon("pdf_icon.png"))  # Usa un ícono de PDF
        self.save_pdf_button.setIconSize(self.save_pdf_button.size())  # Ajustar tamaño del ícono
        self.save_pdf_button.setStyleSheet("border: none; background: transparent;")  # Sin fondo ni bordes
        self.save_pdf_button.clicked.connect(self.generate_pdf)  # Conectar con la función
        self.save_pdf_button.setVisible(False)  # Ocultar inicialmente

        # Esperar a que la ventana se renderice antes de iniciar la guía del usuario
        QTimer.singleShot(500, self.guide_user)  # Espera 500ms antes de iniciar los diálogos

    def create_fixed_text(self):
        """Crear campos de texto fijos en la ventana (inicialmente ocultos)."""
        # Campo de texto para el título
        self.title_edit = QTextEdit(self)
        self.title_edit.setFont(QFont("Times New Roman", 20))
        self.title_edit.setStyleSheet("background: transparent; color: black; border: 1px solid gray;")
        self.title_edit.setPlaceholderText("Título")
        self.title_edit.setGeometry(500, 500, 400, 40)  # Posición fija (x, y, ancho, alto)
        self.title_edit.setVisible(False)  # Ocultar inicialmente

        # Campo de texto para el contenido
        self.content_edit = QTextEdit(self)
        self.content_edit.setFont(QFont("Times New Roman", 10))
        self.content_edit.setStyleSheet("background: transparent; color: black; border: 1px solid gray;")
        self.content_edit.setPlaceholderText("Contenido...")
        self.content_edit.setGeometry(50, 100, 450, 200)  # Posición fija
        self.content_edit.setVisible(False)  # Ocultar inicialmente

        # Etiqueta para la segunda imagen
        self.second_image_label = QLabel(self)
        self.second_image_label.setGeometry(370, 100, 200, 200)  # Posición al lado del QTextEdit
        self.second_image_label.setStyleSheet("border: 1px solid gray;")
        self.second_image_label.setVisible(False)  # Ocultar inicialmente

        # Cargar una imagen en la segunda etiqueta (reemplaza 'imagen2.png' con tu imagen real)
        pixmap = QPixmap("Prueba2.jpeg")  # Asegúrate de que la imagen esté en la misma carpeta o pon la ruta correcta
        scaled_pixmap = pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio)
        self.second_image_label.setPixmap(scaled_pixmap)
        self.second_image_label.setGeometry(300, 500, 700, 160)

        # Campo de texto para el nombre del reportero
        self.reporter_edit = QTextEdit(self)
        self.reporter_edit.setFont(QFont("Times New Roman", 12))
        self.reporter_edit.setStyleSheet("background: transparent; color: black; border: 1px solid gray;")
        self.reporter_edit.setPlaceholderText("Nombre del Reportero")
        self.reporter_edit.setGeometry(50, 300, 200, 40)  # Posición fija
        self.reporter_edit.setVisible(False)  # Ocultar inicialmente

        # Botón para tomar foto
        self.capture_button = QPushButton(self)
        self.capture_button.setGeometry(450, 750, 200, 80)  # Posición fija
        self.capture_button.setIcon(QIcon("Camara.png"))  # Asegúrate de tener un ícono de cámara
        self.capture_button.setIconSize(self.capture_button.size())  # Ajustar el ícono al botón
        self.capture_button.setStyleSheet("background: rgba(255, 255, 255, 0); border-radius: 5px;")
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setVisible(False)  # Ocultar inicialmente

        # Etiqueta para mostrar la foto capturada
        self.photo_label = QLabel(self)
        self.photo_label.setGeometry(450, 700, 200, 200)  # Posición fija
        self.photo_label.setStyleSheet("background: transparent; border: 1px solid gray;")
        self.photo_label.setVisible(False)  # Ocultar inicialmente

    def guide_user(self):
        """Guía al usuario paso a paso con retrasos para evitar que se encadenen los MessageBox."""
        QMessageBox.information(self, "Paso 1: Título", "Primero tienes que escoger el título de tu noticia.")
        self.title_edit.setVisible(True)  # Mostrar el campo de texto del título

        QTimer.singleShot(500, self.step_2)  # Espera antes del siguiente paso

    def step_2(self):
        QMessageBox.information(self, "Paso 2: Contenido", "Ahora escribe el contenido de tu noticia.")
        self.content_edit.setVisible(True)

        QTimer.singleShot(500, self.step_3)

    def step_3(self):
        QMessageBox.information(self, "Paso 3: Reportero", "Ingresa tu nombre como reportero.")
        self.reporter_edit.setVisible(True)

        QTimer.singleShot(500, self.step_4)

    def step_4(self):
        QMessageBox.information(self, "Paso 4: Foto", "Ahora toma una foto para acompañar tu noticia.")
        self.capture_button.setVisible(True)

        QTimer.singleShot(500, self.step_5)

    def step_5(self):
        QMessageBox.information(self, "Paso 5: Finalizar", "¡Ya casi terminamos! Revisa tu noticia y guárdala como PDF cuando estés listo.")
        self.save_pdf_button.setVisible(True)

    def capture_image(self):
        """Abrir la cámara en otra ventana y capturar una imagen cuando se presione un botón."""
        cap = cv2.VideoCapture(0)  # Abre la cámara

        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: No se pudo capturar el frame.")
                break

            cv2.imshow("Presiona ESPACIO para tomar la foto", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Presiona ESPACIO para capturar
                break

        cap.release()
        cv2.destroyAllWindows()

        if ret:
            # Convertir la imagen de OpenCV a formato compatible con Qt
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir BGR a RGB
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

            # Redimensionar la imagen capturada
            q_pixmap = QPixmap.fromImage(q_image).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)

            # Si `photo_label` no es un QLabel, cambiarlo
            if not hasattr(self, 'photo_label') or not isinstance(self.photo_label, QLabel):
                self.photo_label = QLabel(self)
                self.photo_label.setGeometry(450, 500, 200, 200)  # Ajustar la posición
                self.photo_label.setStyleSheet("border: 1px solid gray;")

            respuesta = QMessageBox.question(self, "Confirmar Foto",
                                             "¿Te gusta la foto tomada?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if respuesta == QMessageBox.StandardButton.Yes:
                # Si la foto es aceptada, mostrarla y ocultar el botón
                self.photo_label.setPixmap(q_pixmap)
                self.photo_label.setVisible(True)  # Mostrar la etiqueta de la foto
                self.capture_button.setVisible(False)  # Ocultar el botón de tomar foto
            else:
                # Si la foto no es aceptada, permitir tomar otra
                self.capture_image()

    def adjust_text_position(self, value):
        """Ajustar la posición de los campos de texto para que no se muevan con el scroll."""
        scroll_offset = self.verticalScrollBar().value()
        self.title_edit.move(700, 500 - scroll_offset)
        self.content_edit.move(670, 540 - scroll_offset)
        self.reporter_edit.move(450, 700 - scroll_offset)
        self.capture_button.move(450, 550 - scroll_offset)
        self.photo_label.move(450, 500 - scroll_offset)
        self.second_image_label.move(450, 760 - scroll_offset)

    def wheelEvent(self, event: QWheelEvent):
        """Permite hacer zoom solo con Ctrl + rueda, y mover el scroll con la rueda sola."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 0.8

            if event.angleDelta().y() > 0 and self.scale_factor < self.max_zoom:
                self.scale(zoom_in_factor, zoom_in_factor)
                self.scale_factor *= zoom_in_factor
            elif event.angleDelta().y() < 0 and self.scale_factor > self.min_zoom:
                self.scale(zoom_out_factor, zoom_out_factor)
                self.scale_factor *= zoom_out_factor

            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Activa el modo de arrastre solo cuando se presiona Ctrl."""
        if event.key() == Qt.Key.Key_Control:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def keyReleaseEvent(self, event: QKeyEvent):
        """Desactiva el modo de arrastre cuando se suelta Ctrl."""
        if event.key() == Qt.Key.Key_Control:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def generate_pdf(self):
        """Genera un PDF con los QLabel y QTextEdit, pero sin la imagen de fondo."""
        # Obtener el tamaño de la imagen de fondo para usarlo como referencia en el PDF
        img_width = self.image_item.pixmap().width()
        img_height = self.image_item.pixmap().height()

        # Crear el PDF con el tamaño proporcional al de la imagen
        pdf_writer = QPdfWriter("output.pdf")
        pdf_writer.setPageSizeMM((img_width / 10, img_height / 10))  # Escala para ajustarse mejor
        pdf_writer.setResolution(300)  # Resolución de alta calidad

        # Iniciar el pintor
        painter = QPainter(pdf_writer)

        # Dibujar los QLabel y QTextEdit en el PDF
        self.draw_widgets_on_pdf(painter)

        # Finalizar la pintura y guardar el PDF
        painter.end()
        print("PDF generado exitosamente: output.pdf")

    def draw_widgets_on_pdf(self, painter):
        """Dibuja los QLabel y QTextEdit en el PDF usando QPainter."""
        # Fuente para los textos
        font = QFont("Times New Roman", 12)
        painter.setFont(font)

        # Dibujar los QTextEdit
        for widget in [self.title_edit, self.content_edit, self.reporter_edit]:
            text = widget.toPlainText()
            x, y, w, h = widget.geometry().getRect()
            painter.drawText(x, y + h, text)  # Dibuja el texto en la posición correcta

        # Dibujar los QLabel (si tienen imágenes)
        for label in [self.photo_label, self.second_image_label]:
            if label.pixmap():
                x, y, w, h = label.geometry().getRect()
                painter.drawPixmap(x, y, w, h, label.pixmap())  # Dibuja la imagen


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = ImageViewer("Urbano.png")  # Cambia por la ruta real de tu imagen
    window.showMaximized()

    sys.exit(app.exec())