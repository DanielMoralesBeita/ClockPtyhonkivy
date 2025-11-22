import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
import random

kivy.require('1.9.0')

# Definiciones de la pantalla y el juego
GRID_SIZE = 20 # Tamaño de cada celda (en píxeles)
GRID_WIDTH = 40 # Número de celdas a lo ancho
GRID_HEIGHT = 40 # Número de celdas a lo alto
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

# --------------------------------------------------------------------------
# 1. Clase del Juego (Game Screen)
# --------------------------------------------------------------------------

class SnakeGame(Widget):
    """
    Gestiona la lógica del juego, el dibujo del Snake y la comida.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_canvas) # Asegura que el canvas se actualice con el tamaño del widget
        self.bind(pos=self._update_canvas)
        self.reset_game()
        
    def _update_canvas(self, *args):
        """Redibuja el canvas."""
        self.canvas.clear()
        with self.canvas:
            # Dibuja el fondo del área de juego
            Color(0.2, 0.2, 0.2, 1) # Gris oscuro
            Rectangle(pos=self.pos, size=self.size) 
            self.draw_elements()

    def reset_game(self):
        """Inicializa o reinicializa las variables del juego."""
        # Snake: lista de coordenadas [x, y]
        self.snake = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]] 
        self.direction = 'right'
        self.next_direction = 'right' # Permite guardar la siguiente dirección para evitar giros de 180°
        self.food_pos = self.generate_food()
        self.score = 0
        self.game_over = False
        self.draw_elements() # Dibuja los elementos iniciales

    def generate_food(self):
        """Genera una posición aleatoria para la comida que no esté ocupada por el Snake."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if [x, y] not in self.snake:
                return [x, y]

    def on_touch_down(self, touch):
        """Maneja los cambios de dirección usando swipes (deslizamientos)."""
        # Se guarda la posición inicial del toque para calcular el swipe
        self._touch_start = touch.pos

    def on_touch_up(self, touch):
        """Calcula la dirección del swipe al soltar el toque."""
        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch_start[1]
        
        # Determina si el movimiento fue horizontal o vertical
        if abs(dx) > abs(dy):
            # Movimiento horizontal
            if dx > GRID_SIZE and self.direction != 'left':
                self.next_direction = 'right'
            elif dx < -GRID_SIZE and self.direction != 'right':
                self.next_direction = 'left'
        else:
            # Movimiento vertical
            if dy > GRID_SIZE and self.direction != 'down':
                self.next_direction = 'up'
            elif dy < -GRID_SIZE and self.direction != 'up':
                self.next_direction = 'down'

    def update(self, dt):
        """Función principal del juego, llamada repetidamente por Clock."""
        if self.game_over:
            return

        # Aplica la dirección deseada
        self.direction = self.next_direction
        
        head_x, head_y = self.snake[0]
        
        # Calcula la nueva posición de la cabeza
        new_head = list(self.snake[0])
        if self.direction == 'right':
            new_head[0] += 1
        elif self.direction == 'left':
            new_head[0] -= 1
        elif self.direction == 'up':
            new_head[1] += 1
        elif self.direction == 'down':
            new_head[1] -= 1

        # Comprobación de colisiones:
        
        # 1. Colisión contra sí mismo
        if new_head in self.snake:
            self.end_game()
            return
            
        # 2. Colisión contra bordes
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.end_game()
            return

        # Mueve el snake: añade la nueva cabeza
        self.snake.insert(0, new_head)

        # 3. Colisión con la comida
        if new_head == self.food_pos:
            self.score += 1
            self.food_pos = self.generate_food()
            self.parent.update_score(self.score) # Llama a la función de la pantalla principal
        else:
            # Si no come, elimina la cola (movimiento normal)
            self.snake.pop()

        # Redibuja
        self.draw_elements()

    def draw_elements(self):
        """Dibuja el Snake y la Comida en el canvas."""
        self.canvas.clear()
        
        with self.canvas:
            # Dibuja el fondo del área de juego
            Color(0.2, 0.2, 0.2, 1) 
            Rectangle(pos=self.pos, size=self.size)
            
            # Dibujar el Snake
            Color(0, 0.8, 0, 1) # Color verde
            for segment in self.snake:
                x = self.pos[0] + segment[0] * GRID_SIZE
                y = self.pos[1] + segment[1] * GRID_SIZE
                Rectangle(pos=(x, y), size=(GRID_SIZE, GRID_SIZE))

            # Dibujar la Comida (Manzana)
            Color(1, 0, 0, 1) # Color rojo
            food_x = self.pos[0] + self.food_pos[0] * GRID_SIZE
            food_y = self.pos[1] + self.food_pos[1] * GRID_SIZE
            # Usamos Ellipse para darle forma de círculo/manzana
            Ellipse(pos=(food_x, food_y), size=(GRID_SIZE, GRID_SIZE))

    def end_game(self):
        """Termina el juego y muestra la pantalla de fin de juego."""
        self.game_over = True
        # Detiene el bucle de actualización
        Clock.unschedule(self._event) 
        # Llama al método del ScreenManager para ir a la pantalla de Game Over
        self.parent.parent.parent.show_game_over(self.score)

# --------------------------------------------------------------------------
# 2. Clases de Pantalla (ScreenManager)
# --------------------------------------------------------------------------

class StartScreen(Screen):
    """Pantalla de bienvenida y menú de inicio."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        # Título
        title_label = Label(text='🐍 SNAKE KIVY 🐍', font_size='60sp', size_hint_y=0.4)
        
        # Botón de Inicio
        start_button = Button(text='Iniciar Juego', font_size='40sp', size_hint_y=0.3)
        start_button.bind(on_release=self.start_game)
        
        # Créditos / Instrucciones
        info_label = Label(text='Instrucciones: Desliza el dedo (swipe) para cambiar de dirección.', font_size='20sp', size_hint_y=0.3)
        
        layout.add_widget(title_label)
        layout.add_widget(start_button)
        layout.add_widget(info_label)
        
        self.add_widget(layout)

    def start_game(self, instance):
        """Cambia a la pantalla de juego."""
        self.manager.current = 'game'

class GameScreen(Screen):
    """Pantalla que contiene el juego y la puntuación."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal (vertical): Controles de info + Área de juego
        self.main_layout = BoxLayout(orientation='vertical')
        
        # 1. Barra de Puntuación
        self.score_label = Label(text='Puntos: 0', size_hint_y=0.1, font_size='30sp')
        self.main_layout.add_widget(self.score_label)
        
        # 2. Área de Juego (SnakeGame)
        self.game_widget = SnakeGame(size_hint_y=0.9)
        self.main_layout.add_widget(self.game_widget)
        
        self.add_widget(self.main_layout)
    
    def on_enter(self, *args):
        """Se llama cuando la pantalla se vuelve visible (al iniciar el juego)."""
        self.game_widget.reset_game()
        self.update_score(0)
        # Inicia el bucle del juego (10 FPS)
        self.game_widget._event = Clock.schedule_interval(self.game_widget.update, 1.0 / 10.0) 

    def update_score(self, score):
        """Actualiza el texto de la puntuación."""
        self.score_label.text = f'Puntos: {score}'

class GameOverScreen(Screen):
    """Pantalla que se muestra al perder."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        self.message_label = Label(text='¡Juego Terminado!', font_size='60sp', size_hint_y=0.4)
        self.final_score_label = Label(text='Puntuación Final: 0', font_size='40sp', size_hint_y=0.3)
        
        # Botón para volver al menú
        restart_button = Button(text='Volver al Menú', font_size='40sp', size_hint_y=0.3)
        restart_button.bind(on_release=self.go_to_start)
        
        self.layout.add_widget(self.message_label)
        self.layout.add_widget(self.final_score_label)
        self.layout.add_widget(restart_button)
        self.add_widget(self.layout)

    def update_score_display(self, score):
        """Actualiza la puntuación final antes de mostrar la pantalla."""
        self.final_score_label.text = f'Puntuación Final: {score}'

    def go_to_start(self, instance):
        """Vuelve a la pantalla de inicio."""
        self.manager.current = 'start'

# --------------------------------------------------------------------------
# 3. Clase Principal de la Aplicación (App)
# --------------------------------------------------------------------------

class SnakeGameApp(App):
    """
    Clase principal que construye el ScreenManager para gestionar las pantallas.
    """
    def build(self):
        # Establece el tamaño de la ventana para que coincida con la grilla
        self.title = 'Kivy Snake Game'
        
        # Creamos el gestor de pantallas
        sm = ScreenManager()
        
        # Creamos las pantallas
        start_screen = StartScreen(name='start')
        game_screen = GameScreen(name='game')
        game_over_screen = GameOverScreen(name='game_over')
        
        # Las añadimos al gestor
        sm.add_widget(start_screen)
        sm.add_widget(game_screen)
        sm.add_widget(game_over_screen)
        
        # Guardamos referencias para la transición Game Over
        self.game_over_screen = game_over_screen
        
        # Pantalla inicial
        sm.current = 'start'
        
        # Devuelve el gestor de pantallas
        return sm
        
    def show_game_over(self, score):
        """Función llamada desde el SnakeGame para finalizar el juego."""
        self.game_over_screen.update_score_display(score)
        self.root.current = 'game_over'

if __name__ == '__main__':
    print("Me voy a enfocar solo en lo que está en mi Círculo de Control y voy a ignorar el resto")
    print("yo lo merezco soy un imán de oportunidades y las bendiciones de Dios se proyectan de forma directa.")
    SnakeGameApp().run()

