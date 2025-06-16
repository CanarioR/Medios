from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                            QVBoxLayout, QWidget, QLabel, QMessageBox, QGridLayout)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QGuiApplication, QPainter, QBrush, QColor, QPalette
from PyQt6.QtCore import Qt, QSize
import sys, os
from primeraPlana import ImageViewer as PrimeraPlanaViewer
from salud import ImageViewer as SaludViewer
from deportes import ImageViewer as DeportesViewer
from cultura import ImageViewer as CulturaViewer
from espectaculos import ImageViewer as EspectaculosViewer

#QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
#QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

def ruta_recurso(rel_path):
    """Obtiene la ruta del recurso ya sea en desarrollo o empaquetado"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Editor de Periódico Digital")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(ruta_recurso("Imagenes/icono.ico")))
        
        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Usamos GridLayout para organizar mejor los botones
        layout = QGridLayout(central_widget)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_image = QLabel()
        title_pixmap = QPixmap(ruta_recurso("Imagenes/Titulo.png"))  # Asegúrate de tener esta imagen
        if not title_pixmap.isNull():
            # Escalar la imagen manteniendo la relación de aspecto
            scaled_pixmap = title_pixmap.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)
            title_image.setPixmap(scaled_pixmap)
            title_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            # Fallback en caso de que no se encuentre la imagen
            title_image.setText("SELECCIONE LA SECCIÓN A EDITAR")
            title_image.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        layout.addWidget(title_image, 0, 0, 1, 2)  # Fila 0, columna 0, ocupa 1 fila y 2 columnas
        
        # Botones para cada tipo de periódico
        btn_primera_plana = self.create_section_button("PRIMERA PLANA", "PrimeraPlana.jpg")
        btn_primera_plana.clicked.connect(lambda: self.open_section("primera_plana"))
        layout.addWidget(btn_primera_plana, 1, 0)
        
        btn_salud = self.create_section_button("SALUD", "SaludBoton.jpg")
        btn_salud.clicked.connect(lambda: self.open_section("salud"))
        layout.addWidget(btn_salud, 1, 1)
        
        btn_deportes = self.create_section_button("DEPORTES", "DeportesBoton.jpg")
        btn_deportes.clicked.connect(lambda: self.open_section("deportes"))
        layout.addWidget(btn_deportes, 2, 0)
        
        btn_cultura = self.create_section_button("CULTURA", "CulturaBoton.jpg")
        btn_cultura.clicked.connect(lambda: self.open_section("cultura"))
        layout.addWidget(btn_cultura, 2, 1)
        
        btn_espectaculos = self.create_section_button("ESPECTÁCULOS", "EspectaculosBoton.jpg")
        btn_espectaculos.clicked.connect(lambda: self.open_section("espectaculos"))
        layout.addWidget(btn_espectaculos, 3, 0)
        
        # Botón de salir
        btn_exit = QPushButton("SALIR DEL EDITOR")
        btn_exit.setFont(QFont("Arial", 12))
        btn_exit.clicked.connect(self.close)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(btn_exit, 3, 1)
        
        # Estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
                padding: 10px;
            }
        """)
        
        # Diccionario de vistas
        self.section_windows = {
            "primera_plana": None,
            "salud": None,
            "deportes": None,
            "cultura": None,
            "espectaculos": None
        }
        
        # Diccionario de imágenes de fondo para cada sección
        self.section_backgrounds = {
            "primera_plana": ruta_recurso("backgrounds/PrimeraPlana.png"),
            "salud": ruta_recurso("backgrounds/Salud.png"),
            "deportes": ruta_recurso("backgrounds/Deportes.png"),
            "cultura": ruta_recurso("backgrounds/Cultura.png"),
            "espectaculos": ruta_recurso("backgrounds/Espectaculos.png")
        }
    
    def create_section_button(self, text, image_filename=None):
        button = QPushButton()
        button.setFixedSize(250, 90)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        if image_filename:
            # Ruta de la imagen normal
            ruta_imagen_normal = ruta_recurso(os.path.join("BotonesImg", image_filename))
            
            # Ruta de la imagen hover (asumiendo que tiene el mismo nombre pero con _hover al final)
            base_name, ext = os.path.splitext(image_filename)
            hover_filename = f"{base_name}_hover{ext}"
            ruta_imagen_hover = ruta_recurso(os.path.join("BotonesImg", hover_filename))
            
            # Verificar si existe la imagen hover
            if os.path.exists(ruta_imagen_hover.replace("\\", "/")):  # Normalizar rutas para Windows
                # Configurar estilos con QIcon para evitar problemas de parsing
                button.setIcon(QIcon(ruta_imagen_normal))
                button.setIconSize(QSize(240, 80))
                
                # Usar pseudo-estados para cambiar el icono
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 3px solid #000000;
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        border-color: #f3a7a2;
                        background-color: #f3a7a2;
                    }}
                """)
                
                # Cambiar el icono manualmente en los eventos enter/leave
                def enter_event(event):
                    button.setIcon(QIcon(ruta_imagen_hover))
                    super(type(button), button).enterEvent(event)
                    
                def leave_event(event):
                    button.setIcon(QIcon(ruta_imagen_normal))
                    super(type(button), button).leaveEvent(event)
                    
                button.enterEvent = enter_event
                button.leaveEvent = leave_event
                
            else:
                # Si no hay imagen hover, usar solo la imagen normal
                button.setIcon(QIcon(ruta_imagen_normal))
                button.setIconSize(QSize(240, 80))
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 3px solid #000000;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        border-color: #3498db;
                    }
                """)

        return button

 
    def open_section(self, section_name):
        """Abre la ventana de la sección seleccionada"""
        self.hide()  # Oculta el menú principal
        
        # Cierra la ventana anterior si existe
        if self.section_windows[section_name]:
            self.section_windows[section_name].close()
        
        # Crea la nueva ventana según la sección
        if section_name == "primera_plana":
            self.section_windows[section_name] = PrimeraPlanaViewer(self.section_backgrounds[section_name])
        elif section_name == "salud":
            self.section_windows[section_name] = SaludViewer(self.section_backgrounds[section_name])
        elif section_name == "deportes":
            self.section_windows[section_name] = DeportesViewer(self.section_backgrounds[section_name])
        elif section_name == "cultura":
            self.section_windows[section_name] = CulturaViewer(self.section_backgrounds[section_name])
        elif section_name == "espectaculos":
            self.section_windows[section_name] = EspectaculosViewer(self.section_backgrounds[section_name])
        
        # Configura la referencia al menú principal
        self.section_windows[section_name].main_window = self
        self.section_windows[section_name].showMaximized()
    
    def show(self):
        """Muestra la ventana principal"""
        super().show()
        # Cierra todas las ventanas de sección abiertas
        for section in self.section_windows.values():
            if section:
                section.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ruta_recurso("Imagenes/icono.ico")))
    # Establecer estilo visual moderno
    app.setStyle('Fusion')
    
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())