import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QPointF
from dataclasses import dataclass

@dataclass
class ParameterSet:
    name: str
    cmos_type: str
    focal_length: float
    distance: float
    object_height: float
    aspect_ratio: float
    color: QtGui.QColor
    rect: QtCore.QRectF = None

class CameraCalculator(QtWidgets.QWidget):
    CMOS_SIZES = {
        'APS-C': {'w': 0.0238, 'h': 0.0158},  # 23.8mm x 15.8mm
        'Full Frame': {'w': 0.0360, 'h': 0.0240},  # 36mm x 24mm
        'M43': {'w': 0.0173, 'h': 0.0130}  # 17.3mm x 13mm
    }
    
    def __init__(self):
        super().__init__()
        self.parameter_sets = []  # Store parameter sets
        # Modern, visually appealing color palette
        self.color_palette = [
            QtGui.QColor('#4285F4'),  # Google Blue
            QtGui.QColor('#EA4335'),  # Google Red
            QtGui.QColor('#FBBC05'),  # Google Yellow
            QtGui.QColor('#34A853'),  # Google Green
            QtGui.QColor('#673AB7'),  # Deep Purple
            QtGui.QColor('#FF5722'),  # Deep Orange
            QtGui.QColor('#009688'),  # Teal
            QtGui.QColor('#9C27B0'),  # Purple
            QtGui.QColor('#2196F3'),  # Blue
            QtGui.QColor('#4CAF50'),  # Green
            QtGui.QColor('#FF9800'),  # Orange
            QtGui.QColor('#E91E63')   # Pink
        ]
        self.color_index = 0
        self.current_color = QtGui.QColor(self.color_palette[0])
        self.init_ui()
        
    def showEvent(self, event):
        """Handle the window show event to perform initial drawing"""
        super().showEvent(event)
        # Schedule the initial drawing after the window is shown
        QtCore.QTimer.singleShot(100, self.initial_drawing)
        
    def initial_drawing(self):
        """Perform the initial drawing of the scene"""
        self.update_view()
        
    def update_view(self):
        """Update the view to show the sensor area with proper scaling"""
        self.view.fitInView(0, 0, 300, 250, Qt.KeepAspectRatio)
        self.view.centerOn(150, 125)
        
    def init_ui(self):
        self.setWindowTitle('Camera Field of View Calculator')
        self.setMinimumSize(800, 600)
        
        # Create input fields
        self.cmos_combo = QtWidgets.QComboBox()
        self.cmos_combo.addItems(self.CMOS_SIZES.keys())
        
        self.focal_length_input = QtWidgets.QDoubleSpinBox()
        self.focal_length_input.setRange(1, 1000)
        self.focal_length_input.setValue(50)
        self.focal_length_input.setSuffix(' mm')
        
        self.distance_input = QtWidgets.QDoubleSpinBox()
        self.distance_input.setRange(0.1, 1000)
        self.distance_input.setValue(10.0)  # Default to 10 meters
        self.distance_input.setSuffix(' m')
        
        self.object_height_input = QtWidgets.QDoubleSpinBox()
        self.object_height_input.setRange(0.01, 1000)
        self.object_height_input.setValue(0.5)  # Default to 0.5 meters
        self.object_height_input.setSuffix(' m')
        
        # Aspect ratio input (width/height)
        self.aspect_ratio_input = QtWidgets.QDoubleSpinBox()
        self.aspect_ratio_input.setRange(0.1, 10.0)
        self.aspect_ratio_input.setValue(1.0)  # Default to 1:1 aspect ratio
        self.aspect_ratio_input.setDecimals(2)
        
        # Create add button
        self.add_button = QtWidgets.QPushButton('Add')
        self.add_button.clicked.connect(self.add_parameter_set)
        
        # Create parameter list
        self.parameter_list = QtWidgets.QListWidget()
        self.parameter_list.itemSelectionChanged.connect(self.on_parameter_selected)
        
        # Create delete button
        self.delete_button = QtWidgets.QPushButton('Delete Selected')
        self.delete_button.clicked.connect(self.delete_selected_parameter)
        self.delete_button.setEnabled(False)
        
        # Create result labels
        self.result_label = QtWidgets.QLabel('')
        self.result_label.setWordWrap(True)
        
        # Create details display box
        self.details_group = QtWidgets.QGroupBox('Parameter Set Details')
        details_layout = QtWidgets.QFormLayout()
        
        # Read-only fields for parameter details
        self.detail_name = QtWidgets.QLabel()
        self.detail_cmos = QtWidgets.QLabel()
        self.detail_focal = QtWidgets.QLabel()
        self.detail_distance = QtWidgets.QLabel()
        self.detail_height = QtWidgets.QLabel()
        self.detail_aspect = QtWidgets.QLabel()
        self.detail_fov = QtWidgets.QLabel()
        self.detail_coverage = QtWidgets.QLabel()
        
        # Add to form layout
        details_layout.addRow('Name:', self.detail_name)
        details_layout.addRow('Sensor Type:', self.detail_cmos)
        details_layout.addRow('Focal Length:', self.detail_focal)
        details_layout.addRow('Object Distance:', self.detail_distance)
        details_layout.addRow('Object Height:', self.detail_height)
        details_layout.addRow('Aspect Ratio:', self.detail_aspect)
        details_layout.addRow('Field of View:', self.detail_fov)
        details_layout.addRow('Sensor Coverage:', self.detail_coverage)
        
        self.details_group.setLayout(details_layout)
        self.details_group.setMinimumWidth(300)
        self.details_group.setVisible(False)  # Hidden until a parameter set is selected
        
        # Create graphics view
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QBrush(Qt.transparent))
        
        self.view = QtWidgets.QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Make the view background transparent
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        # Layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Sensor Type:', self.cmos_combo)
        form_layout.addRow('Focal Length:', self.focal_length_input)
        form_layout.addRow('Object Distance:', self.distance_input)
        form_layout.addRow('Object Height:', self.object_height_input)
        form_layout.addRow('Aspect Ratio (w/h):', self.aspect_ratio_input)
        
        # Add color selection
        color_layout = QtWidgets.QHBoxLayout()
        self.color_button = QtWidgets.QPushButton('Select Color')
        self.color_button.clicked.connect(self.choose_color)
        self.color_preview = QtWidgets.QFrame()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(f'background-color: {self.current_color.name()}')
        color_layout.addWidget(QtWidgets.QLabel('Rectangle Color:'))
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        
        # Add name input (hidden since we're using auto-generated names)
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setVisible(False)  # Hide the name input field

        # Form layout for parameters
        form_widget = QtWidgets.QWidget()
        form_widget.setLayout(form_layout)
        
        # Scroll area for form
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(form_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        
        # Right panel layout
        right_panel = QtWidgets.QVBoxLayout()
        right_panel.addWidget(scroll)
        right_panel.addWidget(QtWidgets.QLabel('Parameter Set Name:'))
        right_panel.addWidget(self.name_edit)
        right_panel.addLayout(color_layout)
        right_panel.addWidget(self.add_button)
        right_panel.addWidget(QtWidgets.QLabel('Parameter Sets:'))
        right_panel.addWidget(self.parameter_list)
        right_panel.addWidget(self.delete_button)
        right_panel.addWidget(self.result_label)
        right_panel.addWidget(self.details_group)  # Add details group to the layout
        right_panel.addStretch()
        
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(right_panel, 1)
        main_layout.addWidget(self.view, 2)
        
        self.setLayout(main_layout)
        
        # Don't perform initial calculation here, will be done after window is shown
    
    def add_parameter_set(self):
        try:
            # Generate default name in format: format-focal_length-index (all lowercase)
            cmos_short = self.cmos_combo.currentText().lower().replace(' ', '_')
            focal_length = int(self.focal_length_input.value())
            index = len([p for p in self.parameter_sets if p.cmos_type == self.cmos_combo.currentText() and 
                        p.focal_length == focal_length]) + 1
            default_name = f"{cmos_short}-{focal_length}mm-{index}"
            
            # Get input values
            name = self.name_edit.text().strip() or default_name
            cmos_type = self.cmos_combo.currentText()
            focal_length = self.focal_length_input.value()
            distance = self.distance_input.value()
            object_height = self.object_height_input.value()
            aspect_ratio = self.aspect_ratio_input.value()
            
            # Get next color from palette
            color = self.get_next_color()
            self.current_color = color  # Update current color for preview
            self.color_preview.setStyleSheet(f'background-color: {color.name()}')
            
            # Create new parameter set
            param_set = ParameterSet(
                name=name,
                cmos_type=cmos_type,
                focal_length=focal_length,
                distance=distance,
                object_height=object_height,
                aspect_ratio=aspect_ratio,
                color=color
            )
            
            # Calculate and store rectangle
            self.calculate_rectangle(param_set)
            
            # Add to list
            self.parameter_sets.append(param_set)
            
            # Update UI
            self.update_parameter_list()
            self.update_visualization()
            
            # Auto-select the new item
            self.parameter_list.setCurrentRow(len(self.parameter_sets) - 1)
            
        except Exception as e:
            self.result_label.setText(f'Error: {str(e)}')
    
    def calculate_rectangle(self, param_set):
        try:
            cmos_w = self.CMOS_SIZES[param_set.cmos_type]['w']
            cmos_h = self.CMOS_SIZES[param_set.cmos_type]['h']
            f = param_set.focal_length / 1000  # Convert to meters
            u = param_set.distance
            h_o = param_set.object_height
            
            # Calculate image height
            h_i = self.calc_h_i(f, u, h_o)
            h_prop = h_i / cmos_w
            
            # Calculate field of view
            fov_h = 2 * (cmos_w / (2 * f)) * u
            fov_v = 2 * (cmos_h / (2 * f)) * u
            
            # Calculate rectangle dimensions
            img_w = 200 * min(h_prop, 1.0)
            img_h = img_w / param_set.aspect_ratio
            
            # If height exceeds sensor height, scale down to fit
            if img_h > 200 * 2/3:
                img_h = 200 * 2/3
                img_w = img_h * param_set.aspect_ratio
            
            # Center the rectangle in the sensor
            img_x = 50 + (200 - img_w) / 2
            img_y = 50 + (200 * 2/3 - img_h) / 2
            
            # Store the rectangle
            param_set.rect = QtCore.QRectF(img_x, img_y, img_w, img_h)
            
        except Exception as e:
            self.result_label.setText(f'Error calculating rectangle: {str(e)}')
    
    def calc_h_i(self, f, u, h_o):
        """Calculate image height on sensor"""
        return (h_o * f) / (u - f)
    
    def get_next_color(self):
        """Get the next color from the palette and update the index"""
        color = self.color_palette[self.color_index % len(self.color_palette)]
        self.color_index += 1
        return QtGui.QColor(color)
        
    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor(self.current_color, self, 'Select Rectangle Color')
        if color.isValid():
            self.current_color = color
            self.color_preview.setStyleSheet(f'background-color: {color.name()}')

    def update_parameter_list(self):
        self.parameter_list.clear()
        for i, param_set in enumerate(self.parameter_sets):
            item = QtWidgets.QListWidgetItem(param_set.name)
            item.setForeground(param_set.color)
            self.parameter_list.addItem(item)
    
    def on_parameter_selected(self):
        selected = self.parameter_list.currentRow()
        self.delete_button.setEnabled(selected >= 0)
        
        if 0 <= selected < len(self.parameter_sets):
            param_set = self.parameter_sets[selected]
            self.update_parameter_details(param_set)
            self.details_group.setVisible(True)
        else:
            self.details_group.setVisible(False)
    
    def delete_selected_parameter(self):
        selected = self.parameter_list.currentRow()
        if 0 <= selected < len(self.parameter_sets):
            self.parameter_sets.pop(selected)
            self.details_group.setVisible(False)  # Hide details when parameter is deleted
            
            # Update the parameter list and visualization
            self.update_parameter_list()
            self.update_visualization()
            
            # Disable delete button if no items left
            if not self.parameter_sets:
                self.delete_button.setEnabled(False)

    def mouse_press_event(self, event):
        # No longer needed - just pass the event to the parent
        super().mousePressEvent(event)

    def mouse_move_event(self, event):
        # No longer needed - just pass the event to the parent
        super().mouseMoveEvent(event)

    def mouse_release_event(self, event):
        # No longer needed - just pass the event to the parent
        super().mouseReleaseEvent(event)
        
    def calculate_fov(self, focal_length, sensor_size, distance):
        """Calculate field of view in degrees"""
        import math
        fov_rad = 2 * math.atan(sensor_size / (2 * focal_length))
        return math.degrees(fov_rad)
        
    def calculate_sensor_coverage(self, param_set):
        """Calculate what percentage of the sensor is covered by the object"""
        if not param_set.rect:
            return 0.0
        sensor_area = 200 * (200 * 2/3)  # Total sensor area in pixels
        rect_area = param_set.rect.width() * param_set.rect.height()
        return min(100.0, (rect_area / sensor_area) * 100)
        
    def update_parameter_details(self, param_set):
        """Update the details display with parameter set information"""
        # Get sensor dimensions
        sensor_w = self.CMOS_SIZES[param_set.cmos_type]['w'] * 1000  # Convert to mm
        sensor_h = self.CMOS_SIZES[param_set.cmos_type]['h'] * 1000  # Convert to mm
        
        # Calculate FOV
        fov_h = self.calculate_fov(param_set.focal_length, sensor_w, param_set.distance)
        fov_v = self.calculate_fov(param_set.focal_length, sensor_h, param_set.distance)
        
        # Update labels
        self.detail_name.setText(param_set.name)
        self.detail_cmos.setText(f"{param_set.cmos_type} ({sensor_w:.1f}mm x {sensor_h:.1f}mm)")
        self.detail_focal.setText(f"{param_set.focal_length:.1f} mm")
        self.detail_distance.setText(f"{param_set.distance:.2f} m")
        self.detail_height.setText(f"{param_set.object_height:.2f} m")
        self.detail_aspect.setText(f"{param_set.aspect_ratio:.2f}")
        self.detail_fov.setText(f"H: {fov_h:.1f}°  V: {fov_v:.1f}°")
        
        # Calculate and display sensor coverage
        coverage = self.calculate_sensor_coverage(param_set)
        self.detail_coverage.setText(f"{coverage:.1f}% of sensor area")
    
    def update_visualization(self):
        self.scene.clear()
        
        # Store current view transformation
        old_transform = self.view.transform() if hasattr(self, 'view') else None
        
        # Draw sensor frame (2:3 aspect ratio)
        sensor_rect = QtCore.QRectF(0, 0, 200, 200 * 2/3)
        sensor = self.scene.addRect(sensor_rect, 
                                  QtGui.QPen(Qt.black, 1, Qt.DashLine), 
                                  QtGui.QBrush(Qt.NoBrush))
        sensor.setPos(50, 50)
        
        # Draw all parameter set rectangles
        for param_set in self.parameter_sets:
            if param_set.rect:
                # Draw rectangle with medium border and no rounded corners
                color = param_set.color
                pen = QtGui.QPen(color, 1.5)  # Slightly thicker border (1.5px)
                pen.setCosmetic(True)  # Makes the border width consistent regardless of zoom
                pen.setJoinStyle(Qt.MiterJoin)  # Sharp corners
                
                # Add rectangle to scene with no fill and medium border
                rect_item = self.scene.addRect(param_set.rect, pen, QtGui.QBrush(Qt.NoBrush))
        
        # Add sensor label at the top-left corner
        sensor_label = self.scene.addText('Sensor Area', QtGui.QFont('Arial', 8))
        sensor_label.setPos(50, 50)  # Top-left of sensor
        
        # Set scene rect to ensure sensor area is always visible
        sensor_rect = QtCore.QRectF(0, 0, 300, 250)  # Slightly larger than the sensor area
        self.scene.setSceneRect(sensor_rect)
        
        # Restore view transformation if it exists
        if old_transform:
            self.view.setTransform(old_transform)
        else:
            # Fit the view to show the sensor area with some padding
            self.view.fitInView(0, 0, 300, 250, Qt.KeepAspectRatio)
            self.view.centerOn(150, 125)  # Center on the sensor area
        for param_set in self.parameter_sets:
            if param_set.rect:
                # Draw rectangle with medium border and no rounded corners
                color = param_set.color
                pen = QtGui.QPen(color, 1.5)  # Slightly thicker border (1.5px)
                pen.setCosmetic(True)  # Makes the border width consistent regardless of zoom
                pen.setJoinStyle(Qt.MiterJoin)  # Sharp corners
                
                # Add rectangle to scene with no fill and medium border
                rect_item = self.scene.addRect(param_set.rect, pen, QtGui.QBrush(Qt.NoBrush))
        
        # Add sensor label at the top-left corner
        sensor_label = self.scene.addText('Sensor Area', QtGui.QFont('Arial', 8))
        sensor_label.setPos(50, 50)  # Top-left of sensor
        
        # Set scene rect to ensure sensor area is always visible
        sensor_rect = QtCore.QRectF(0, 0, 300, 250)  # Slightly larger than the sensor area
        self.scene.setSceneRect(sensor_rect)
        
        # Restore view transformation if it exists
        if old_transform:
            self.view.setTransform(old_transform)
        else:
            # Fit the view to show the sensor area with some padding
            self.view.fitInView(0, 0, 300, 250, Qt.KeepAspectRatio)
            self.view.centerOn(150, 125)  # Center on the sensor area

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    calculator = CameraCalculator()
    calculator.show()
    
    sys.exit(app.exec())