from PyQt5.QtWidgets import QLabel, QSpinBox, QDoubleSpinBox, QCheckBox


class LabelledDoubleSpinBox():
    def __init__(self,
                 label="Label",
                 minimum=0,
                 maximum=1,
                 value=0,
                 mode='Double'):
        self.Label = QLabel(label)
        if mode == 'Double':
            self.Value = QDoubleSpinBox()
            self.Value.setMinimum(minimum)
            self.Value.setMaximum(maximum)
            self.Value.setValue(value)
            self.Value.setObjectName(label)
        elif mode == 'Integer':
            self.Value = QSpinBox()
            self.Value.setMinimum(minimum)
            self.Value.setMaximum(maximum)
            self.Value.setValue(value)
            self.Value.setObjectName(label)

        if mode == 'Binary':
            self.Value = QCheckBox()
            self.Value.setObjectName(label)
            self.Value.setChecked(value)