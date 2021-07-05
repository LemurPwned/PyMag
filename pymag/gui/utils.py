from PyQt5.QtWidgets import QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox
from typing import Any, Dict

unicode_subs = {
    "theta": "\u03B8",
    "phi": "\u03C6",
    "lam": "\u03BB",
    "beta": "\u03B2",
    "eng": "\u014B",
    "zeta_fl": "\u03B6 FL",
    "zeta_dl": "\u03B6 DL",
    "h_fl": "H FL",
    "h_dl": "H DL"
}
inverse_subs = {v: k for k, v in unicode_subs.items()}


class Labelled():
    def __init__(self,
                 var_name,
                 label="Label",
                 minimum=0,
                 maximum=1,
                 value=0,
                 mode='Double',
                 item_list=["1", "2", "3"]):
        self.var_name = var_name
        self.Label = QLabel(label)
        self.mode = mode
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
        if mode == 'Combo':
            self.Value = QComboBox()
            self.Value.setObjectName(label)
            for i in range(0, len(item_list)):
                self.Value.addItem(item_list[i])

    def setValue(self, value: Any):
        if self.mode == "Binary":
            self.Value.setChecked(value)
        elif self.mode == "Combo":
            self.Value.setCurrentIndex(value)
        else:
            self.Value.setValue(value)

    def show(self):
        self.Value.show()
        self.Label.show()

    def hide(self):
        self.Value.hide()
        self.Label.hide()

    def to_json(self) -> Dict[str, Any]:
        ret = {
            "label": self.Label.text(),
            "mode": self.mode
        }
        if self.mode == 'Double' or self.mode == 'Integer':
            add = {
                "maximum": self.Value.maximum(),
                "minimum": self.Value.minimum(),
                "value": self.Value.value(),
            }
        elif self.mode == "Binary":
            add = {
                "value": self.Value.checkState()
            }
        else:
            add = {
                "item_list": [self.Value.itemText(i) for i in range(self.Value.count())],
                "value": self.Value.currentIndex()
            }
        return {"name": self.var_name,
                "params": {**ret, **add}}
