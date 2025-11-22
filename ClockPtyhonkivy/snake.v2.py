import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window # Importar para manejar el teclado
from kivy.utils import platform # Utilidad para detectar la plataforma
import random

kivy.require('1.9.0')

# Definiciones de la pantalla y el juego
GRID_SIZE = 20    # Tamaño de cada celda (20 píxeles)
GRID_WIDTH = 25   # 25 celdas * 20 px/celda = 500 px
GRID_HEIGHT = 25  # 25 celdas * 20 px/celda = 500 px
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE   # 500
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE # 500

# --------------------------------------------------------------------------
# 1. Clase del Juego (Game Screen)
# --------------------------------------------------------------------------

class SnakeGame(Widget):
    """
    Gestiona la lógica del juego, el dibujo del Snake, la comida y el teclado.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (SCREEN_WIDTH, SCREEN_HEIGHT) 
        self.bind(size=self._update_canvas) 
        self.bind(pos=self._update_canvas)
        self.reset_game()

        # ----------------------------------------------------
        # INICIALIZACIÓN DEL TECLADO
        # ----------------------------------------------------
        
        # Solicitamos el teclado virtual (funciona para desktop y mobile)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if self._keyboard.bind(on_key_down=self.on_key_down):
            pass # El teclado está listo
        
    def _keyboard_closed(self):
        """Función que se llama cuando se cierra el teclado."""
        # Necesario desvincular el evento
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None
        
    def on_key_down(self, keyboard, keycode, text, modifiers):
        """Maneja la pulsación de teclas."""
        key_name = keycode[1]
        
        # Mapeo de teclas de flecha
        if key_name == 'up' and self.direction != 'down':
            self.next_direction = 'up'
        elif key_name == 'down' and self.direction != 'up':
            self.next_direction = 'down'
        elif key_name == 'left' and self.direction != 'right':
            self.next_direction = 'left'
        elif key_name == 'right' and self.direction != 'left':
            self.next_direction = 'right'
            
        # Para el control táctil, no hace falta eliminarlo, solo se prioriza el último evento.
        return True # Indicamos que la pulsación ha sido manejada

    def _update_canvas(self, *args):
        """Redibuja el canvas."""
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1) # Gris oscuro
            Rectangle(pos=self.pos, size=self.size) 
            self.draw_elements()

    def reset_game(self):
        """Inicializa o reinicializa las variables del juego."""
        self.snake = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]] 
        self.direction = 'right'
        self.next_direction = 'right'
        self.food_pos = self.generate_food()
        self.score = 0
        self.game_over = False
        self.draw_elements()

    def generate_food(self):
        """Genera una posición aleatoria para la comida que no esté ocupada por el Snake."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if [x, y] not in self.snake:
                return [x, y]

    # Mantenemos on_touch_down y on_touch_up para que el juego siga siendo 
    # jugable en móvil (swipes) además del teclado.
    def on_touch_down(self, touch):
        """Maneja los cambios de dirección usando swipes (deslizamientos)."""
        if platform not in ('android', 'ios'):
            # Si estamos en desktop, ignoramos el toque para no interferir con el teclado
            return
        self._touch_start = touch.pos

    def on_touch_up(self, touch):
        """Calcula la dirección del swipe al soltar el toque."""
        if platform not in ('android', 'ios'):
            return
        
        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch