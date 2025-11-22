import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window 
from kivy.utils import platform 
import random

kivy.require('1.9.0')

# Definiciones de la pantalla y el juego
GRID_SIZE = 20    
GRID_WIDTH = 25   
GRID_HEIGHT = 25  
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

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
        # LLAMADA A LA FUNCIÓN DE INICIALIZACIÓN DEL TECLADO
        # ----------------------------------------------------
        self._init_keyboard() # <--- La función que inicializa el teclado
        
    def _init_keyboard(self):
        """
        Función para solicitar el teclado virtual y vincular el manejador de eventos.
        """
        # Solicitamos el teclado virtual 
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        
        # Vinculamos la función on_key_down al evento de pulsación de tecla
        if self._keyboard.bind(on_key_down=self.on_key_down):
            pass # El teclado está listo
        
    def _keyboard_closed(self):
        """Función que se llama cuando se cierra el teclado."""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None
        
    def on_key_down(self, keyboard, keycode, text, modifiers):
        """Maneja la pulsación de teclas (Flechas)."""
        key_name = keycode[1]
        
        # Mapeo de teclas de flecha y lógica para evitar giros de 180 grados
        if key_name == 'up' and self.direction != 'down':
            self.next_direction = 'up'
        elif key_name == 'down' and self.direction != 'up':
            self.next_direction = 'down'
        elif key_name == 'left' and self.direction != 'right':
            self.next_direction = 'left'
        elif key_name == 'right' and self.direction != 'left':
            self.next_direction = 'right'
            
        return True 

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1) 
            Rectangle(pos=self.pos, size=self.size) 
            self.draw_elements()

    def reset_game(self):
        self.snake = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]] 
        self.direction = 'right'
        self.next_direction = 'right'
        self.food_pos = self.generate_food()
        self.score = 0
        self.game_over = False
        self.draw_elements()

    def generate_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if [x, y] not in self.snake:
                return [x, y]

    # El manejo táctil sigue aquí, solo para dispositivos que no usan teclado
    def on_touch_down(self, touch):
        if platform not in ('android', 'ios'): return
        self._touch_start = touch.pos

    def on_touch_up(self, touch):
        if platform not in ('android', 'ios'): return
        
        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch_start[1]
        
        if abs(dx) > abs(dy):
            if dx > GRID_SIZE and self.direction != 'left':
                self.next_direction = 'right'
            elif dx < -GRID_SIZE and self.direction != 'right':
                self.next_direction = 'left'
        else:
            if dy > GRID_SIZE and self.direction != 'down':
                self.next_direction = 'up'
            elif dy < -GRID_SIZE and self.direction != 'up':
                self.next_direction = 'down'

    def update(self, dt):
        if self.game_over: return

        self.direction = self.next_direction
        
        new_head = list(self.snake[0])
        if self.direction == 'right': new_head[0] += 1
        elif self.direction == 'left': new_head[0] -= 1
        elif self.direction == 'up': new_head[1] += 1
        elif self.direction == 'down': new_head[1] -= 1

        if new_head in self.snake or \
           not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food_pos:
            self.score += 1
            self.food_pos = self.generate_food()
            self.parent.update_score(self.score)
        else:
            self.snake.pop()

        self.draw_elements()

    def draw_elements(self):
        self.canvas.clear()
        
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1) 
            Rectangle(pos=self.pos, size=self.size)
            
            Color(0, 0.8, 0, 1) 
            for segment in self.snake:
                x = self.pos[0] + segment[0] * GRID_SIZE
                y = self.pos[1] + segment[1] * GRID_SIZE
                Rectangle(pos=(x, y), size=(GRID_SIZE, GRID_SIZE))

            Color(1, 0, 0, 1) 
            food_x = self.pos[0] + self.food_pos[0] * GRID_SIZE
            food_y = self.pos[1] + self.food_pos[1] * GRID_SIZE
            Ellipse(pos=(food_x, food_y), size=(GRID_SIZE, GRID_SIZE))

    def end_game(self):
        self.game_over = True
        Clock.unschedule(self._event) 
        self.parent.parent.parent.show_game_over(self.score)

# --------------------------------------------------------------------------
# 2. Clases de Pantalla (ScreenManager)
# --------------------------------------------------------------------------

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        title_label = Label(text='?? SNAKE KIVY ??', font_size='60sp', size_hint_y=0.4)
        start_button = Button(text='Iniciar Juego', font_size='40sp', size_hint_y=0.3)
        start_button.bind(on_release=self.start_game)
        
        info_text = (
            f'Tamaño del Lienzo: {SCREEN_WIDTH}x{SCREEN_HEIGHT}\n'
            'Controles:\n'
            '• Escritorio: Use las **teclas de flecha**.\n'
            '• Móvil: Use **gestos de deslizamiento (swipe)**.'
        )
        info_label = Label(text=info_text, font_size='20sp', size_hint_y=0.3)
        
        layout.add_widget(title_label)
        layout.add_widget(start_button)
        layout.add_widget(info_label)
        
        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.main_layout = BoxLayout(orientation='vertical', padding=[0, 0, 0, 20])
        
        self.score_label = Label(text='Puntos: 0', size_hint_y=0.1, font_size='30sp')
        self.main_layout.add_widget(self.score_label)
        
        self.game_container = Widget(size_hint=(None, None), size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_widget = SnakeGame()
        self.game_container.add_widget(self.game_widget)
        self.main_layout.add_widget(self.game_container)
        
        self.add_widget(self.main_layout)
    
    def on_enter(self, *args):
        # Aquí se inicia el juego y la lógica del reloj
        self.game_widget.reset_game()
        self.update_score(0)
        self.game_widget._event = Clock.schedule_interval(self.game_widget.update, 1.0 / 10.0) 

    def update_score(self, score):
        self.score_label.text = f'Puntos: {score}'

class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        self.message_label = Label(text='¡Juego Terminado!', font_size='60sp', size_hint_y=0.4)
        self.final_score_label = Label(text='Puntuación Final: 0', font_size='40sp', size_hint_y=0.3)
        
        restart_button = Button(text='Volver al Menú', font_size='40sp', size_hint_y=0.3)
        restart_button.bind(on_release=self.go_to_start)
        
        self.layout.add_widget(self.message_label)
        self.layout.add_widget(self.final_score_label)
        self.layout.add_widget(restart_button)
        self.add_widget(self.layout)

    def update_score_display(self, score):
        self.final_score_label.text = f'Puntuación Final: {score}'

    def go_to_start(self, instance):
        self.manager.current = 'start'

# --------------------------------------------------------------------------
# 3. Clase Principal de la Aplicación (App)
# --------------------------------------------------------------------------

class SnakeGameApp(App):
    def build(self):
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT + 50) 
        self.title = 'Kivy Snake Game'
        
        sm = ScreenManager()
        
        start_screen = StartScreen(name='start')
        game_screen = GameScreen(name='game')
        game_over_screen = GameOverScreen(name='game_over')
        
        sm.add_widget(start_screen)
        sm.add_widget(game_screen)
        sm.add_widget(game_over_screen)
        
        self.game_over_screen = game_over_screen
        
        sm.current = 'start'
        
        return sm
        
    def show_game_over(self, score):
        self.game_over_screen.update_score_display(score)
        self.root.current = 'game_over'

if __name__ == '__main__':
    # Mensajes de información guardada
    print("Me voy a enfocar solo en lo que está en mi Círculo de Control y voy a ignorar el resto")
    print("yo lo merezco soy un imán de oportunidades y las bendiciones de Dios se proyectan de forma directa.")
    SnakeGameApp().run()

