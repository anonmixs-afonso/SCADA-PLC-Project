from client import Clientinit
from creategraph import TempGraphApp
import threading
import time
import io
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.lang.builder import Builder 
from mainwidget import MainWidget
import popups
from mainwidget import MainWidget
import mainwidget
import client
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import numpy as np
from db import Base, engine, Session
from models import DadoCLP
from threading import Lock
from time import sleep
import json
from datetime import datetime
from creategraph import TempGraphApp


class MyWidget(MainWidget):
    def __init__(self, **kwargs):
        super().__init__()
        self.modclient = ModbusClient(host=self._serverIP, port=self._serverPort)

class RectangleWidget(FloatLayout):
    pass

class MainApp(App):
    def build(self):
        """
        Método para construção do aplicativo com base no widget criado
        """
        Window.size = (Window.width, Window.height)
        super().__init__()
        self._widget = MainWidget(
            scan_time = 1000,server_ip ='localhost',server_port=1502,modbus_addrs={
            #scan_time = 1000,server_ip ='10.15.30.183',server_port=502,modbus_addrs={
            'tipomotor': 708,
            'statuspid': 722,
            'temperaturasa': 710,
            'vazaosa': 714,
            'tensaors': 847,
            'tensaost': 848,
            'tensaotr': 849,
            'tipopartida': 1216,
            'partidainversor': 1312,
            'velocidadeinversor': 1313,
            'rampaaceleracaoinversor': 1314,
            'rampadesaceleracaoinversor': 1315,
            'partidasoft': 1316,
            'rampaaceleracaosoft': 1317,
            'rampadesaceleracaosoft': 1318,
            'partidadireta': 1319,
            'tipopartida': 1324,
            'tipopid': 1332,
            'temperaturatit02': 1218,
            'temperaturatit01': 1220,
            'temperaturatermostato': 1338,
            'vazaopid': 1302,
            'pressaopit02': 1222, 
            'pressaopit01': 1224, 
            'pressaopit03': 1226,
            }
            )
        return MyWidget()

    def on_stop(self):
        self._widget.stopRefresh()

def runrealTimeGraph():
    TempGraphApp(data=data).run()


if __name__ == '__main__':
    Builder.load_string(open("/home/anon/Documents/Gits/GitInf_Gitkraken/SCADA-PLC-Project/software_SCADA/Client/mainwidget.kv",encoding="utf-8").read(),rulesonly ="True")
    Builder.load_string(open("/home/anon/Documents/Gits/GitInf_Gitkraken/SCADA-PLC-Project/software_SCADA/Client/popups.kv",encoding="utf-8").read(),rulesonly ="True")
    MainApp().run()
