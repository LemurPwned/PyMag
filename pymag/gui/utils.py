from PyQt5.QtWidgets import QLabel, QSpinBox, QDoubleSpinBox, QCheckBox

unicode_subs = {
    "theta": "\u03B8",
    "phi": "\u03C6",
    "lam": "\u03BB",
    "beta": "\u03B2",
    "eng": "\u014B",
    "zeta_fl": "\u03B6 FL",
    "zeta_dl": "\u03B6 DL"
}
inverse_subs = {v: k for k, v in unicode_subs.items()}


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