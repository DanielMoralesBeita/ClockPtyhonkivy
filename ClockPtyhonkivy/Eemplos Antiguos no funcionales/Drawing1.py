import kivy   
from kivy.app import App  
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Line, Color 

kivy.require('1.9.0')  

class DrawingApp(App):
    """
    Clase principal de la aplicación que contiene la lógica para 
    crear el lienzo de dibujo y manejar los eventos táctiles.
    """
    
    def build(self):
        
        # Clase interna que funciona como el lienzo de dibujo. 
        # Hereda de RelativeLayout para manejar los eventos táctiles 
        # y usar su canvas para dibujar.
        class DrawingCanvas(RelativeLayout):
            
            def on_touch_down(self, touch):
                # Comprueba si el toque está dentro de este widget
                if self.collide_point(*touch.pos):
                    # 1. Inicia un nuevo dibujo en el Canvas
                    with self.canvas:
                        # Define el color de la línea (verde en este caso)
                        Color(0, 1, 0, 1) 
                        
                        # 2. Crea un objeto Line. Lo guardamos en 'touch.ud' 
                        # para que on_touch_move pueda referenciarlo.
                        touch.ud['line'] = Line(points=(touch.x, touch.y), width=3)
                        
                    return True # Indica que el evento fue manejado
                return super(DrawingCanvas, self).on_touch_down(touch)
                
            def on_touch_move(self, touch):
                # Solo si el toque fue iniciado en este widget (tiene la 'line' guardada)
                if 'line' in touch.ud:
                    # 3. Añade el nuevo punto a la línea que se está dibujando
                    touch.ud['line'].points += [touch.x, touch.y]
                    return True
                return super(DrawingCanvas, self).on_touch_move(touch)
                
            # No se necesita on_touch_up para este ejemplo simple, 
            # ya que la línea permanece visible automáticamente.
        
        # Retorna la instancia del lienzo de dibujo
        return DrawingCanvas()

if __name__ == '__main__':
    # Mensaje de información personal guardada
    print("Me voy a enfocar solo en lo que está en mi Círculo de Control y voy a ignorar el resto")
    print("yo lo merezco soy un imán de oportunidades y las bendiciones de Dios se proyectan de forma directa.")
    
    # Ejecuta la aplicación
    DrawingApp().run()