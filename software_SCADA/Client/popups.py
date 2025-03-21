from kivy.uix.popup import Popup
from kivy.uix.label import Label 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from datetime import datetime
from models import DadoCLP
from threading import Lock
from db import Base, engine, Session
from tabulate import tabulate
import matplotlib.pyplot as plt

class TimeSeriesGraph(Widget):
    # Define any properties or methods specific to TimeSeriesGraph here
    pass

class ModbusPopup(Popup):
    '''
    Popup da configuração do protocolo MODBUS
    '''
    _info_lb = None
    def __init__(self,server_ip,server_port,**kwargs):
        '''
        Construtor da classe ScanPopup
        '''
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(server_port)

    def setInfo(self,message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)

    def clearInfo(self,message):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)

class MotorPopup(Popup):
    '''
    Popup da configuração do protocolo MODBUS
    '''
    def __init__(self,inv,vel,rampaace,rampades,partida,**kwargs):
        '''
        Construtor da classe ScanPopup
        '''
        super().__init__(**kwargs)
        self.ids.inv.text = str(inv)
        self.ids.vel.text = str(vel)
        self.ids.rampaace.text = str(rampaace)
        self.ids.rampades.text = str(rampades)
        self.ids.partida.text = str(partida)


class ScanPopup(Popup):
    '''
    Popup da configuração do tempo de varredura
    '''
    def __init__(self,scantime,**kwargs):
        '''
        Construtor da classe ScanPopup
        '''
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)



class grafPopup(Popup):
    '''
    Popup da exibição dos gráficos em tempo real
    '''
    def __init__(self,**kwargs):
        '''
        Construtor da classe ScanPopup
        '''
        self._session = Session()
        Base.metadata.create_all(engine)
        self._lock = Lock()
        super().__init__(**kwargs)
        #self.ids.txt_st.text = str(scantime)
        
    def showHistGraph(self, init, final, variavel):
        self.ids.init = str(init)
        self.ids.final = str(final)
        self.ids.variavel = variavel
        a = self.ids.variavel  # Nome da variável digitada no campo
        init = datetime.strptime(init, '%d/%m/%Y %H:%M:%S')
        final = datetime.strptime(final, '%d/%m/%Y %H:%M:%S')

        # Bloqueia o acesso ao banco de dados e realiza a consulta
        self._lock.acquire()
        results = self._session.query(DadoCLP).filter(DadoCLP.timestamp.between(init, final)).all()
        self._lock.release()

        # Extrai os timestamps e os valores da variável digitada
        timestamps = [reg.timestamp for reg in results]
        try:
            values = [getattr(reg, a) for reg in results]  # Usa getattr para acessar dinamicamente o atributo
        except AttributeError:
            print(f"Erro: A variável '{a}' não existe nos registros.")
            return

        # Plota os dados
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, values, marker='o', linestyle='-', color='b')
        plt.title(f'Historical Data for {a}')
        plt.xlabel('Timestamp')
        plt.ylabel(a)  # Nome da variável como rótulo do eixo Y
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


class HistGraphPopup(Popup):
    def __init__(self,**kwargs):
        super().__init__()
        for key, value in kwargs.get('tags').items():
            cb = LabeledCheckBoxHistGraph()
            cb.ids.label.text = key
            cb.id = key
            self.ids.sensores.add_widget(cb)



class LabeledCheckBoxHistGraph(BoxLayout):
    pass

class MotorConfigPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)