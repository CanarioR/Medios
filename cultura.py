from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTextEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QWheelEvent, QKeyEvent, QImage, QIcon, QPainter, QPdfWriter, QPageSize, QFontMetrics
from PyQt6.QtCore import Qt, QSizeF, QStandardPaths
import cv2
import numpy as np
import sys, os

def ruta_recurso(rel_path):
    """Obtiene la ruta del recurso ya sea en desarrollo o empaquetado"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

class ImageViewer(QGraphicsView):
    def __init__(self, image_path):
        super().__init__()
        self.foto_capturada = False  # Inicializar el estado


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

        # Crear campos de texto fijos
        self.create_fixed_text()

        # Conectar el evento de scroll para ajustar la posición de los campos de texto
        self.verticalScrollBar().valueChanged.connect(self.adjust_text_position)

        self.save_pdf_button = QPushButton(self)
        self.save_pdf_button.setGeometry(1600, 100, 70, 70)  # Ajusta la posición
        self.save_pdf_button.setIcon(QIcon(ruta_recurso("Imagenes/Imprimir.png")))  # Usa un ícono de PDF
        self.save_pdf_button.setIconSize(self.save_pdf_button.size())  # Ajustar tamaño del ícono
        self.save_pdf_button.setStyleSheet("border: none; background: transparent;")  # Sin fondo ni bordes
        self.save_pdf_button.clicked.connect(self.generate_pdf)  # Conectar con la función
        # Solo necesitamos añadir este método al final de la clase ImageViewer
    # Botón para volver al menú
        self.back_button = QPushButton("Volver al Menú", self)
        self.back_button.setGeometry(1585, 20, 100, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #d51218;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d6676c;
            }
        """)
        self.back_button.clicked.connect(self.return_to_menu)

    def return_to_menu(self):
        """Volver al menú principal"""
        if hasattr(self, 'main_window'):
            self.main_window.show()
        self.close()

    def create_fixed_text(self):
        """Crear campos de texto fijos en la ventana."""
        # Campo de texto para el título
        self.title_edit = QTextEdit(self)
        self.title_edit.setFont(QFont("Times New Roman", 23))
        self.title_edit.setStyleSheet("background: transparent; color: black; border: 1px solid gray;")
        self.title_edit.setPlaceholderText("Título")
        self.title_edit.setGeometry(500, 500, 400, 45)  # Posición fija (x, y, ancho, alto)

        # Campo de texto para el contenido
        self.content_edit = QTextEdit(self)
        self.content_edit.setFont(QFont("Times New Roman", 16))
        self.content_edit.setStyleSheet("background: transparent; color: black; border: 1px solid gray;")
        self.content_edit.setPlaceholderText("Contenido...")
        self.content_edit.setGeometry(50, 100, 430, 550)  # Posición fija

        # Etiqueta para la segunda imagen
        self.second_image_label = QLabel(self)
        self.second_image_label.setGeometry(370, 100, 200, 200)  # Posición al lado del QTextEdit
        self.second_image_label.setStyleSheet("border: 1px solid gray;")

        # Cargar una imagen en la segunda etiqueta 
        pixmap = QPixmap(ruta_recurso("temporada/Temporada.jpeg"))  
        scaled_pixmap = pixmap.scaled(200, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.second_image_label.setPixmap(scaled_pixmap)
        self.second_image_label.setGeometry(300,500,200,350)

        # Campo de texto para el nombre del reportero
        self.reporter_edit = QTextEdit(self)
        self.reporter_edit.setFont(QFont("Times New Roman", 16))
        self.reporter_edit.setStyleSheet("background: transparent; color: black; border: 1px solid gray;")
        self.reporter_edit.setPlaceholderText("Nombre del Reportero")
        self.reporter_edit.setGeometry(50, 300, 200, 40)  # Posición fija

        # Botón para tomar foto
        self.capture_button = QPushButton(self)
        self.capture_button.setGeometry(450, 750, 200, 80)  # Posición fija
        self.capture_button.setIcon(QIcon(ruta_recurso("Imagenes/Camara.png")))  # Asegúrate de tener un ícono de cámara
        self.capture_button.setIconSize(self.capture_button.size())  # Ajustar el ícono al botón
        self.capture_button.setStyleSheet("background: rgba(255, 255, 255, 0); border-radius: 5px;")
        self.capture_button.clicked.connect(self.capture_image)
        

        # Etiqueta para mostrar la foto capturada
        self.photo_label = QLabel(self)
        self.photo_label.setGeometry(450, 700, 200, 200)  # Posición fija
        self.photo_label.setStyleSheet("background: transparent; border: 1px solid gray;")
        
        self.capture_button.raise_()

        # Limitar caracteres
        self.title_edit.textChanged.connect(lambda: self.limit_text(self.title_edit, 20))  # máximo 50 caracteres
        self.content_edit.textChanged.connect(lambda: self.limit_text(self.content_edit, 700))  # máximo 500 caracteres
        self.reporter_edit.textChanged.connect(lambda: self.limit_text(self.reporter_edit, 20))  # máximo 100 caracteres

    def limit_text(self, text_edit, max_chars):
        cursor = text_edit.textCursor()
        position = cursor.position()

        text = text_edit.toPlainText()
        if len(text) > max_chars:
            text_edit.blockSignals(True)  # Evita recursividad infinita
            text_edit.setPlainText(text[:max_chars])
            cursor.setPosition(min(position, max_chars))  # Mantiene el cursor donde estaba
            text_edit.setTextCursor(cursor)
            text_edit.blockSignals(False)

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

            # Redimensionar la imagen capturada para la ventana emergente (más grande)
            q_pixmap_large = QPixmap.fromImage(q_image).scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio)

            # Redimensionar la imagen capturada para el periódico (tamaño original o deseado)
            q_pixmap_small = QPixmap.fromImage(q_image).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)

            # Mostrar la foto capturada en una ventana emergente (más grande)
            photo_window = QLabel()
            photo_window.setPixmap(q_pixmap_large)
            photo_window.setWindowTitle("Foto Capturada")
            photo_window.setGeometry(100, 100, q_pixmap_large.width(), q_pixmap_large.height())
            photo_window.show()

            # Crear el QMessageBox y posicionarlo correctamente
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Confirmar Foto")
            msg_box.setText("¿Te gusta la foto tomada?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            # Mover el QMessageBox para que no interfiera con la ventana de la foto
            msg_box.move(photo_window.x() + photo_window.width() + 20, photo_window.y())

            # Mostrar el QMessageBox y obtener la respuesta
            respuesta = msg_box.exec()

            # Cerrar la ventana emergente después de la confirmación
            photo_window.close()

            if respuesta == QMessageBox.StandardButton.Yes:
                self.photo_label.setPixmap(q_pixmap_small)
                self.capture_button.hide()
                self.foto_capturada = True  # Nueva variable para rastrear el estado
            else:
                self.foto_capturada = False
                self.capture_image()

    def adjust_text_position(self, value):
        """Ajustar la posición de los campos de texto para que no se muevan con el scroll."""
        scroll_offset = self.verticalScrollBar().value()
        self.title_edit.move(520, 270 - scroll_offset)
        self.content_edit.move(470, 320 - scroll_offset)
        self.reporter_edit.move(950, 470 - scroll_offset)
        self.capture_button.move(950, 320 - scroll_offset)
        self.photo_label.move(950, 270 - scroll_offset)
        self.second_image_label.move(920, 520 -scroll_offset)

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
        # Validar campos obligatorios
        if not self.title_edit.toPlainText().strip():
            QMessageBox.warning(self, "Campo requerido", "Debe ingresar un título")
            return
        
        if not self.content_edit.toPlainText().strip():
            QMessageBox.warning(self, "Campo requerido", "Debe ingresar el contenido")
            return
        
        if not self.reporter_edit.toPlainText().strip():
            QMessageBox.warning(self, "Campo requerido", "Debe ingresar el nombre del reportero")
            return
        
        if not self.foto_capturada:  # Cambiamos esta validación
            QMessageBox.warning(self, "Foto requerida", "Debe tomar una foto para continuar")
            return
        """Genera un PDF con los QLabel y QTextEdit ajustados al tamaño de la página."""
        escritorio = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        ruta_pdf = os.path.join(escritorio, "Periodico.pdf")
        # Crear el PDF
        pdf_writer = QPdfWriter(ruta_pdf)
        pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A3))  # Usar un tamaño de página estándar
        pdf_writer.setResolution(300)  # Resolución de alta calidad

        # Iniciar el pintor
        painter = QPainter()
        if not painter.begin(pdf_writer):
            print("Error: No se pudo inicializar QPainter.")
            return

        # Obtener el tamaño de la imagen de fondo
        img_width = self.image_item.pixmap().width()
        img_height = self.image_item.pixmap().height()

        # Obtener el tamaño de la página del PDF
        page_width = pdf_writer.width()  # Ancho de la página en píxeles
        page_height = pdf_writer.height()  # Alto de la página en píxeles

        # Dibujar la imagen de fondo en el PDF (que abarque toda la página)
        #painter.drawPixmap(0, 0, page_width, page_height, self.image_item.pixmap().scaled(page_width, page_height))

        # Obtener la posición de la imagen de fondo en la escena
        img_pos = self.image_item.scenePos()

        # Obtener el valor del scroll vertical
        scroll_value = self.verticalScrollBar().value()

        # Dibujar los widgets (QLabel y QTextEdit) en el PDF
        self.draw_widgets_on_pdf(painter, img_width, img_height, page_width, page_height, img_pos, scroll_value)

        # Finalizar la pintura y guardar el PDF
        painter.end()
        print("PDF generado exitosamente: output.pdf")

        QMessageBox.information(self, "PDF generado", f"PDF guardado exitosamente en:\n{ruta_pdf}")

    def draw_widgets_on_pdf(self, painter, img_width, img_height, page_width, page_height, img_pos, scroll_value):
        """Dibuja los QLabel y QTextEdit en el PDF usando QPainter."""

        # Calcular el factor de escalado general
        scale_factor_x = page_width / img_width
        scale_factor_y = page_height / img_height
        scale_factor = min(scale_factor_x, scale_factor_y)

        def get_wrapped_lines(text, font, max_width):
            fm = QFontMetrics(font)
            lines = []
            
            # Primero dividir por los saltos de línea existentes (manuales)
            paragraphs = text.split('\n')
            
            for paragraph in paragraphs:
                current_line = ""
                
                for word in paragraph.split(' '):
                    # Probar si la palabra cabe en la línea actual
                    test_line = f"{current_line} {word}".strip() if current_line else word
                    
                    if fm.horizontalAdvance(test_line) <= max_width:
                        current_line = test_line
                    else:
                        if current_line:  # Si ya hay contenido en la línea, la guardamos
                            lines.append(current_line)
                            current_line = word  # Comenzamos nueva línea con la palabra actual
                        else:
                            # Manejar palabras muy largas que exceden el ancho máximo
                            # Dividir la palabra en caracteres que quepan en el ancho
                            remaining_word = word
                            while remaining_word:
                                # Encontrar el máximo número de caracteres que caben
                                chars_fit = 0
                                for i in range(1, len(remaining_word)+1):
                                    if fm.horizontalAdvance(remaining_word[:i]) <= max_width:
                                        chars_fit = i
                                    else:
                                        break
                                
                                if chars_fit > 0:
                                    lines.append(remaining_word[:chars_fit])
                                    remaining_word = remaining_word[chars_fit:]
                                else:
                                    # Por si acaso el ancho es menor que un caracter (no debería pasar)
                                    lines.append(remaining_word[0])
                                    remaining_word = remaining_word[1:]
                
                if current_line:  # Añadir la última línea del párrafo
                    lines.append(current_line)
            
            return lines

        # Dibujar el título (QTextEdit)
        title_text = self.title_edit.toPlainText()
        title_x, title_y, title_w, title_h = self.title_edit.geometry().getRect()
        title_x_scaled = int((title_x - img_pos.x() - 110))
        title_y_scaled = int((title_y - img_pos.y() - scroll_value + 510))

        # Establecer la fuente para el título
        title_font = QFont("Times New Roman", 23)
        painter.setFont(title_font)
        
        # Dibujar el texto del título (sin ajuste de línea)
        painter.drawText(title_x_scaled, title_y_scaled + title_h, title_text)

        # Dibujar el contenido (QTextEdit)
        content_text = self.content_edit.toPlainText()
        content_x, content_y, content_w, content_h = self.content_edit.geometry().getRect()
        content_x_scaled = int((content_x - img_pos.x() - 270 ))
        content_y_scaled = int((content_y - img_pos.y() - scroll_value + 650))

        # Establecer la fuente para el contenido
        content_font = QFont("Times New Roman", 16)
        painter.setFont(content_font)
        fm_content = QFontMetrics(content_font)
        
        # Obtener líneas ajustadas al ancho (400 es el ancho máximo en píxeles)
        max_content_width = 420
        wrapped_lines = get_wrapped_lines(content_text, content_font, max_content_width)

        # Dibujar el texto del contenido con saltos de línea
        line_height = fm_content.height()
        line_spacing = 35  # Espacio entre líneas (ajustar según necesidad)
        current_y = content_y_scaled
        
        for line in wrapped_lines:
            painter.drawText(content_x_scaled, current_y, line)
            current_y += line_height + line_spacing

        # Dibujar el nombre del reportero (QTextEdit)
        reporter_text = self.reporter_edit.toPlainText()
        reporter_x, reporter_y, reporter_w, reporter_h = self.reporter_edit.geometry().getRect()
        reporter_x_scaled = int((reporter_x - img_pos.x() + 650))
        reporter_y_scaled = int((reporter_y - img_pos.y() - scroll_value + 890))

        # Establecer la fuente para el nombre del reportero
        reporter_font = QFont("Times New Roman", 16)
        painter.setFont(reporter_font)

        # Dibujar el texto del reportero
        painter.drawText(reporter_x_scaled + reporter_w, reporter_y_scaled + reporter_h, reporter_text)

        # Imagen Temporada
        if self.second_image_label.pixmap():
            second_img_x, second_img_y, second_img_w, second_img_h = self.second_image_label.geometry().getRect()
            second_img_x_scaled = int((second_img_x - img_pos.x() + 720))
            second_img_y_scaled = int((second_img_y - img_pos.y() - scroll_value + 980))
            second_img_w_scaled = int(second_img_w * 2.5)
            second_img_h_scaled = int(second_img_h * 2.8)
            painter.drawPixmap(second_img_x_scaled, second_img_y_scaled, second_img_w_scaled, second_img_h_scaled, self.second_image_label.pixmap())

        # Imagen reportero
        if self.photo_label.pixmap():
            photo_x, photo_y, photo_w, photo_h = self.photo_label.geometry().getRect()
            photo_x_scaled = int((photo_x - img_pos.x() + 850))
            photo_y_scaled = int((photo_y - img_pos.y() - scroll_value + 570))
            photo_w_scaled = int(photo_w * 2.8)
            photo_h_scaled = int(photo_h * 2.5)
            painter.drawPixmap(photo_x_scaled, photo_y_scaled, photo_w_scaled, photo_h_scaled, self.photo_label.pixmap())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = ImageViewer(ruta_recurso("backgrounds/Cultura.png"))  # Cambia por la ruta real de tu imagen        
    window.showMaximized()
    sys.exit(app.exec())